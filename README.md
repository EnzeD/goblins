# Goblins

Summon one tiny desktop goblin. It roams. It loiters. It has no calendar invite.

This is a standalone Codex skill that launches a little animated 2D companion onto your desktop when you invoke:

```text
/goblins
```

No Electron tavern. No npm cauldron. Just a small bundled runtime and one suspicious little guy.

## Goblin Capabilities

- Skitters around your desktop in a transparent always-on-top window.
- Ignores your mouse, as all respectable desktop goblins should.
- Uses a native Swift/Cocoa overlay on macOS.
- Falls back to Python/Tk outside macOS, if your Python has Tkinter.
- Can wear a custom generated sprite sheet if you give it one.
- Stores its tiny administrative paperwork in `~/.codex/goblins/`.

## Install The Goblin

Clone the repo, then from the repo root:

```bash
ln -s "$(pwd)/goblins" ~/.codex/skills/goblins
```

Restart Codex so it notices the new resident.

Then type:

```text
/goblins
```

or use the formal incantation:

```text
spawn a goblin on my desktop
```

## Goblin Wrangler Commands

Start the goblin:

```bash
cd goblins
python3 scripts/goblin_desktop.py start
```

Stop the goblin:

```bash
cd goblins
python3 scripts/goblin_desktop.py stop
```

Ask whether the goblin is currently employed:

```bash
cd goblins
python3 scripts/goblin_desktop.py status
```

Restart the goblin after it has reconsidered its life choices:

```bash
cd goblins
python3 scripts/goblin_desktop.py restart
```

## Custom Goblin Attire

The runtime will use a PNG sprite sheet if you install one:

```bash
cd goblins
python3 scripts/goblin_desktop.py spritesheet /path/to/goblin_spritesheet.png
python3 scripts/goblin_desktop.py restart
```

Sprite sheet rules, because even goblins need boundaries:

- PNG
- 128x128 frames
- Regular grid
- One horizontal row of 8 frames is ideal

If no sprite sheet is installed, the runtime draws its own procedural goblin. This is not a punishment. It is a lifestyle.

## Requirements

macOS:

- `python3`
- Swift compiler (`swiftc`)

Other platforms:

- `python3`
- Tkinter support in the local Python build

No npm install, Electron app, or PyPI package is required. The goblin travels light.

## Burrow Layout

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

## Fine Print

This project is intentionally small, silly, and mildly alarming. The Codex skill handles the invocation workflow; the bundled runtime handles the desktop mischief.

If the goblin appears in the wrong place, stares at your draft PR, or drifts across an important button, that is expected behavior.
