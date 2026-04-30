# Goblins

A tiny Codex skill that releases a small animated 2D desktop goblin onto your screen.

It wanders. It stares. It has somewhere to be, probably.

## What It Does

- Installs as a standalone Codex skill named `goblins`.
- Starts a transparent, always-on-top desktop companion.
- Uses a native Swift/Cocoa overlay on macOS.
- Falls back to a Python/Tk runtime outside macOS.
- Supports optional generated sprite sheets for a fancier character.
- Keeps runtime state in `~/.codex/goblins/`.

## Install

From this repo:

```bash
ln -s "$(pwd)/goblins" ~/.codex/skills/goblins
```

Restart Codex so the skill list reloads.

Then invoke:

```text
/goblins
```

or ask Codex:

```text
spawn a goblin on my desktop
```

## Manual Commands

Start:

```bash
cd goblins
python3 scripts/goblin_desktop.py start
```

Stop:

```bash
cd goblins
python3 scripts/goblin_desktop.py stop
```

Status:

```bash
cd goblins
python3 scripts/goblin_desktop.py status
```

Restart:

```bash
cd goblins
python3 scripts/goblin_desktop.py restart
```

## Custom Sprite Sheet

The runtime prefers a PNG sprite sheet if one has been installed:

```bash
cd goblins
python3 scripts/goblin_desktop.py spritesheet /path/to/goblin_spritesheet.png
python3 scripts/goblin_desktop.py restart
```

Sprite sheet format:

- PNG
- 128x128 frames
- Regular grid
- One horizontal row of 8 frames is ideal

If no sprite sheet exists, the runtime draws a procedural character.

## Requirements

macOS:

- `python3`
- Swift compiler (`swiftc`)

Other platforms:

- `python3`
- Tkinter support in the local Python build

No npm install, Electron app, or PyPI package is required.

## Repo Layout

```text
goblins/
├── SKILL.md
├── agents/
│   └── openai.yaml
├── assets/
└── scripts/
    ├── GoblinDesktop.swift
    └── goblin_desktop.py
```

## Notes

This is intentionally small and silly. The skill owns the Codex workflow; the bundled runtime owns the actual desktop animation.

If it appears in the wrong place, behaving suspiciously, or making strong eye contact, that is normal desktop companion behavior.
