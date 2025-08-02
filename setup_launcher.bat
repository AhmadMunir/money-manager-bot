@echo off
REM MonMan Bot - Setup Script for Windows
REM This script sets up the launcher and creates shortcuts

setlocal EnableDelayedExpansion

set SCRIPT_DIR=%~dp0
set LAUNCHER_BAT=%SCRIPT_DIR%monman.bat

echo [INFO] Setting up MonMan Bot Launcher for Windows...

REM Check Python installation
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://python.org
    echo Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
)

echo [SUCCESS] Python found

REM Install dependencies
echo [INFO] Installing launcher dependencies...
pip install -r requirements_launcher.txt
if errorlevel 1 (
    echo [WARNING] Some dependencies may not have installed correctly
    echo This might affect advanced features but basic functionality should work
) else (
    echo [SUCCESS] Dependencies installed
)

REM Create directories
if not exist "logs" mkdir logs
if not exist "config" mkdir config
echo [SUCCESS] Created required directories

REM Create desktop shortcut
set /p create_shortcut="Create desktop shortcut? [y/N]: "
if /i "%create_shortcut%"=="y" (
    set DESKTOP=%USERPROFILE%\Desktop
    set SHORTCUT_NAME=MonMan Bot.lnk
    
    REM Create VBS script to create shortcut
    echo Set oWS = WScript.CreateObject("WScript.Shell"^) > CreateShortcut.vbs
    echo sLinkFile = "%DESKTOP%\%SHORTCUT_NAME%" >> CreateShortcut.vbs
    echo Set oLink = oWS.CreateShortcut(sLinkFile^) >> CreateShortcut.vbs
    echo oLink.TargetPath = "%LAUNCHER_BAT%" >> CreateShortcut.vbs
    echo oLink.WorkingDirectory = "%SCRIPT_DIR%" >> CreateShortcut.vbs
    echo oLink.Description = "MonMan Finance Bot Launcher" >> CreateShortcut.vbs
    echo oLink.Save >> CreateShortcut.vbs
    
    cscript CreateShortcut.vbs >nul
    del CreateShortcut.vbs
    
    echo [SUCCESS] Desktop shortcut created
)

REM Add to PATH (optional)
set /p add_to_path="Add MonMan to system PATH? [y/N]: "
if /i "%add_to_path%"=="y" (
    echo [INFO] Adding to PATH requires administrator privileges
    echo [INFO] You can also add manually: %SCRIPT_DIR%
    
    REM Try to add to user PATH
    for /f "skip=2 tokens=3*" %%a in ('reg query HKCU\Environment /v PATH 2^>nul') do set CURRENT_PATH=%%b
    if not defined CURRENT_PATH set CURRENT_PATH=
    
    echo !CURRENT_PATH! | findstr /C:"%SCRIPT_DIR%" >nul
    if errorlevel 1 (
        if defined CURRENT_PATH (
            set NEW_PATH=!CURRENT_PATH!;%SCRIPT_DIR%
        ) else (
            set NEW_PATH=%SCRIPT_DIR%
        )
        reg add HKCU\Environment /v PATH /d "!NEW_PATH!" /f >nul 2>&1
        if not errorlevel 1 (
            echo [SUCCESS] Added to user PATH
            echo [INFO] Restart command prompt to use 'monman' command globally
        ) else (
            echo [WARNING] Could not add to PATH automatically
            echo [INFO] Add manually: %SCRIPT_DIR%
        )
    ) else (
        echo [INFO] Already in PATH
    )
)

REM Create Windows service (optional, requires NSSM or similar)
set /p create_service="Create Windows service? (requires NSSM) [y/N]: "
if /i "%create_service%"=="y" (
    where nssm >nul 2>&1
    if errorlevel 1 (
        echo [WARNING] NSSM not found
        echo [INFO] Download NSSM from https://nssm.cc/ to create Windows service
        echo [INFO] After installing NSSM, run:
        echo   nssm install MonManBot python "%SCRIPT_DIR%main.py"
        echo   nssm set MonManBot AppDirectory "%SCRIPT_DIR%"
        echo   nssm set MonManBot DisplayName "MonMan Finance Bot"
        echo   nssm set MonManBot Description "Telegram Finance Bot"
        echo   nssm start MonManBot
    ) else (
        echo [INFO] Creating Windows service...
        nssm install MonManBot python "%SCRIPT_DIR%main.py"
        nssm set MonManBot AppDirectory "%SCRIPT_DIR%"
        nssm set MonManBot DisplayName "MonMan Finance Bot"
        nssm set MonManBot Description "Telegram Finance Bot"
        echo [SUCCESS] Service created (not started)
        echo [INFO] Service commands:
        echo   Start:   nssm start MonManBot
        echo   Stop:    nssm stop MonManBot
        echo   Remove:  nssm remove MonManBot
    )
)

echo.
echo [SUCCESS] Setup completed!
echo.
echo Usage examples:
echo   monman.bat            # GUI launcher (default)
echo   monman.bat start      # Start bot via CLI
echo   monman.bat status     # Check status
echo   monman.bat logs -f    # Follow logs
echo   python gui_launcher.py   # Direct GUI launch
echo.
pause
