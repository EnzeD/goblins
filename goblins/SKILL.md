---
name: goblins
description: Spawn, stop, or manage a standalone animated 2D desktop goblin companion. Use when the user invokes `/goblins`, asks for a goblin on their desktop, wants a roaming animated desktop character, or asks to stop/status/restart the goblin process.
---

# Goblins

## Quick Start

When the user asks to spawn the goblin, including `/goblins`, run the bundled runtime from this skill directory:

```bash
python3 scripts/goblin_desktop.py start
```

When the user asks to stop it:

```bash
python3 scripts/goblin_desktop.py stop
```

For status:

```bash
python3 scripts/goblin_desktop.py status
```

For restart:

```bash
python3 scripts/goblin_desktop.py restart
```

To install a generated spritesheet:

```bash
python3 scripts/goblin_desktop.py spritesheet /path/to/goblin_spritesheet.png
python3 scripts/goblin_desktop.py restart
```

## Runtime Behavior

- Use only the bundled `scripts/goblin_desktop.py`; it has no third-party Python dependencies.
- On macOS, the manager compiles and launches the bundled native Swift/Cocoa overlay at first run. This requires `python3` and the macOS Swift compiler, but no npm, Electron, PyPI packages, or external assets.
- On non-macOS, the manager falls back to its Python/Tk runtime. If Tkinter is unavailable, report that the local Python build cannot display the fallback GUI.
- The script launches a detached local GUI process and stores its PID/log under `~/.codex/goblins/`.
- Re-running `start` should not create duplicates; use `restart` when the user wants a fresh goblin.
- The runtime first looks for `~/.codex/goblins/goblin_spritesheet.png`, then `assets/goblin_spritesheet.png`, then falls back to its procedural goblin drawing.
- A spritesheet must be a PNG containing 128x128 frames in a regular grid. One row of 8 frames works well.

## Optional Image Gen Spritesheet

If the user asks for a custom, generated, polished, or image-based goblin, use `$imagegen` to create a PNG spritesheet before launching or restarting the runtime.

Use a prompt like:

```text
Use case: stylized-concept
Asset type: 2D game sprite sheet for a desktop companion
Primary request: Create an 8-frame sprite sheet of one cute mischievous fantasy goblin walking in place.
Style: polished 2D game sprite, clean silhouette, readable at 128x128 pixels, expressive face, green skin, simple purple tunic.
Layout: exactly 8 square animation frames in one horizontal row, each frame 128x128, total image 1024x128.
Background: perfectly flat solid #ff00ff chroma-key background, no shadows, no gradients, no texture.
Constraints: same character in every frame, centered in each cell, no text, no watermark, no frame borders, no extra characters.
```

After generation, remove the chroma-key background with the Image Gen skill's transparent-image workflow if needed, save the final PNG locally, install it with the `spritesheet` command, then restart the goblin.

## Notes For Codex

If the user types `/goblins` or says "spawn goblins", do the start action immediately and briefly report whether it launched. Do not open or explain the script unless launch fails.
