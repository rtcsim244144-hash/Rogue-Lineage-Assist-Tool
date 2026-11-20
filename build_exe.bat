@echo off
setlocal
cd /d "%~dp0"
echo ==============================================
echo   Cooldown Indicator - build the .exe (Nuitka)
echo ==============================================
echo   Nuitka turns the Python code into C and compiles it: the exe starts faster and uses less CPU
echo   than a PyInstaller exe. The FIRST build takes several minutes (it also downloads a C compiler once).
echo   Use  build_exe_pyinstaller.bat  if you want the old way (fast to build, slower to run).
echo.
rem  By default the exe does NOT ask for administrator rights. If the game or the hotkeys need it (e.g. the game runs as administrator), build with:
rem      build_exe.bat admin
set ADMINARG=
if /i "%~1"=="admin" set ADMINARG=--windows-uac-admin

rem Nuitka does not work with the newest Python versions (3.15 keeps Tcl inside a zip it can't read): prefer 3.13, 3.14, 3.12, 3.11.
set PY=
for %%V in (3.13 3.14 3.12 3.11) do if not defined PY (py -%%V -c "import sys" >nul 2>nul && set PY=py -%%V)
if not defined PY set PY=python
echo Using: %PY%
%PY% --version

where python >nul 2>nul
if errorlevel 1 (
  echo Python is not installed or not in PATH.
  echo Install it from https://www.python.org/downloads/ and tick "Add python.exe to PATH".
  pause
  exit /b 1
)

echo [1/3] Installing the build tools...
%PY% -m pip install --upgrade pip
%PY% -m pip install -r requirements.txt nuitka
if errorlevel 1 (
  echo pip failed - check your internet connection.
  pause
  exit /b 1
)
rem (zstandard makes the exe a bit smaller but needs a C compiler to install on new Python versions: it is optional, so a failure here is fine)
%PY% -m pip install zstandard >nul 2>nul

rem The Manufaktur font: any file called *anufaktur*.ttf / .otf in this folder is packed INSIDE the exe.
set FONTARG=
for %%F in (*anufaktur*.ttf *anufaktur*.otf) do set FONTARG=--include-data-files="%%F=%%F"
for %%F in (*inzel*.ttf *inzel*.otf) do set FONTARG=%FONTARG% --include-data-files="%%F=%%F"
if defined FONTARG (
  echo [2/3] Font found - it will be packed into the exe.
) else (
  echo [2/3] No Manufaktur font in this folder - the exe will use Segoe UI.
  echo       ^(Put Manufaktur.ttf next to this file and build again to pack it in.^)
)

rem Nuitka sometimes can't find Python's Tcl/Tk folders by itself: ask Python where they are and tell Nuitka.
set TCLARG=
set TCLDIR=
set TKDIR=
for /f "delims=" %%I in ('%PY% find_tcl.py 2^>nul') do (if not defined TCLDIR (set "TCLDIR=%%I") else set "TKDIR=%%I")
if not defined TKDIR (
  echo Could not find Python's Tcl/Tk files ^(tkinter missing?^). Install Python from python.org and tick "tcl/tk and IDLE".
  pause
  exit /b 1
)
if not exist "%TCLDIR%\init.tcl" (
  echo The Tcl folder %TCLDIR% has no init.tcl - install Python from python.org ^(tick "tcl/tk and IDLE"^) and run this again.
  pause
  exit /b 1
)
set TCLARG=--tcl-library-dir="%TCLDIR%" --tk-library-dir="%TKDIR%"

echo [3/3] Building... this takes a while the first time. Do not close this window.
set NUITKA_ARGS=--onefile --assume-yes-for-downloads --windows-console-mode=disable %ADMINARG% ^
  --enable-plugin=tk-inter %TCLARG% --windows-icon-from-ico=CooldownIndicator.ico %FONTARG% ^
  --include-module=PIL._tkinter_finder --include-module=mss.windows --include-module=pyaudiowpatch ^
  --lto=no --output-dir=dist --output-filename="Rogue Lineage Assist Tool.exe"
rem Compressed exe first (the small one for users). Compressing needs a lot of memory: if the PC runs out, it is built again without compression (bigger exe).
%PY% -m nuitka %NUITKA_ARGS% CooldownIndicator.py
if not errorlevel 1 goto built
echo.
echo The compressed build failed ^(probably not enough memory^). Building again WITHOUT compression - the exe will be bigger.
echo Tip for a small exe: close other programs, or raise Windows virtual memory, and run this again.
if exist dist rmdir /s /q dist
if exist CooldownIndicator.onefile-build rmdir /s /q CooldownIndicator.onefile-build
%PY% -m nuitka %NUITKA_ARGS% --onefile-no-compression CooldownIndicator.py
if errorlevel 1 (
  echo.
  echo The build failed - scroll up for the error.
  pause
  exit /b 1
)
:built
echo.
echo Done:  %~dp0dist\Rogue Lineage Assist Tool.exe
if defined ADMINARG (echo ^(It asks for administrator rights on start.^)) else (echo ^(Built WITHOUT the administrator request. Use  build_exe.bat admin  if the hotkeys don't work in the game.^))
pause
