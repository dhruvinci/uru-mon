"""Small helpers for authoring maps in code instead of hand-typed ASCII.

A Canvas holds the layout characters (see compiler.py for the legend); helper functions build common rooms.
"""

DIRS = {"UP": (0, -1), "DOWN": (0, 1), "LEFT": (-1, 0), "RIGHT": (1, 0)}


class Canvas:
    def __init__(self, w, h, fill="."):
        self.w = w
        self.h = h
        self.g = [[fill] * w for _ in range(h)]

    def set(self, x, y, ch):
        if 0 <= x < self.w and 0 <= y < self.h:
            self.g[y][x] = ch
        return self

    def get(self, x, y):
        return self.g[y][x] if 0 <= x < self.w and 0 <= y < self.h else "X"

    def fill(self, x, y, w, h, ch):
        for yy in range(y, y + h):
            for xx in range(x, x + w):
                self.set(xx, yy, ch)
        return self

    def hline(self, x0, x1, y, ch, thick=1):
        return self.fill(min(x0, x1), y, abs(x1 - x0) + 1, thick, ch)

    def vline(self, x, y0, y1, ch, thick=1):
        return self.fill(x, min(y0, y1), thick, abs(y1 - y0) + 1, ch)

    def text(self, x, y, rows):
        """Paste a block of characters; spaces are skipped."""
        for dy, row in enumerate(rows.strip("\n").split("\n")):
            for dx, ch in enumerate(row):
                if ch != " ":
                    self.set(x + dx, y + dy, ch)
        return self

    def clear_area(self, x, y, w, h, ch="."):
        return self.fill(x, y, w, h, ch)

    def tree_border(self, kind="T", gaps=None, sides="NSEW", ground="."):
        """Rings the map with 2x2 trees, leaving gaps: {side: [(from, to), ...]} in tile coords along that side."""
        gaps = gaps or {}

        def in_gap(side, t):
            return any(a <= t <= b for a, b in gaps.get(side, []))

        def ok(x, y):
            return self.get(x, y) not in "TJGRYOP" and self.get(x + 1, y) not in "TJGRYOP" and \
                self.get(x, y + 1) not in "TJGRYOP" and self.get(x + 1, y + 1) not in "TJGRYOP"

        if "N" in sides:
            for x in range(0, self.w - 1, 2):
                if not in_gap("N", x) and not in_gap("N", x + 1) and ok(x, 0):
                    self.set(x, 0, kind)
                    self.set(x + 1, 0, ground)
                    self.set(x, 1, ground)
                    self.set(x + 1, 1, ground)
                elif in_gap("N", x) != in_gap("N", x + 1):
                    for xx in (x, x + 1):
                        if not in_gap("N", xx):
                            self.fill(xx, 0, 1, 2, "%")
        if "S" in sides:
            y = self.h - 2
            for x in range(0, self.w - 1, 2):
                if not in_gap("S", x) and not in_gap("S", x + 1) and ok(x, y):
                    self.set(x, y, kind)
                elif in_gap("S", x) != in_gap("S", x + 1):
                    for xx in (x, x + 1):
                        if not in_gap("S", xx):
                            self.fill(xx, y, 1, 2, "%")
        if "W" in sides:
            for y in range(2, self.h - 3, 2):
                if not in_gap("W", y) and not in_gap("W", y + 1) and ok(0, y):
                    self.set(0, y, kind)
                elif in_gap("W", y) != in_gap("W", y + 1):
                    for yy in (y, y + 1):
                        if not in_gap("W", yy):
                            self.fill(0, yy, 2, 1, "%")
        if "E" in sides:
            x = self.w - 2
            for y in range(2, self.h - 3, 2):
                if not in_gap("E", y) and not in_gap("E", y + 1) and ok(x, y):
                    self.set(x, y, kind)
                elif in_gap("E", y) != in_gap("E", y + 1):
                    for yy in (y, y + 1):
                        if not in_gap("E", yy):
                            self.fill(x, yy, 2, 1, "%")
        return self

    def trees(self, x, y, w, h, kind="T"):
        """A solid block of 2x2 trees covering (x, y, w, h); w and h should be even."""
        for yy in range(y, y + h, 2):
            for xx in range(x, x + w, 2):
                self.set(xx, yy, kind)
                self.set(xx + 1, yy, ".")
                self.set(xx, yy + 1, ".")
                self.set(xx + 1, yy + 1, ".")
        return self

    def layout(self):
        return "\n".join("".join(r) for r in self.g)


def room(w, h, floor="w", exit_x=None, wall="plain", extra_exits=()):
    """A GBA-style room: a two-tile wall band on top, floor below, a door mat in the bottom row at exit_x."""
    c = Canvas(w, h, floor)
    c.fill(0, 0, w, 2, "X")
    c.fill(0, h - 1, w, 1, "X")
    mats = []
    if exit_x is not None:
        c.set(exit_x, h - 1, "M")
        mats.append(exit_x)
    for ex in extra_exits:
        c.set(ex, h - 1, "M")
    return c, [(0, 0, w, wall)]


def warp(id, x, y, to, toId=None, exit="UP", dir=None, mode="bump", **kw):
    d = dict(id=id, x=x, y=y, to=to, exit=exit, mode=mode, **kw)
    if toId is not None:
        d["toId"] = toId
    if dir:
        d["dir"] = dir
    return d


def npc(id, x, y, sprite, script=None, facing="DOWN", movement="IDLE", **kw):
    d = dict(id=id, x=x, y=y, sprite=sprite, facing=facing, movement=movement, **kw)
    if script is not None:
        d["script"] = script if isinstance(script, list) else [script]
    return d


def trainer(id, x, y, sprite, trainer_id, facing="DOWN", sight=4, **kw):
    return dict(id=id, x=x, y=y, sprite=sprite, facing=facing, trainer=trainer_id, sight=sight, movement="IDLE", **kw)


def say(*lines, speaker=None):
    d = {"say": list(lines) if len(lines) > 1 else lines[0]}
    if speaker:
        d["speaker"] = speaker
    return d


def enc(rate, *slots):
    """Encounter table: slots are (species, min, max, weight)."""
    return {"rate": rate, "slots": [dict(species=s, min=a, max=b, weight=w) for s, a, b, w in slots]}
