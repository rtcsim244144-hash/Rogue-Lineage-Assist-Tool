BUILD THE EXE (Windows)
1. Put Manufaktur.ttf in this folder (optional - without it the exe uses Segoe UI).
2. Double-click build_exe.bat.
3. Your exe: dist\Rogue Lineage Assist Tool.exe  (one file; the GUI art from scroom_assets.py and the font are inside it)

The exe asks for administrator rights when it starts (needed for the key / click hooks).
Its settings are saved NEXT TO the exe (cooldown_indicator_config.json, mana_overlay_custom.png, decorations\).

No Windows PC handy? Upload this folder to a GitHub repo, open the Actions tab -> "Build exe" -> Run workflow;
the exe appears under Artifacts. Pushing a tag like v1.0 also attaches it to a Release.


AUTOMATIC UPDATES (for exe users)
The macro has an "Updates" part in Settings: [Check for updates] and [Update now]. Discord links don't work
for this (they expire). GitHub is free and permanent: version.txt + the script live in a repo, the exe goes
on a GitHub "Release" (a normal upload is limited to 25 MB, a Release to 2 GB).

ONE-TIME SETUP
1. github.com > sign up > Settings > Password and authentication > turn on two-factor authentication.
   (Whoever controls your repo controls what everyone's macro installs.)
2. New repository: name it e.g. "cooldown-macro", set it PUBLIC, tick "Add a README", Create.
3. Open CooldownIndicator.py in a text editor and set (YOUR_NAME / YOUR_REPO = your GitHub name / repo name):
       UPDATE_BASE_URL = "https://raw.githubusercontent.com/YOUR_NAME/YOUR_REPO/main/"
4. Build the exe (build_exe.bat) and send THAT exe to everyone. This first exe must already contain the link,
   because older exes without it can't update themselves.

EVERY NEW VERSION
1. In CooldownIndicator.py raise the number:   APP_VERSION = "1.1.0"
2. Double-click build_exe.bat  (makes dist\Rogue Lineage Assist Tool.exe).
3. Open a command prompt in this folder and run:   python make_update_files.py "what changed"
   (needs Python installed; it makes the folder  update_folder  with version.txt + CooldownIndicator.py)
4. On your repo page: Add file > Upload files > drag in the files from  update_folder  (version.txt and
   CooldownIndicator.py) > Commit. (Replace the old ones.)
5. On your repo page: Releases > "Create a new release" > Tag: v1.1.0 (same as APP_VERSION) > drag
   dist\Rogue Lineage Assist Tool.exe into the files box > Publish release.
6. Post "new version" in your Discord. Everyone presses Settings > Check for updates > Update now > Restart now
   (their macro also looks by itself when it starts). GitHub can take a few minutes to refresh.

IMPORTANT: do steps 4 and 5 with the exe you built in step 2 - version.txt contains that exe's checksum and the
macro rejects any other file.

SAFETY / NOTES
- Nothing installs without a click. The file's checksum is checked first; a bad or half-finished download is
  rejected and the current version stays.
- The old exe is kept as the old exe name + .old until the next start. Settings, profiles and pictures
  (next to the exe) are never touched. The exe asks for administrator rights again after a restart (normal).
- If you also share the plain script, script users update the same way (they get CooldownIndicator.py, the old
  one is kept as .bak).

Auto Bard (Songs) needs opencv-python: it is in requirements.txt and bundled by build_exe.bat (--hidden-import cv2).

The exe is called "Rogue Lineage Assist Tool.exe". GitHub turns the spaces of an uploaded release file into dots, so on the release page it
is  Rogue.Lineage.Assist.Tool.exe  (that is the name the update link uses). Users on the old CooldownIndicator.exe get the new exe
under their old file name when they update - nothing breaks.
