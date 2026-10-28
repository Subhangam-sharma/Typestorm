"""Tiny sound effects. Uses winsound on Windows and stays silent elsewhere."""

import threading

try:
    import winsound
except ImportError:  # Linux / macOS
    winsound = None

PATTERNS = {
    "hit": [(880, 40)],
    "wrong": [(180, 60)],
    "miss": [(220, 90), (150, 140)],
    "power": [(660, 60), (880, 60), (1170, 90)],
    "level": [(523, 80), (659, 80), (784, 80), (1047, 160)],
    "over": [(392, 150), (330, 150), (262, 300)],
}


class Sound:
    def __init__(self):
        self.enabled = winsound is not None

    def play(self, name: str) -> None:
        if not self.enabled or winsound is None:
            return
        notes = PATTERNS.get(name)
        if notes:
            # Beep blocks, so play it on a helper thread to keep the game smooth
            threading.Thread(target=self._play, args=(notes,), daemon=True).start()

    @staticmethod
    def _play(notes) -> None:
        for freq, ms in notes:
            try:
                winsound.Beep(freq, ms)
            except RuntimeError:
                return
