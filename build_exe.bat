@echo off
setlocal
cd /d "%~dp0"
echo ==============================================
echo   Cooldown Indicator - build the .exe
echo ==============================================
echo.

where python >nul 2>nul
if errorlevel 1 (
  echo Python is not installed or not in PATH.
  echo Install it from https://www.python.org/downloads/ and tick "Add python.exe to PATH".
  pause
  exit /b 1
)

echo [1/3] Installing the build tools...
python -m pip install --upgrade pip
python -m pip install -r requirements.txt pyinstaller
if errorlevel 1 (
  echo pip failed - check your internet connection.
  pause
  exit /b 1
)

rem The Manufaktur font: any file called *anufaktur*.ttf / .otf in this folder is packed INSIDE the exe.
set FONTARG=
for %%F in (*anufaktur*.ttf *anufaktur*.otf) do set FONTARG=--add-data "%%F;."
if defined FONTARG (
  echo [2/3] Font found - it will be packed into the exe.
) else (
  echo [2/3] No Manufaktur font in this folder - the exe will use Segoe UI. 
  echo       ^(Put Manufaktur.ttf next to this file and build again to pack it in.^)
)

echo [3/3] Building... this takes a minute.
python -m PyInstaller --noconfirm --clean --onefile --windowed --uac-admin ^
  --name "Rogue Lineage Assist Tool" --icon CooldownIndicator.ico %FONTARG% ^
  --hidden-import PIL._tkinter_finder --hidden-import mss.windows --hidden-import pyaudiowpatch --hidden-import cv2 ^
  CooldownIndicator.py
if errorlevel 1 (
  echo.
  echo The build failed - scroll up for the error.
  pause
  exit /b 1
)

echo.
echo Done:  %~dp0dist\Rogue Lineage Assist Tool.exe
echo (It asks for administrator rights on start - that is needed for the key / click hooks.)
pause
