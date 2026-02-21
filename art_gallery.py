#!/usr/bin/env python3
"""Interactive Terminal Art Gallery — 6 generative art animations in pure Python."""

import curses
import math
import random
import time

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def clamp(v, lo, hi):
    return max(lo, min(hi, v))

def init_colors(stdscr):
    """Set up color pairs. Returns True if 256-color mode is available."""
    curses.start_color()
    curses.use_default_colors()
    has256 = curses.COLORS >= 256
    # Pairs 1-7: basic colors
    for i in range(1, 8):
        curses.init_pair(i, i, -1)
    if has256:
        # Pairs 10-49: green shades for matrix
        greens = [22, 28, 34, 40, 46, 82, 118, 154, 190, 226]
        for idx, c in enumerate(greens):
            curses.init_pair(10 + idx, c, -1)
        # Pairs 50-99: rainbow for plasma / fireworks
        rainbow = [196, 202, 208, 214, 220, 226, 190, 154, 118, 82,
                   46, 47, 48, 49, 50, 51, 45, 39, 33, 27,
                   21, 57, 93, 129, 165, 201, 200, 199, 198, 197]
        for idx, c in enumerate(rainbow):
            curses.init_pair(50 + idx, c, -1)
        # Pairs 100-109: firework burst colors
        burst = [196, 208, 226, 46, 51, 21, 201, 231, 214, 118]
        for idx, c in enumerate(burst):
            curses.init_pair(100 + idx, c, -1)
    return has256


# ---------------------------------------------------------------------------
# Animation: Matrix Rain
# ---------------------------------------------------------------------------

class MatrixRain:
    name = "Matrix Rain"
    CHARS = "abcdefghijklmnopqrstuvwxyz0123456789@#$%&*(){}[]<>?/\\|~"

    def __init__(self, h, w, has256):
        self.h, self.w, self.has256 = h, w, has256
        self.reset()

    def reset(self):
        self.drops = []
        for x in range(self.w):
            if random.random() < 0.4:
                self.drops.append({"x": x, "y": random.randint(-self.h, 0),
                                   "speed": random.randint(1, 3),
                                   "length": random.randint(5, self.h // 2)})

    def resize(self, h, w):
        self.h, self.w = h, w
        self.reset()

    def update(self):
        for d in self.drops:
            d["y"] += d["speed"]
            if d["y"] - d["length"] > self.h:
                d["y"] = random.randint(-self.h // 2, 0)
                d["x"] = random.randint(0, self.w - 1)
                d["speed"] = random.randint(1, 3)
                d["length"] = random.randint(5, self.h // 2)
        # occasionally spawn new drops
        if random.random() < 0.3 and len(self.drops) < self.w:
            self.drops.append({"x": random.randint(0, self.w - 1),
                               "y": random.randint(-10, 0),
                               "speed": random.randint(1, 3),
                               "length": random.randint(5, self.h // 2)})

    def draw(self, stdscr):
        for d in self.drops:
            x = d["x"]
            for i in range(d["length"]):
                y = d["y"] - i
                if 0 <= y < self.h and 0 <= x < self.w:
                    ch = random.choice(self.CHARS) if i < 3 else self.CHARS[random.randint(0, len(self.CHARS) - 1)]
                    if i == 0:
                        attr = curses.color_pair(7) | curses.A_BOLD  # white head
                    elif self.has256:
                        shade = clamp(9 - (i * 10 // d["length"]), 0, 9)
                        attr = curses.color_pair(10 + shade)
                    else:
                        attr = curses.color_pair(2) | (curses.A_BOLD if i < d["length"] // 3 else 0)
                    try:
                        stdscr.addch(y, x, ch, attr)
                    except curses.error:
                        pass


# ---------------------------------------------------------------------------
# Animation: Starfield
# ---------------------------------------------------------------------------

class Starfield:
    name = "Starfield"

    def __init__(self, h, w, has256):
        self.h, self.w, self.has256 = h, w, has256
        self.reset()

    def reset(self):
        self.stars = []
        for _ in range(120):
            self.stars.append(self._new_star())

    def _new_star(self):
        return {"x": random.uniform(-1, 1), "y": random.uniform(-1, 1),
                "z": random.uniform(0.1, 1.0)}

    def resize(self, h, w):
        self.h, self.w = h, w

    def update(self):
        for s in self.stars:
            s["z"] -= 0.02
            if s["z"] <= 0.005:
                ns = self._new_star()
                ns["z"] = 1.0
                s.update(ns)

    def draw(self, stdscr):
        cx, cy = self.w // 2, self.h // 2
        for s in self.stars:
            sx = int(cx + s["x"] / s["z"] * cx)
            sy = int(cy + s["y"] / s["z"] * cy)
            if 0 <= sy < self.h and 0 <= sx < self.w:
                brightness = 1.0 - s["z"]
                if brightness > 0.8:
                    ch, attr = "*", curses.color_pair(7) | curses.A_BOLD
                elif brightness > 0.5:
                    ch, attr = "+", curses.color_pair(7)
                elif brightness > 0.2:
                    ch, attr = ".", curses.color_pair(6)
                else:
                    ch, attr = ".", curses.color_pair(0)
                try:
                    stdscr.addch(sy, sx, ch, attr)
                except curses.error:
                    pass


# ---------------------------------------------------------------------------
# Animation: Fireworks
# ---------------------------------------------------------------------------

class Fireworks:
    name = "Fireworks"

    def __init__(self, h, w, has256):
        self.h, self.w, self.has256 = h, w, has256
        self.reset()

    def reset(self):
        self.rockets = []
        self.particles = []
        self.tick = 0

    def resize(self, h, w):
        self.h, self.w = h, w

    def _explode(self, x, y):
        color = random.randint(0, 9)
        count = random.randint(20, 40)
        for _ in range(count):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(0.5, 2.5)
            self.particles.append({
                "x": x, "y": y,
                "vx": math.cos(angle) * speed,
                "vy": math.sin(angle) * speed - 0.5,
                "life": random.randint(10, 25),
                "color": color,
            })

    def update(self):
        self.tick += 1
        # launch rockets
        if self.tick % 15 == 0 or (random.random() < 0.08):
            self.rockets.append({
                "x": random.uniform(self.w * 0.1, self.w * 0.9),
                "y": float(self.h - 1),
                "vy": -random.uniform(1.0, 2.0),
                "target_y": random.uniform(self.h * 0.1, self.h * 0.5),
            })
        # move rockets
        new_rockets = []
        for r in self.rockets:
            r["y"] += r["vy"]
            if r["y"] <= r["target_y"]:
                self._explode(r["x"], r["y"])
            else:
                new_rockets.append(r)
        self.rockets = new_rockets
        # move particles
        new_particles = []
        for p in self.particles:
            p["x"] += p["vx"]
            p["y"] += p["vy"]
            p["vy"] += 0.08  # gravity
            p["vx"] *= 0.98
            p["life"] -= 1
            if p["life"] > 0:
                new_particles.append(p)
        self.particles = new_particles

    def draw(self, stdscr):
        for r in self.rockets:
            iy, ix = int(r["y"]), int(r["x"])
            if 0 <= iy < self.h and 0 <= ix < self.w:
                try:
                    stdscr.addch(iy, ix, "|", curses.color_pair(7) | curses.A_BOLD)
                except curses.error:
                    pass
        for p in self.particles:
            iy, ix = int(p["y"]), int(p["x"])
            if 0 <= iy < self.h and 0 <= ix < self.w:
                if self.has256:
                    attr = curses.color_pair(100 + p["color"])
                else:
                    attr = curses.color_pair(1 + p["color"] % 7)
                if p["life"] > 15:
                    ch = "*"
                    attr |= curses.A_BOLD
                elif p["life"] > 8:
                    ch = "+"
                else:
                    ch = "."
                try:
                    stdscr.addch(iy, ix, ch, attr)
                except curses.error:
                    pass


# ---------------------------------------------------------------------------
# Animation: Game of Life
# ---------------------------------------------------------------------------

class GameOfLife:
    name = "Game of Life"

    def __init__(self, h, w, has256):
        self.h, self.w, self.has256 = h, w, has256
        self.reset()

    def reset(self):
        self.grid = [[random.random() < 0.3 for _ in range(self.w)] for _ in range(self.h)]
        self.age = [[0] * self.w for _ in range(self.h)]

    def resize(self, h, w):
        self.h, self.w = h, w
        self.reset()

    def update(self):
        new = [[False] * self.w for _ in range(self.h)]
        for y in range(self.h):
            for x in range(self.w):
                n = 0
                for dy in (-1, 0, 1):
                    for dx in (-1, 0, 1):
                        if dy == 0 and dx == 0:
                            continue
                        ny, nx = (y + dy) % self.h, (x + dx) % self.w
                        if self.grid[ny][nx]:
                            n += 1
                if self.grid[y][x]:
                    new[y][x] = n in (2, 3)
                else:
                    new[y][x] = n == 3
                if new[y][x]:
                    self.age[y][x] = self.age[y][x] + 1 if self.grid[y][x] else 1
                else:
                    self.age[y][x] = 0
        self.grid = new

    def draw(self, stdscr):
        for y in range(self.h):
            for x in range(self.w):
                if self.grid[y][x]:
                    a = self.age[y][x]
                    if self.has256:
                        idx = clamp(a, 0, 29)
                        attr = curses.color_pair(50 + idx)
                    else:
                        attr = curses.color_pair(1 + (a % 7))
                    try:
                        stdscr.addch(y, x, "\u2588", attr)
                    except curses.error:
                        pass


# ---------------------------------------------------------------------------
# Animation: Plasma Waves
# ---------------------------------------------------------------------------

class PlasmaWaves:
    name = "Plasma Waves"
    GRADIENT = " .:-=+*#%@"

    def __init__(self, h, w, has256):
        self.h, self.w, self.has256 = h, w, has256
        self.t = 0.0

    def reset(self):
        self.t = 0.0

    def resize(self, h, w):
        self.h, self.w = h, w

    def update(self):
        self.t += 0.07

    def draw(self, stdscr):
        t = self.t
        for y in range(self.h):
            for x in range(self.w):
                v = math.sin(x * 0.06 + t)
                v += math.sin(y * 0.08 + t * 0.7)
                v += math.sin((x + y) * 0.04 + t * 0.5)
                v += math.sin(math.sqrt(x * x + y * y) * 0.04 + t * 0.8)
                # v is roughly in [-4, 4], normalize to [0, 1]
                nv = (v + 4) / 8.0
                ci = int(nv * (len(self.GRADIENT) - 1))
                ch = self.GRADIENT[clamp(ci, 0, len(self.GRADIENT) - 1)]
                if self.has256:
                    pair = 50 + int(nv * 29)
                    attr = curses.color_pair(clamp(pair, 50, 79))
                else:
                    attr = curses.color_pair(1 + int(nv * 6))
                try:
                    stdscr.addch(y, x, ch, attr)
                except curses.error:
                    pass


# ---------------------------------------------------------------------------
# Animation: Maze Generator (recursive backtracker)
# ---------------------------------------------------------------------------

class MazeGenerator:
    name = "Maze Generator"

    def __init__(self, h, w, has256):
        self.h, self.w, self.has256 = h, w, has256
        self.reset()

    def resize(self, h, w):
        self.h, self.w = h, w
        self.reset()

    def reset(self):
        # maze dimensions (odd numbers for walls+cells)
        self.mh = (self.h // 2) * 2 + 1
        self.mw = (self.w // 2) * 2 + 1
        self.grid = [[1] * self.mw for _ in range(self.mh)]  # 1=wall
        self.stack = []
        self.visited = set()
        self.done = False
        self.done_tick = 0
        # start at (1,1)
        sy, sx = 1, 1
        if sy < self.mh and sx < self.mw:
            self.grid[sy][sx] = 0
            self.visited.add((sy, sx))
            self.stack.append((sy, sx))

    def _neighbors(self, y, x):
        dirs = [(y - 2, x), (y + 2, x), (y, x - 2), (y, x + 2)]
        result = []
        for ny, nx in dirs:
            if 1 <= ny < self.mh - 1 and 1 <= nx < self.mw - 1 and (ny, nx) not in self.visited:
                result.append((ny, nx))
        return result

    def update(self):
        if self.done:
            self.done_tick += 1
            if self.done_tick > 80:
                self.reset()
            return
        steps = max(1, (self.mh * self.mw) // 200)  # carve multiple cells per frame
        for _ in range(steps):
            if not self.stack:
                self.done = True
                return
            cy, cx = self.stack[-1]
            nbrs = self._neighbors(cy, cx)
            if nbrs:
                ny, nx = random.choice(nbrs)
                # carve wall between
                wy, wx = (cy + ny) // 2, (cx + nx) // 2
                self.grid[wy][wx] = 0
                self.grid[ny][nx] = 0
                self.visited.add((ny, nx))
                self.stack.append((ny, nx))
            else:
                self.stack.pop()

    def draw(self, stdscr):
        for y in range(min(self.mh, self.h)):
            for x in range(min(self.mw, self.w)):
                if self.grid[y][x] == 1:
                    if self.has256:
                        attr = curses.color_pair(50 + 15)  # wall color
                    else:
                        attr = curses.color_pair(4)
                    try:
                        stdscr.addch(y, x, "\u2588", attr)
                    except curses.error:
                        pass
                else:
                    # passage — show head of stack brighter
                    if self.stack and (y, x) == self.stack[-1]:
                        attr = curses.color_pair(7) | curses.A_BOLD
                        try:
                            stdscr.addch(y, x, "\u00b7", attr)
                        except curses.error:
                            pass


# ---------------------------------------------------------------------------
# Animation: Spirograph
# ---------------------------------------------------------------------------

class Spirograph:
    name = "Spirograph"

    def __init__(self, h, w, has256):
        self.h, self.w, self.has256 = h, w, has256
        self.reset()

    def reset(self):
        self.curves = []
        self.tick = 0
        self._new_curve_set()

    def _new_curve_set(self):
        self.curves = []
        offsets = [0, 10, 20]
        random.shuffle(offsets)
        for i in range(3):
            R = random.uniform(8, 16)
            r = random.uniform(2, 7)
            d = random.uniform(3, 10)
            self.curves.append({
                "R": R, "r": r, "d": d, "t": random.uniform(0, math.pi),
                "color_base": offsets[i], "trail": []
            })

    def resize(self, h, w):
        self.h, self.w = h, w
        self.reset()

    def update(self):
        self.tick += 1
        cx, cy = self.w / 2, self.h / 2
        scale = min(self.h, self.w) * 0.35
        for c in self.curves:
            for _ in range(3):  # plot multiple points per frame
                t = c["t"]
                R, r, d = c["R"], c["r"], c["d"]
                x = (R - r) * math.cos(t) + d * math.cos((R - r) / r * t)
                y = (R - r) * math.sin(t) - d * math.sin((R - r) / r * t)
                # normalize to [-1,1] range then scale
                norm = R + d
                sx = int(cx + x / norm * scale)
                sy = int(cy + y / norm * scale * 0.5)  # aspect correction
                c["trail"].append((sx, sy, 0))
                c["t"] += 0.05
            # age trail
            c["trail"] = [(x, y, a + 1) for x, y, a in c["trail"] if a < 80]
        if self.tick > 400:
            self.tick = 0
            self._new_curve_set()

    def draw(self, stdscr):
        for c in self.curves:
            base = c["color_base"]
            for x, y, age in c["trail"]:
                if 0 <= y < self.h and 0 <= x < self.w:
                    if age < 5:
                        ch, bold = "@", True
                    elif age < 20:
                        ch, bold = "*", True
                    elif age < 40:
                        ch, bold = "+", False
                    else:
                        ch, bold = ".", False
                    if self.has256:
                        ci = 50 + (base + min(age // 3, 9)) % 30
                        attr = curses.color_pair(ci)
                    else:
                        attr = curses.color_pair(1 + base % 7)
                    if bold:
                        attr |= curses.A_BOLD
                    try:
                        stdscr.addch(y, x, ch, attr)
                    except curses.error:
                        pass


# ---------------------------------------------------------------------------
# Animation: Raindrop Ripples
# ---------------------------------------------------------------------------

class RaindropRipples:
    name = "Raindrop Ripples"

    def __init__(self, h, w, has256):
        self.h, self.w, self.has256 = h, w, has256
        self.reset()

    def reset(self):
        self.ripples = []
        self.tick = 0

    def resize(self, h, w):
        self.h, self.w = h, w

    def update(self):
        self.tick += 1
        for r in self.ripples:
            r["radius"] += 0.8
            r["age"] += 1
        self.ripples = [r for r in self.ripples if r["radius"] < r["max_radius"]]
        if random.random() < 0.1 and len(self.ripples) < 10:
            self.ripples.append({
                "cx": random.uniform(0, self.w),
                "cy": random.uniform(0, self.h),
                "radius": 0.0,
                "max_radius": random.uniform(min(self.h, self.w) * 0.5,
                                             max(self.h, self.w) * 1.2),
                "age": 0,
            })

    GRADIENT = " .:-=+*#%@"

    def draw(self, stdscr):
        for y in range(self.h):
            for x in range(self.w):
                intensity = 0.0
                for r in self.ripples:
                    dx = x - r["cx"]
                    dy = (y - r["cy"]) * 2  # aspect correction
                    dist = math.sqrt(dx * dx + dy * dy)
                    ring = max(0.0, 1.0 - abs(dist - r["radius"]) / 2.5)
                    fade = max(0.0, 1.0 - r["radius"] / r["max_radius"])
                    intensity += ring * fade
                if intensity > 0.05:
                    intensity = min(intensity, 1.0)
                    ci = int(intensity * (len(self.GRADIENT) - 1))
                    ch = self.GRADIENT[clamp(ci, 0, len(self.GRADIENT) - 1)]
                    if self.has256:
                        # map intensity to cool blue/cyan colors
                        pair = 50 + 15 + int((1.0 - intensity) * 14)
                        attr = curses.color_pair(clamp(pair, 50, 79))
                    else:
                        attr = curses.color_pair(6) if intensity < 0.5 else curses.color_pair(7)
                    if intensity > 0.7:
                        attr |= curses.A_BOLD
                    try:
                        stdscr.addch(y, x, ch, attr)
                    except curses.error:
                        pass


# ---------------------------------------------------------------------------
# Animation: Lissajous Weaver
# ---------------------------------------------------------------------------

class LissajousWeaver:
    name = "Lissajous Weaver"

    def __init__(self, h, w, has256):
        self.h, self.w, self.has256 = h, w, has256
        self.reset()

    def reset(self):
        self.phosphor = [[0.0] * self.w for _ in range(self.h)]
        self.beams = []
        ratios = [(3, 2), (5, 4), (3, 4), (7, 6)]
        for i, (a, b) in enumerate(ratios):
            self.beams.append({
                "a": a, "b": b, "t": 0.0,
                "delta": random.uniform(0, 2 * math.pi),
                "delta_drift": random.uniform(0.001, 0.004),
            })
        self.tick = 0

    def resize(self, h, w):
        self.h, self.w = h, w
        self.reset()

    def update(self):
        self.tick += 1
        # decay phosphor
        for y in range(self.h):
            for x in range(self.w):
                self.phosphor[y][x] *= 0.93
        cx, cy = self.w / 2, self.h / 2
        sx, sy = self.w * 0.42, self.h * 0.42
        for beam in self.beams:
            beam["t"] += 0.04
            beam["delta"] += beam["delta_drift"]
            px = math.sin(beam["a"] * beam["t"] + beam["delta"]) * sx + cx
            py = math.sin(beam["b"] * beam["t"]) * sy + cy
            ix, iy = int(px), int(py)
            # plot with glow
            for dy in range(-1, 2):
                for dx in range(-1, 2):
                    ny, nx = iy + dy, ix + dx
                    if 0 <= ny < self.h and 0 <= nx < self.w:
                        v = 1.0 if dx == 0 and dy == 0 else 0.5
                        self.phosphor[ny][nx] = min(1.0, self.phosphor[ny][nx] + v)
        if self.tick > 600:
            self.tick = 0
            ratios = [(3, 2), (5, 4), (3, 4), (7, 6), (5, 3), (4, 3)]
            random.shuffle(ratios)
            for i, beam in enumerate(self.beams):
                beam["a"], beam["b"] = ratios[i]
                beam["delta"] = random.uniform(0, 2 * math.pi)

    def draw(self, stdscr):
        for y in range(self.h):
            for x in range(self.w):
                v = self.phosphor[y][x]
                if v > 0.05:
                    if v > 0.8:
                        ch = "\u2588"
                    elif v > 0.5:
                        ch = "#"
                    elif v > 0.3:
                        ch = "*"
                    elif v > 0.15:
                        ch = "+"
                    else:
                        ch = "."
                    if self.has256:
                        shade = clamp(int(v * 9), 0, 9)
                        attr = curses.color_pair(10 + shade)
                    else:
                        attr = curses.color_pair(2)
                    if v > 0.6:
                        attr |= curses.A_BOLD
                    try:
                        stdscr.addch(y, x, ch, attr)
                    except curses.error:
                        pass


# ---------------------------------------------------------------------------
# Animation: Voronoi Landscape
# ---------------------------------------------------------------------------

class VoronoiLandscape:
    name = "Voronoi Landscape"

    def __init__(self, h, w, has256):
        self.h, self.w, self.has256 = h, w, has256
        self.reset()

    def reset(self):
        self.seeds = []
        n = random.randint(12, 16)
        for i in range(n):
            self.seeds.append({
                "x": random.uniform(0, self.w),
                "y": random.uniform(0, self.h),
                "vx": random.uniform(-0.3, 0.3),
                "vy": random.uniform(-0.3, 0.3),
                "color": i % 30,
            })

    def resize(self, h, w):
        self.h, self.w = h, w
        self.reset()

    def update(self):
        for s in self.seeds:
            s["x"] += s["vx"]
            s["y"] += s["vy"]
            if s["x"] < 0 or s["x"] >= self.w:
                s["vx"] = -s["vx"]
                s["x"] = clamp(s["x"], 0, self.w - 1)
            if s["y"] < 0 or s["y"] >= self.h:
                s["vy"] = -s["vy"]
                s["y"] = clamp(s["y"], 0, self.h - 1)
            # slight random drift
            s["vx"] += random.uniform(-0.02, 0.02)
            s["vy"] += random.uniform(-0.02, 0.02)
            s["vx"] = clamp(s["vx"], -0.5, 0.5)
            s["vy"] = clamp(s["vy"], -0.5, 0.5)

    def draw(self, stdscr):
        step = 2 if self.w > 150 else 1
        for y in range(0, self.h, step):
            for x in range(0, self.w, step):
                d1, d2 = 1e9, 1e9
                nearest = 0
                for i, s in enumerate(self.seeds):
                    dx = x - s["x"]
                    dy = (y - s["y"]) * 2  # aspect correction
                    d = dx * dx + dy * dy
                    if d < d1:
                        d2, d1, nearest = d1, d, i
                    elif d < d2:
                        d2 = d
                edge = math.sqrt(d2) - math.sqrt(d1) if d1 < 1e8 else 999
                if edge < 1.2:
                    attr = curses.color_pair(7) | curses.A_BOLD
                    ch = "\u00b7"
                else:
                    ci = self.seeds[nearest]["color"]
                    if self.has256:
                        attr = curses.color_pair(50 + ci)
                    else:
                        attr = curses.color_pair(1 + ci % 7)
                    ch = "\u2588"
                try:
                    stdscr.addch(y, x, ch, attr)
                    if step == 2 and x + 1 < self.w:
                        stdscr.addch(y, x + 1, ch, attr)
                except curses.error:
                    pass


# ---------------------------------------------------------------------------
# Main loop
# ---------------------------------------------------------------------------

def draw_status_bar(stdscr, h, w, anim_name, idx, total, paused):
    bar = f" [{idx+1}/{total}] {anim_name}"
    controls = " \u2190/\u2192:switch  1-0:jump  Space:pause  r:reset  q:quit "
    if paused:
        bar += "  [PAUSED]"
    pad = w - len(bar) - len(controls)
    if pad < 1:
        controls = ""
        pad = w - len(bar)
    line = bar + " " * max(pad, 0) + controls
    line = line[:w]
    try:
        stdscr.addstr(h - 1, 0, line, curses.color_pair(0) | curses.A_REVERSE)
    except curses.error:
        pass


def main(stdscr):
    curses.curs_set(0)
    stdscr.nodelay(True)
    stdscr.timeout(33)  # ~30 fps
    has256 = init_colors(stdscr)

    h, w = stdscr.getmaxyx()
    # reserve last row for status
    ah = h - 1

    animations = [
        MatrixRain(ah, w, has256),
        Starfield(ah, w, has256),
        Fireworks(ah, w, has256),
        GameOfLife(ah, w, has256),
        PlasmaWaves(ah, w, has256),
        MazeGenerator(ah, w, has256),
        Spirograph(ah, w, has256),
        RaindropRipples(ah, w, has256),
        LissajousWeaver(ah, w, has256),
        VoronoiLandscape(ah, w, has256),
    ]
    current = 0
    paused = False

    while True:
        key = stdscr.getch()
        if key == ord("q"):
            break
        elif key == curses.KEY_RIGHT:
            current = (current + 1) % len(animations)
        elif key == curses.KEY_LEFT:
            current = (current - 1) % len(animations)
        elif ord("1") <= key <= ord("9"):
            current = key - ord("1")
        elif key == ord("0"):
            current = 9
        elif key == ord(" "):
            paused = not paused
        elif key == ord("r"):
            animations[current].reset()
        elif key == curses.KEY_RESIZE:
            h, w = stdscr.getmaxyx()
            ah = h - 1
            for a in animations:
                a.resize(ah, w)

        # check for resize even without KEY_RESIZE
        nh, nw = stdscr.getmaxyx()
        if nh != h or nw != w:
            h, w = nh, nw
            ah = h - 1
            for a in animations:
                a.resize(ah, w)

        if not paused:
            animations[current].update()

        stdscr.erase()
        animations[current].draw(stdscr)
        draw_status_bar(stdscr, h, w, animations[current].name, current, len(animations), paused)
        stdscr.refresh()


if __name__ == "__main__":
    curses.wrapper(main)
