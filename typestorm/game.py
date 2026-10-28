"""Game logic, input handling and the main loop. Drawing lives in renderer.py."""

import math
import random
import tkinter as tk

from . import rules, storage, words
from .entities import FloatText, Meteor, Particle
from .renderer import POWER_INFO, Renderer
from .sound import Sound
from .theme import GROUND, H, METEOR_COLORS, W, WARN

FREEZE_FRAMES = 5 * rules.FPS
FREEZE_SLOWDOWN = 0.25
CHIP_HALF_HEIGHT = 19


class Game:
    def __init__(self, root):
        self.root = root
        root.title("TypeStorm")
        root.resizable(False, False)
        self.canvas = tk.Canvas(root, width=W, height=H, bg="#070b1f", highlightthickness=0)
        self.canvas.pack()
        self._center_window()
        self.view = Renderer(self.canvas)

        # (x, y, speed) - three speeds give a simple parallax effect
        self.stars = [[random.randint(0, W), random.uniform(0, GROUND), random.choice((0.4, 0.8, 1.4))]
                      for _ in range(90)]

        self.stats = storage.load()
        self.sound = Sound()
        self.difficulties = list(rules.DIFFICULTY)
        self.diff_index = self.difficulties.index("Normal")
        self.state = "menu"          # menu | play | paused | over
        self.ticks = 0
        self.reset()

        root.bind("<Key>", self.on_key)
        self.tick()

    def _center_window(self):
        self.root.update_idletasks()
        x = max(0, (self.root.winfo_screenwidth() - W) // 2)
        y = max(0, (self.root.winfo_screenheight() - H) // 3)
        self.root.geometry(f"+{x}+{y}")

    # ------------------------------------------------------------ state
    @property
    def difficulty(self):
        return self.difficulties[self.diff_index]

    @property
    def factor(self):
        return rules.DIFFICULTY[self.difficulty]

    @property
    def level(self):
        return rules.level_for(self.killed)

    def reset(self):
        self.score = 0
        self.lives = rules.START_LIVES
        self.killed = 0
        self.combo = 0
        self.best_combo = 0
        self.meteors = []
        self.particles = []
        self.floaters = []
        self.target = None
        self.progress = 0
        self.timer = 0.0
        self.flash = 0
        self.shake = 0
        self.banner = 0
        self.freeze = 0
        self.frames_played = 0
        self.keys_total = 0
        self.keys_hit = 0
        self.chars_ok = 0
        self.boss_levels = set()
        self.shown_level = 1
        self.new_best = False

    def start(self):
        self.reset()
        self.state = "play"
        self.timer = rules.spawn_interval(1, self.factor)  # first meteor right away

    # ------------------------------------------------------------ spawning
    def spawn(self):
        level = self.level
        initials = {m.text[0] for m in self.meteors}
        kind = "normal"
        if level >= 2 and random.random() < 0.10 and all(m.kind not in POWER_INFO for m in self.meteors):
            kind = random.choice(list(POWER_INFO))

        text = words.pick_word(min(level, 3) if kind in POWER_INFO else level, initials)
        color = POWER_INFO[kind][2] if kind in POWER_INFO else random.choice(METEOR_COLORS)
        speed = rules.fall_speed(level, self.factor) * random.uniform(0.9, 1.15)
        sway = min(30, (level - 4) * 6) if level >= 5 and kind == "normal" else 0
        margin = int(self.view.chip_width(text) / 2 + sway + 14)
        x = random.randint(margin, W - margin)
        self.meteors.append(Meteor(text, x, -40, speed, color, kind, base_x=x, sway=sway,
                                   phase=random.uniform(0, math.tau)))

    def spawn_boss(self):
        self.boss_levels.add(self.level)
        text = random.choice(words.BOSS_WORDS)
        speed = rules.fall_speed(self.level, self.factor) * 0.45
        self.meteors.append(Meteor(text, W // 2, -50, speed, WARN, "boss", base_x=W // 2))

    # ------------------------------------------------------------ effects
    def explode(self, x, y, color, count=22):
        for _ in range(count):
            angle = random.uniform(0, math.tau)
            power = random.uniform(1, 5)
            self.particles.append(Particle(x, y, math.cos(angle) * power, math.sin(angle) * power,
                                           30, color))

    def destroy(self, m):
        points = rules.score_for_word(len(m.text), self.combo, m.kind == "boss")
        self.score += points
        self.combo += 1
        self.best_combo = max(self.best_combo, self.combo)
        self.killed += 1
        self.chars_ok += len(m.text)
        self.meteors.remove(m)
        self.target, self.progress = None, 0
        self.explode(m.x, m.y, m.color, 40 if m.kind == "boss" else 22)
        self.floaters.append(FloatText(f"+{points}", m.x, m.y - 24, 45, "#ffffff"))
        self.sound.play("power" if m.kind in POWER_INFO else "hit")

        if m.kind == "freeze":
            self.freeze = FREEZE_FRAMES
        elif m.kind == "life":
            self.lives = min(rules.MAX_LIVES, self.lives + 1)
        elif m.kind == "bomb":
            for other in self.meteors[:]:
                if other.kind != "boss":
                    self.explode(other.x, other.y, other.color)
                    self.score += len(other.text) * 5
                    self.meteors.remove(other)
            self.target, self.progress = None, 0

        self.check_level_up()

    def check_level_up(self):
        if self.level > self.shown_level:
            self.shown_level = self.level
            self.banner = 110
            self.sound.play("level")
            if self.level % 4 == 0 and self.level not in self.boss_levels:
                self.spawn_boss()

    def lose_life(self, m):
        self.lives -= 2 if m.kind == "boss" else 1
        self.combo = 0
        self.flash = 14
        self.shake = 16
        self.explode(m.x, GROUND, "#ff5d73", 30)
        self.sound.play("miss")
        if self.lives <= 0:
            self.game_over()

    def game_over(self):
        self.state = "over"
        self.new_best = storage.record_game(self.stats, self.difficulty, self.score, self.killed)
        storage.save(self.stats)
        self.sound.play("over")

    # ------------------------------------------------------------ input
    def on_key(self, e):
        key = e.keysym
        if key == "F1":
            self.sound.enabled = not self.sound.enabled
            return

        if self.state in ("menu", "over"):
            if key == "Return":
                self.start()
            elif key == "Left":
                self.diff_index = (self.diff_index - 1) % len(self.difficulties)
            elif key == "Right":
                self.diff_index = (self.diff_index + 1) % len(self.difficulties)
            return

        if key == "Tab":
            self.state = "paused" if self.state == "play" else "play"
            return
        if self.state == "paused":
            return
        if key == "Escape":
            self.target, self.progress = None, 0
            return

        ch = e.char.lower()
        if len(ch) != 1 or not ch.isalpha():
            return
        self.keys_total += 1

        if self.target is None:
            options = [m for m in self.meteors if m.text[0] == ch]
            if not options:
                self.mistake()
                return
            self.target = max(options, key=lambda m: m.y)   # the one closest to the ground
            self.progress = 1
            self.keys_hit += 1
        elif ch == self.target.text[self.progress]:
            self.progress += 1
            self.keys_hit += 1
        else:
            self.mistake()
            return

        if self.progress == len(self.target.text):
            self.destroy(self.target)

    def mistake(self):
        self.combo = 0
        self.sound.play("wrong")

    # ------------------------------------------------------------ update
    def update(self):
        self.ticks += 1
        speed_up = 1 + self.level * 0.06
        for star in self.stars:
            star[1] += star[2] * speed_up
            if star[1] > GROUND:
                star[0], star[1] = random.randint(0, W), 0

        for p in self.particles:
            p.x += p.vx
            p.y += p.vy
            p.vy += 0.12
            p.life -= 1
        self.particles = [p for p in self.particles if p.life > 0]

        for f in self.floaters:
            f.y -= 1
            f.life -= 1
        self.floaters = [f for f in self.floaters if f.life > 0]

        self.flash = max(0, self.flash - 1)
        self.shake = max(0, self.shake - 1)
        self.banner = max(0, self.banner - 1)
        if self.state != "play":
            return

        self.frames_played += 1
        slow = FREEZE_SLOWDOWN if self.freeze else 1.0
        self.freeze = max(0, self.freeze - 1)

        self.timer += slow
        if self.timer >= rules.spawn_interval(self.level, self.factor):
            self.timer = 0
            self.spawn()

        for m in self.meteors[:]:
            m.y += m.speed * slow
            if m.sway:
                m.phase += 0.04 * slow
                m.x = m.base_x + math.sin(m.phase) * m.sway
            if m.y + CHIP_HALF_HEIGHT >= GROUND:
                self.meteors.remove(m)
                if m is self.target:
                    self.target, self.progress = None, 0
                self.lose_life(m)
                if self.state == "over":
                    return

    # ------------------------------------------------------------ loop
    def tick(self):
        self.update()
        self.view.draw(self)
        self.root.after(16, self.tick)


def run():
    root = tk.Tk()
    Game(root)
    root.mainloop()
