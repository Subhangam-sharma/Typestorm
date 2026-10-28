"""Everything that gets drawn on the canvas.

The renderer only reads the game state; it never changes it. All fonts are
sized in pixels so the layout looks the same on every screen scaling.
"""

import math
import random
import tkinter.font as tkfont

from . import rules
from .theme import (ACCENT, BAD, BG_BOTTOM, BG_TOP, CHIP, GOOD, GROUND, H, MONO_FONT, MUTED,
                    PANEL, PANEL_DARK, PANEL_EDGE, TEXT, UI_FONT, W, WARN, mix)

DYN = "dyn"          # items redrawn every frame
CHIP_H = 38
CHIP_PAD = 16

POWER_INFO = {
    "freeze": ("FREEZE", "Slows time for 5 sec", ACCENT),
    "bomb": ("BOMB", "Clears every meteor", "#ff9f68"),
    "life": ("+LIFE", "Restores one life", GOOD),
}


class Renderer:
    def __init__(self, canvas):
        self.c = canvas
        self._fonts = {}
        self._draw_background()

    # ------------------------------------------------------------ helpers
    def font(self, size, bold=False, family=UI_FONT):
        key = (family, size, bold)
        if key not in self._fonts:
            self._fonts[key] = tkfont.Font(family=family, size=-int(size),
                                           weight="bold" if bold else "normal")
        return self._fonts[key]

    def fit(self, text, size, max_width, bold=False, family=UI_FONT):
        """Largest font (not above `size`) in which the text fits max_width."""
        while size > 9 and self.font(size, bold, family).measure(text) > max_width:
            size -= 1
        return self.font(size, bold, family)

    def text(self, x, y, text, size=14, color=TEXT, bold=False, anchor="center",
             family=UI_FONT, max_width=None):
        font = self.fit(text, size, max_width, bold, family) if max_width else \
            self.font(size, bold, family)
        return self.c.create_text(x, y, text=text, fill=color, font=font, anchor=anchor, tags=DYN)

    def rrect(self, x1, y1, x2, y2, r, fill="", outline="", width=1):
        r = min(r, (x2 - x1) / 2, (y2 - y1) / 2)
        pts = [x1 + r, y1, x2 - r, y1, x2, y1, x2, y1 + r, x2, y2 - r, x2, y2, x2 - r, y2,
               x1 + r, y2, x1, y2, x1, y2 - r, x1, y1 + r, x1, y1]
        return self.c.create_polygon(pts, smooth=True, fill=fill, outline=outline,
                                     width=width, tags=DYN)

    def pill(self, x, y, label, color, size=12, anchor="center", filled=False):
        """Small rounded label. Returns its width."""
        font = self.font(size, True)
        w = font.measure(label) + 20
        h = size + 12
        x1 = {"center": x - w / 2, "w": x, "e": x - w}[anchor]
        self.rrect(x1, y - h / 2, x1 + w, y + h / 2, h / 2,
                   fill=color if filled else mix(PANEL_DARK, color, 0.18), outline=color, width=1)
        self.c.create_text(x1 + w / 2, y, text=label, font=font,
                           fill=PANEL_DARK if filled else color, tags=DYN)
        return w

    def heart(self, cx, cy, size, fill, outline=""):
        pts = []
        for i in range(28):
            t = i / 28 * math.tau
            x = 16 * math.sin(t) ** 3
            y = -(13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t))
            pts += [cx + x * size / 16, cy + y * size / 16 + size * 0.1]
        self.c.create_polygon(pts, fill=fill, outline=outline, width=2, tags=DYN)

    def chip_width(self, word):
        return self.font(18, True, MONO_FONT).measure(word) + CHIP_PAD * 2

    # ------------------------------------------------------------ background
    def _draw_background(self):
        c = self.c
        bands = 60
        for i in range(bands):
            y1, y2 = H * i / bands, H * (i + 1) / bands + 1
            c.create_rectangle(0, y1, W, y2, fill=mix(BG_TOP, BG_BOTTOM, i / (bands - 1)),
                               outline="", tags="bg")
        grid = mix(BG_BOTTOM, ACCENT, 0.07)
        for x in range(0, W + 1, 50):
            c.create_line(x, 0, x, GROUND, fill=grid, tags="bg")
        for y in range(40, GROUND, 50):
            c.create_line(0, y, W, y, fill=grid, tags="bg")

    # ------------------------------------------------------------ main entry
    def draw(self, g):
        c = self.c
        c.delete(DYN)
        self.stars(g)
        self.ground(g)
        for m in g.meteors:
            self.meteor(m, g)
        for p in g.particles:
            r = max(1, p.life / 9)
            c.create_oval(p.x - r, p.y - r, p.x + r, p.y + r, fill=p.color, outline="", tags=DYN)
        for f in g.floaters:
            self.text(f.x, f.y, f.text, 16, mix(BG_TOP, f.color, min(1, f.life / 20)), True)

        if g.freeze:
            c.create_rectangle(3, 3, W - 3, H - 3, outline=mix(BG_TOP, ACCENT, 0.8), width=3, tags=DYN)
        if g.state != "menu":
            self.hud(g)
        if g.state == "play" and g.banner:
            self.level_banner(g)

        if g.state in ("menu", "paused", "over"):
            c.create_rectangle(0, 0, W, H, fill="#02030c", stipple="gray50", outline="", tags=DYN)
        if g.state == "menu":
            self.menu(g)
        elif g.state == "paused":
            self.pause(g)
        elif g.state == "over":
            self.game_over(g)

        if g.shake:
            c.move(DYN, random.randint(-g.shake, g.shake) // 2, random.randint(-g.shake, g.shake) // 2)

    # ------------------------------------------------------------ playfield
    def stars(self, g):
        for x, y, speed in g.stars:
            colour = mix(BG_BOTTOM, "#ffffff", 0.25 + speed * 0.35)
            size = speed * 1.8
            self.c.create_oval(x, y, x + size, y + size, fill=colour, outline="", tags=DYN)

    def ground(self, g):
        c = self.c
        col = BAD if g.flash else GOOD
        c.create_rectangle(0, GROUND, W, H, fill="#0a1230", outline="", tags=DYN)
        c.create_rectangle(0, GROUND - 8, W, GROUND, fill=mix(BG_BOTTOM, col, 0.18), outline="", tags=DYN)
        c.create_line(0, GROUND, W, GROUND, fill=col, width=3, tags=DYN)
        shift = (g.ticks * 0.6) % 36
        x = -36 + shift
        while x < W:
            c.create_rectangle(x, GROUND + 7, x + 18, GROUND + 10, fill=mix("#0a1230", col, 0.45),
                               outline="", tags=DYN)
            x += 36
        self.text(18, GROUND + 30, "FIREWALL", 12, col, True, "w")
        self.text(W // 2, H - 20, "TAB  pause      ESC  drop target      F1  sound", 12, MUTED)
        if not g.sound.enabled:
            self.text(W - 18, GROUND + 30, "SOUND OFF", 12, MUTED, True, "e")

    def meteor(self, m, g):
        c = self.c
        font = self.font(18, True, MONO_FONT)
        width = self.chip_width(m.text)
        x1, x2 = m.x - width / 2, m.x + width / 2
        y1, y2 = m.y - CHIP_H / 2, m.y + CHIP_H / 2
        is_target = m is g.target
        boss = m.kind == "boss"
        frozen = bool(g.freeze)
        edge = mix(m.color, ACCENT, 0.5) if frozen else m.color

        # comet trail
        for i in range(1, 6):
            top = y1 - i * 9
            c.create_line(m.x, top - 5, m.x, top, fill=mix(BG_TOP, edge, 0.75 - i * 0.13),
                          width=max(1, 4 - i // 2), tags=DYN)
        if is_target:
            self.rrect(x1 - 5, y1 - 5, x2 + 5, y2 + 5, CHIP_H / 2 + 5,
                       outline=mix(BG_TOP, ACCENT, 0.55), width=3)
        self.rrect(x1, y1, x2, y2, CHIP_H / 2, fill=CHIP,
                   outline="#ffffff" if is_target else (WARN if boss else edge),
                   width=3 if (is_target or boss) else 2)

        done = m.text[:g.progress] if is_target else ""
        left = m.x - font.measure(m.text) / 2
        c.create_text(left, m.y, anchor="w", text=done, fill=GOOD, font=font, tags=DYN)
        c.create_text(left + font.measure(done), m.y, anchor="w", text=m.text[len(done):],
                      fill=TEXT, font=font, tags=DYN)

        if boss:
            self.pill(m.x, y1 - 18, "BOSS  x3 points", WARN, 11, filled=True)
        elif m.kind in POWER_INFO:
            self.pill(m.x, y1 - 18, POWER_INFO[m.kind][0], POWER_INFO[m.kind][2], 11, filled=True)

    # ------------------------------------------------------------ HUD
    def hud(self, g):
        c = self.c
        self.rrect(12, 10, W - 12, 64, 14, fill=PANEL, outline=PANEL_EDGE, width=1)

        self.text(30, 19, "SCORE", 11, MUTED, True, "nw")
        self.text(30, 31, f"{g.score:,}", 26, TEXT, True, "nw")

        self.text(W // 2, 23, f"LEVEL {g.level}", 17, WARN, True)
        filled = (g.killed % rules.WORDS_PER_LEVEL) / rules.WORDS_PER_LEVEL
        bx1, bx2 = W // 2 - 80, W // 2 + 80
        self.rrect(bx1, 42, bx2, 50, 4, fill=PANEL_DARK, outline=PANEL_EDGE)
        if filled > 0:
            self.rrect(bx1, 42, bx1 + max(8, 160 * filled), 50, 4, fill=WARN)

        slots = max(rules.START_LIVES, g.lives)
        for i in range(slots):
            x = W - 38 - (slots - 1 - i) * 26
            if i < g.lives:
                self.heart(x, 38, 10, BAD)
            else:
                self.heart(x, 38, 10, "", mix(BAD, PANEL, 0.6))

        if g.state == "play" and g.combo >= 3:
            self.pill(14, 82, f"COMBO x{g.combo}  -  score x{rules.combo_multiplier(g.combo):g}",
                      ACCENT, 12, "w")
        if g.freeze:
            self.pill(W - 14, 82, f"FROZEN {g.freeze / rules.FPS:.1f}s", ACCENT, 12, "e", filled=True)

    def level_banner(self, g):
        fade = min(1, g.banner / 30)
        col = mix(BG_BOTTOM, WARN, fade)
        self.text(W // 2 + 2, 252, f"LEVEL {g.level}", 54, mix(BG_BOTTOM, "#000000", fade * 0.5), True)
        self.text(W // 2, 250, f"LEVEL {g.level}", 54, col, True)
        self.text(W // 2, 292, "THE STORM SPEEDS UP", 14, mix(BG_BOTTOM, TEXT, fade), True)

    # ------------------------------------------------------------ screens
    def panel(self, x1, y1, x2, y2):
        self.rrect(x1 + 4, y1 + 6, x2 + 4, y2 + 6, 22, fill="#02030c")      # shadow
        self.rrect(x1, y1, x2, y2, 22, fill=PANEL, outline=PANEL_EDGE, width=2)

    def menu(self, g):
        c = self.c
        self.panel(110, 55, W - 110, 565)
        glow = mix(PANEL, ACCENT, 0.35)
        self.text(W // 2 + 3, 118 + 3, "TYPESTORM", 56, glow, True, max_width=480)
        self.text(W // 2, 118, "TYPESTORM", 56, ACCENT, True, max_width=480)
        self.text(W // 2, 166, "Type the falling words before they hit the firewall",
                  14, MUTED, max_width=500)

        # difficulty selector
        x0, y1, y2, cell = W // 2 - 180, 200, 242, 120
        self.rrect(x0, y1, x0 + cell * 3, y2, 21, fill=PANEL_DARK, outline=PANEL_EDGE)
        for i, name in enumerate(g.difficulties):
            selected = i == g.diff_index
            if selected:
                self.rrect(x0 + i * cell + 4, y1 + 4, x0 + (i + 1) * cell - 4, y2 - 4, 17, fill=ACCENT)
            self.text(x0 + i * cell + cell / 2, (y1 + y2) / 2, name, 15,
                      PANEL_DARK if selected else MUTED, True)
        self.text(W // 2, 262, f"Left / Right to change   -   Best score: {g.stats['best'][g.difficulty]:,}",
                  12, MUTED, max_width=480)

        # power words
        self.text(W // 2, 298, "POWER WORDS", 11, MUTED, True)
        cw, gap = 150, 12
        cx = W // 2 - (cw * 3 + gap * 2) / 2
        for i, kind in enumerate(("freeze", "bomb", "life")):
            title, desc, col = POWER_INFO[kind]
            x = cx + i * (cw + gap)
            self.rrect(x, 312, x + cw, 380, 14, fill=PANEL_DARK, outline=mix(PANEL_DARK, col, 0.55))
            self.text(x + cw / 2, 336, title, 16, col, True)
            self.text(x + cw / 2, 360, desc, 12, MUTED, max_width=cw - 16)
        self.text(W // 2, 408, "Every 4th level a BOSS word drops: triple points, but it costs 2 lives.",
                  12, WARN, max_width=480)

        # start button
        pulse = (math.sin(g.ticks * 0.08) + 1) / 2
        self.rrect(W // 2 - 140, 440, W // 2 + 140, 490, 25,
                   fill=mix(GOOD, "#7dffd2", pulse * 0.5), outline="")
        self.text(W // 2, 465, "PRESS  ENTER  TO  START", 16, PANEL_DARK, True)
        self.text(W // 2, 524, "Wrong keys break your combo  -  every 5 words in a row add +0.5x",
                  12, MUTED, max_width=480)

    def pause(self, g):
        self.panel(240, 230, W - 240, 370)
        self.text(W // 2, 280, "PAUSED", 40, ACCENT, True)
        self.text(W // 2, 335, "Press TAB to continue", 14, MUTED)

    def game_over(self, g):
        self.panel(120, 60, W - 120, 560)
        self.text(W // 2, 112, "SYSTEM BREACHED", 38, BAD, True, max_width=520)
        self.text(W // 2, 190, f"{g.score:,}", 64, TEXT, True, max_width=400)
        self.text(W // 2, 238, "FINAL SCORE", 12, MUTED, True)
        if g.new_best:
            self.pill(W // 2, 272, "NEW PERSONAL BEST", WARN, 13, filled=True)
        else:
            self.text(W // 2, 272, f"Best on {g.difficulty}: {g.stats['best'][g.difficulty]:,}", 13, MUTED)

        acc = rules.accuracy(g.keys_hit, g.keys_total)
        speed = rules.wpm(g.chars_ok, g.frames_played)
        cards = [("LEVEL", str(g.level)), ("WORDS", str(g.killed)), ("BEST COMBO", f"x{g.best_combo}"),
                 ("ACCURACY", f"{acc:.0f}%"), ("SPEED", f"{speed:.0f} WPM"), ("MODE", g.difficulty)]
        cw, ch, gap = 150, 70, 14
        x0 = W // 2 - (cw * 3 + gap * 2) / 2
        for i, (label, value) in enumerate(cards):
            x = x0 + (i % 3) * (cw + gap)
            y = 312 + (i // 3) * (ch + gap)
            self.rrect(x, y, x + cw, y + ch, 14, fill=PANEL_DARK, outline=PANEL_EDGE)
            self.text(x + cw / 2, y + 25, value, 22, TEXT, True, max_width=cw - 16)
            self.text(x + cw / 2, y + 52, label, 11, MUTED, True)

        pulse = (math.sin(g.ticks * 0.08) + 1) / 2
        self.rrect(W // 2 - 140, 482, W // 2 + 140, 526, 22,
                   fill=mix(GOOD, "#7dffd2", pulse * 0.5), outline="")
        self.text(W // 2, 504, "ENTER  TO  PLAY  AGAIN", 15, PANEL_DARK, True)
        self.text(W // 2, 546, "Left / Right to change difficulty", 11, MUTED)
