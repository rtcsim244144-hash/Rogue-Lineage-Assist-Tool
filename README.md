# Rogue Lineage Assist Tool

A free, open-source overlay and helper for **Rogue Lineage** (Roblox) on Windows (Linux and Mac builds also exist, without House). It reads what is on your screen and keyboard/mouse input, and shows cooldowns and counters on top of the game. It does not touch the game's files or memory.

> Not affiliated with Roblox or the Rogue Lineage developers. Use at your own risk.

## What it does

- **Cooldown boxes** on your hotbar: moves, M2 / snap spells, inventory items, buffs (Soul Berserk, Awakened, Bloodline, Flood, Galvanize and more), shards (Lapidarist), songs (Cadence) and potions.
- **Base cooldowns filled in for you:** type a known move name (Action Surge, Pommel Strike, a weapon ...) and its cooldown boxes fill themselves. Numbers you type are never overwritten. Snap Gelidus (3 s) and Snap Gate (6.5 s) show their fixed cooldowns.
- **Mana overlay:** cast marks, mana % and dash / PB coins. Spells the tool knows (Viribus, Ignis, Gate, Snarvindur ...) get their **mana marks made automatically**, locked to the spell's key (they follow if you change the keybind). Spells kept in the inventory get their mark on their inventory card.
- **House (Windows):** make a house with friends (Leader / Officers / Members, one-time invite codes) and see your housemates' **health, buffs and potion timers** on your screen. See "House" below.
- **Class and race pages:** per-profile options for Fischeran dodges, Whisperer double jump, Dragon Sage / Faceless dashes and others.
- **Profiles:** save, share and import profiles with a share code. Default profiles for most classes are included.
- **Keybinds:** hotbar, gate and potion keys can be set to a key or to **Ctrl + a key**.
- **Auto Bard:** plays the song minigame while a song is being played. While it runs, **"Auto Bard is Active."** is always shown on screen. It cannot be hidden or moved.
- **KDA counters:** Grip / Death / Assist / Knocked counters. Left click adds, right click subtracts. You can move and resize them.
- **Instant Menu:** press a key (default `[`) and the mouse jumps to the game's Menu button and clicks it.
- **Alchemy / Smith** and **Snap Training** automation.
- **Checklists** next to the mana bar and a **Gank Ping** that sends a screenshot to a Discord webhook.
- **What's New?** window in the tool (read from this repo's release notes) and an **Update Available** pop-up that lists what changed. Nothing installs without a click.

## House (housemate health bars)

Extras > House Stuff. Start a house, press "Make invite code" and send it; your friend types it under "Join a house".

- Housemates' health, buffs and potion timers show above your mana bar while your own health bar is on the screen. A housemate whose bar is not found is hidden.
- **No server needed.** The house talks through free **public MQTT brokers** (`broker.emqx.io`, `broker.hivemq.com`, `mqtt.eclipseprojects.io`). Everything is encrypted with the house's own key, but a public broker can still see your **IP address** and that you are connected. Using a VPN is recommended. The tool shows this notice the first time you open House Setup.
- The person who made an invite code must be online with the tool open when the friend enters it.
- You can run your own server instead (folder `housemate_server`, see `HOUSEMATE_SERVER.txt`) and paste its address in House Setup > "Server Address (Optional)".
- The house lives in each member's own config file next to the exe. Roles are obeyed by the members' tools: a house is for friends, a modified tool could cheat.
- Housemate names use the Cinzel font (SIL Open Font License, `Cinzel-OFL.txt`).

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

Double-click `build_exe.bat` (see `README_BUILD.txt`). The exe appears in `dist\`. Put `Manufaktur.ttf` and `Cinzel-Bold.ttf` next to it to have them packed into the exe.

## Known limits

- Made and tested at **1920x1080**. Windowed mode and other resolutions are only partly supported.
- Auto Bard's circle detection is tuned for 1080p fullscreen.
- Base cooldowns are hardcoded from the default profiles. If the game changes, edit the numbers in the tool.
- House uses public MQTT brokers (see above): they are free services with no promise to stay up.

## Safety and fair use

- The tool only **reads the screen** and **sends normal mouse / keyboard input**. It does not read or change game memory.
- Auto Bard is added with the knowledge of a game moderator and always shows an on-screen notice while it is running.
- Roblox and game rules can change. You are responsible for how you use this.

## Reporting problems

Open an **Issue** on this repo. Please include your screen resolution, whether the game is windowed or fullscreen, what you did, and a screenshot or short video if you can.

## Credits and third-party software

Fonts: Cinzel (SIL OFL, see `Cinzel-OFL.txt`). Built with Python, tkinter, [mss](https://github.com/BoboTiG/python-mss), [NumPy](https://numpy.org), [Pillow](https://python-pillow.org), [OpenCV](https://opencv.org), [keyboard](https://github.com/boppreh/keyboard) and [PyAudioWPatch](https://github.com/s0d3s/PyAudioWPatch). Each keeps its own license. Game names and artwork belong to their owners.

## License

Released under the **MIT License** (see `LICENSE`).
