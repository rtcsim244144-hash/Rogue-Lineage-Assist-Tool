# Rogue Lineage Assist Tool

A free, open-source overlay and helper for **Rogue Lineage** (Roblox) on Windows. It reads what is on your screen and keyboard/mouse input, and shows cooldowns and counters on top of the game. It does not touch the game's files or memory.

> Not affiliated with Roblox or the Rogue Lineage developers. Use at your own risk.

## What it does

- **Cooldown boxes** on your hotbar: moves, M2 / snap spells, inventory items, buffs (Soul Berserk, Awakened, Bloodline, Flood, Galvanize and more), shards (Lapidarist), songs (Cadence) and potions.
- **Mana overlay:** cast marks, mana % and dash / PB coins.
- **Class and race pages:** per-profile options for Fischeran dodges, Whisperer double jump, Dragon Sage / Faceless dashes and others.
- **Profiles:** save, share and import profiles with a share code. Default profiles for most classes are included.
- **Auto Bard:** plays the song minigame while a song is being played. While it runs, **"Auto Bard is Active."** is always shown on screen. It cannot be hidden or moved.
- **KDA counters:** Grip / Death / Assist / Knocked counters. Left click adds, right click subtracts. You can move and resize them.
- **Instant Menu:** press a key (default `[`) and the mouse jumps to the game's Menu button and clicks it.
- **Alchemy / Smith** and **Snap Training** automation.
- **Checklists** next to the mana bar and a **Gank Ping** that sends a screenshot to a Discord webhook.
- **Automatic updates** from this repo's releases (nothing installs without a click).

## Install

1. Open the **Releases** page of this repo and download `Rogue.Lineage.Assist.Tool.exe`.
2. Run it. It asks for administrator rights because it needs to watch keys and clicks.
3. Start Rogue Lineage (**1920x1080** is what it was made on; other sizes and windowed mode may need adjusting).
4. Press **F2** to find your hotbar and use the Mana Overlay tab to find your mana bar.

Settings are saved next to the exe in `cooldown_indicator_config.json`.

## Run from source

```
pip install -r requirements.txt
python CooldownIndicator.py
```

Needs Python 3.10+ on Windows. `opencv-python` is only needed for Auto Bard and Instant Menu.

## Build the exe

Double-click `build_exe.bat` (see `README_BUILD.txt`). The exe appears in `dist\`.

## Known limits

- Made and tested at **1920x1080**. Windowed mode and other resolutions are only partly supported.
- Auto Bard's circle detection is tuned for 1080p fullscreen.
- Cooldown timings are set by hand. If the game changes, edit them in the tool.

## Safety and fair use

- The tool only **reads the screen** and **sends normal mouse / keyboard input**. It does not read or change game memory.
- Auto Bard is added with the knowledge of a game moderator and always shows an on-screen notice while it is running.
- Roblox and game rules can change. You are responsible for how you use this.

## Reporting problems

Open an **Issue** on this repo. Please include your screen resolution, whether the game is windowed or fullscreen, what you did, and a screenshot or short video if you can.

## Credits and third-party software

Built with Python, tkinter, [mss](https://github.com/BoboTiG/python-mss), [NumPy](https://numpy.org), [Pillow](https://python-pillow.org), [OpenCV](https://opencv.org), [keyboard](https://github.com/boppreh/keyboard) and [PyAudioWPatch](https://github.com/s0d3s/PyAudioWPatch). Each keeps its own license. Game names and artwork belong to their owners.

## License

Released under the **MIT License** (see `LICENSE`).
