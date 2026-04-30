#!/usr/bin/env python3
"""Spawn a small animated goblin that roams around the desktop."""

from __future__ import annotations

import argparse
import math
import os
import random
import shutil
import signal
import subprocess
import sys
import time
from pathlib import Path


APP_DIR = Path.home() / ".codex" / "goblins"
PID_FILE = APP_DIR / "goblin.pid"
LOG_FILE = APP_DIR / "goblin.log"
USER_SPRITESHEET = APP_DIR / "goblin_spritesheet.png"
BUNDLED_SPRITESHEET = Path(__file__).resolve().parents[1] / "assets" / "goblin_spritesheet.png"
SWIFT_SOURCE = Path(__file__).resolve().with_name("GoblinDesktop.swift")
SWIFT_BINARY = APP_DIR / "GoblinDesktop"
SPRITE_SIZE = 128
FRAME_MS = 33


def ensure_app_dir() -> None:
    APP_DIR.mkdir(parents=True, exist_ok=True)


def read_pid() -> int | None:
    try:
        return int(PID_FILE.read_text(encoding="utf-8").strip())
    except (FileNotFoundError, ValueError):
        return None


def process_alive(pid: int | None) -> bool:
    if not pid:
        return False
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    return True


def write_pid(pid: int) -> None:
    ensure_app_dir()
    PID_FILE.write_text(f"{pid}\n", encoding="utf-8")


def clear_pid() -> None:
    try:
        PID_FILE.unlink()
    except FileNotFoundError:
        pass


def swift_available() -> bool:
    return sys.platform == "darwin" and shutil.which("swiftc") is not None


def ensure_swift_binary() -> Path | None:
    if not swift_available():
        return None
    ensure_app_dir()
    source_mtime = SWIFT_SOURCE.stat().st_mtime if SWIFT_SOURCE.exists() else 0
    binary_mtime = SWIFT_BINARY.stat().st_mtime if SWIFT_BINARY.exists() else 0
    if SWIFT_BINARY.exists() and binary_mtime >= source_mtime:
        return SWIFT_BINARY

    compile_cmd = [
        "swiftc",
        str(SWIFT_SOURCE),
        "-o",
        str(SWIFT_BINARY),
        "-framework",
        "Cocoa",
    ]
    result = subprocess.run(compile_cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(result.stderr.strip() or "failed to compile Swift goblin runtime", file=sys.stderr)
        return None
    return SWIFT_BINARY


def runtime_command() -> list[str] | None:
    swift_binary = ensure_swift_binary()
    if swift_binary is not None:
        return [str(swift_binary)]
    return [sys.executable, str(Path(__file__).resolve()), "run"]


def start_background() -> int:
    ensure_app_dir()
    current = read_pid()
    if process_alive(current):
        print(f"goblin already running with pid {current}")
        return 0

    command = runtime_command()
    if command is None:
        print("no usable goblin runtime found", file=sys.stderr)
        return 1

    with LOG_FILE.open("ab") as log:
        proc = subprocess.Popen(
            command,
            stdin=subprocess.DEVNULL,
            stdout=log,
            stderr=log,
            start_new_session=True,
            close_fds=True,
        )
    write_pid(proc.pid)
    print(f"spawned goblin with pid {proc.pid}")
    return 0


def stop_background() -> int:
    pid = read_pid()
    if not process_alive(pid):
        clear_pid()
        print("goblin is not running")
        return 0

    assert pid is not None
    os.kill(pid, signal.SIGTERM)
    deadline = time.time() + 3
    while time.time() < deadline:
        if not process_alive(pid):
            clear_pid()
            print("stopped goblin")
            return 0
        time.sleep(0.1)

    try:
        os.kill(pid, signal.SIGKILL)
    except ProcessLookupError:
        pass
    clear_pid()
    print("stopped goblin")
    return 0


def status() -> int:
    pid = read_pid()
    if process_alive(pid):
        print(f"goblin running with pid {pid}")
    else:
        clear_pid()
        print("goblin is not running")
    return 0


def install_spritesheet(path: str) -> int:
    source = Path(path).expanduser().resolve()
    if not source.exists():
        print(f"spritesheet not found: {source}", file=sys.stderr)
        return 1
    if source.suffix.lower() != ".png":
        print("spritesheet must be a PNG file", file=sys.stderr)
        return 1
    ensure_app_dir()
    shutil.copy2(source, USER_SPRITESHEET)
    print(f"installed spritesheet at {USER_SPRITESHEET}")
    return 0


def find_spritesheet() -> Path | None:
    if USER_SPRITESHEET.exists():
        return USER_SPRITESHEET
    if BUNDLED_SPRITESHEET.exists():
        return BUNDLED_SPRITESHEET
    return None


def load_sprite_frames(tk, size: int) -> list:
    spritesheet = find_spritesheet()
    if spritesheet is None:
        return []
    try:
        sheet = tk.PhotoImage(file=str(spritesheet))
        sheet_w = sheet.width()
        sheet_h = sheet.height()
        if sheet_w < size or sheet_h < size:
            print(f"spritesheet too small: {spritesheet}", file=sys.stderr)
            return []

        cols = sheet_w // size
        rows = sheet_h // size
        frames = []
        for row in range(rows):
            for col in range(cols):
                frame = tk.PhotoImage(width=size, height=size)
                x1 = col * size
                y1 = row * size
                frame.tk.call(frame, "copy", sheet, "-from", x1, y1, x1 + size, y1 + size, "-to", 0, 0)
                frames.append(frame)
        return frames
    except Exception as exc:
        print(f"could not load spritesheet {spritesheet}: {exc}", file=sys.stderr)
        return []


class Goblin:
    def __init__(self, root, canvas, frames):
        self.root = root
        self.canvas = canvas
        self.frames = frames
        self.screen_w = max(root.winfo_screenwidth(), SPRITE_SIZE)
        self.screen_h = max(root.winfo_screenheight(), SPRITE_SIZE)
        self.x = random.randint(0, max(0, self.screen_w - SPRITE_SIZE))
        self.y = random.randint(80, max(80, self.screen_h - SPRITE_SIZE - 80))
        self.vx = random.choice([-1, 1]) * random.uniform(1.2, 2.5)
        self.vy = random.uniform(-0.45, 0.45)
        self.phase = 0.0
        self.target_change_at = time.time() + random.uniform(3, 7)
        self.items: list[int] = []

    def maybe_change_direction(self) -> None:
        now = time.time()
        if now < self.target_change_at:
            return
        self.target_change_at = now + random.uniform(3, 8)
        self.vx = random.choice([-1, 1]) * random.uniform(1.0, 2.8)
        self.vy = random.uniform(-0.65, 0.65)

    def update_position(self) -> None:
        self.maybe_change_direction()
        self.x += self.vx
        self.y += self.vy + math.sin(self.phase * 0.7) * 0.18

        max_x = self.screen_w - SPRITE_SIZE
        max_y = self.screen_h - SPRITE_SIZE - 24
        if self.x <= 0 or self.x >= max_x:
            self.vx *= -1
            self.x = min(max(self.x, 0), max_x)
        if self.y <= 40 or self.y >= max_y:
            self.vy *= -1
            self.y = min(max(self.y, 40), max_y)

        self.root.geometry(f"{SPRITE_SIZE}x{SPRITE_SIZE}+{int(self.x)}+{int(self.y)}")
        self.phase += 0.16

    def draw(self) -> None:
        self.canvas.delete("all")
        if self.frames:
            frame = self.frames[int(self.phase * 4) % len(self.frames)]
            self.canvas.create_image(SPRITE_SIZE / 2, SPRITE_SIZE / 2, image=frame)
            return

        walk = math.sin(self.phase)
        bob = math.sin(self.phase * 2) * 3
        facing = 1 if self.vx >= 0 else -1
        cx = SPRITE_SIZE / 2
        cy = SPRITE_SIZE / 2 + bob

        # Shadow
        self.canvas.create_oval(28, 121, 100, 131, fill="#1b1f18", outline="")

        # Ears
        self.poly(
            [(39, 40), (8, 28), (32, 58)],
            fill="#6fa443",
            outline="#20351f",
            width=2,
        )
        self.poly(
            [(89, 40), (120, 28), (96, 58)],
            fill="#6fa443",
            outline="#20351f",
            width=2,
        )

        # Body and tunic
        self.canvas.create_oval(42, 58 + bob, 86, 108 + bob, fill="#66733a", outline="#1e2617", width=2)
        self.canvas.create_polygon(
            39,
            76 + bob,
            89,
            76 + bob,
            80,
            111 + bob,
            48,
            111 + bob,
            fill="#5b3f65",
            outline="#211629",
            width=2,
        )
        self.canvas.create_line(64, 77 + bob, 64, 107 + bob, fill="#2a1d31", width=2)

        # Legs
        self.limb(53, 106 + bob, 47 - walk * 7, 122, "#394427")
        self.limb(74, 106 + bob, 81 + walk * 7, 122, "#394427")

        # Arms
        self.limb(45, 75 + bob, 30, 88 + walk * 6, "#6fa443", width=8)
        self.limb(83, 75 + bob, 100, 88 - walk * 6, "#6fa443", width=8)

        # Head
        self.canvas.create_oval(31, 28 + bob, 97, 82 + bob, fill="#79ad47", outline="#20351f", width=3)
        self.canvas.create_oval(38, 48 + bob, 50, 61 + bob, fill="#f0d45b", outline="#1a1a10", width=1)
        self.canvas.create_oval(78, 48 + bob, 90, 61 + bob, fill="#f0d45b", outline="#1a1a10", width=1)
        pupil_shift = 2 * facing
        self.canvas.create_oval(44 + pupil_shift, 52 + bob, 48 + pupil_shift, 58 + bob, fill="#111", outline="")
        self.canvas.create_oval(84 + pupil_shift, 52 + bob, 88 + pupil_shift, 58 + bob, fill="#111", outline="")
        self.canvas.create_polygon(62, 58 + bob, 56, 67 + bob, 69, 67 + bob, fill="#4f7d31", outline="#20351f")
        self.canvas.create_arc(49, 61 + bob, 79, 77 + bob, start=200, extent=140, style="arc", outline="#211", width=2)

        # Teeth
        self.canvas.create_polygon(55, 69 + bob, 59, 69 + bob, 57, 75 + bob, fill="#efe7c2", outline="")
        self.canvas.create_polygon(70, 69 + bob, 74, 69 + bob, 72, 75 + bob, fill="#efe7c2", outline="")

        # Hair tufts
        for offset in (-12, 0, 12):
            self.canvas.create_line(
                cx + offset,
                cy - 42 + bob,
                cx + offset / 2,
                cy - 56 + bob + abs(offset) / 5,
                fill="#242018",
                width=4,
                capstyle="round",
            )

    def limb(self, x1, y1, x2, y2, color, width=9) -> None:
        self.canvas.create_line(x1, y1, x2, y2, fill="#1c2416", width=width + 2, capstyle="round")
        self.canvas.create_line(x1, y1, x2, y2, fill=color, width=width, capstyle="round")

    def poly(self, points, **kwargs) -> None:
        flat = []
        for x, y in points:
            flat.extend((x, y))
        self.canvas.create_polygon(*flat, **kwargs)

    def tick(self) -> None:
        self.update_position()
        self.draw()
        self.root.after(FRAME_MS, self.tick)


def run_gui() -> int:
    try:
        import tkinter as tk
    except Exception as exc:  # pragma: no cover - depends on local Python build
        print(f"Tkinter is required to display the desktop goblin: {exc}", file=sys.stderr)
        return 1

    ensure_app_dir()
    write_pid(os.getpid())

    root = tk.Tk()
    root.title("Goblin")
    root.overrideredirect(True)
    root.resizable(False, False)

    transparent = "#00ff01"
    root.configure(bg=transparent)
    try:
        root.wm_attributes("-topmost", True)
    except tk.TclError:
        pass
    try:
        root.wm_attributes("-transparentcolor", transparent)
    except tk.TclError:
        try:
            root.configure(bg="systemTransparent")
            root.wm_attributes("-transparent", True)
            transparent = "systemTransparent"
        except tk.TclError:
            pass

    canvas = tk.Canvas(
        root,
        width=SPRITE_SIZE,
        height=SPRITE_SIZE,
        bg=transparent,
        highlightthickness=0,
        bd=0,
    )
    canvas.pack(fill="both", expand=True)
    frames = load_sprite_frames(tk, SPRITE_SIZE)

    def shutdown(*_args) -> None:
        clear_pid()
        try:
            root.destroy()
        except tk.TclError:
            pass

    signal.signal(signal.SIGTERM, shutdown)
    signal.signal(signal.SIGINT, shutdown)

    goblin = Goblin(root, canvas, frames)
    root.geometry(f"{SPRITE_SIZE}x{SPRITE_SIZE}+{int(goblin.x)}+{int(goblin.y)}")
    root.after(0, goblin.tick)

    try:
        root.mainloop()
    finally:
        clear_pid()
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Manage the desktop goblin companion.")
    parser.add_argument("command", choices=["start", "run", "stop", "restart", "status", "spritesheet"])
    parser.add_argument("path", nargs="?", help="PNG spritesheet path for the spritesheet command.")
    args = parser.parse_args()

    if args.command == "start":
        return start_background()
    if args.command == "run":
        return run_gui()
    if args.command == "stop":
        return stop_background()
    if args.command == "restart":
        stop_background()
        return start_background()
    if args.command == "status":
        return status()
    if args.command == "spritesheet":
        if not args.path:
            print("usage: goblin_desktop.py spritesheet /path/to/goblin_spritesheet.png", file=sys.stderr)
            return 2
        return install_spritesheet(args.path)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
