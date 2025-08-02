@echo off
title MonMan Bot - GUI Launcher
echo.
echo ================================
echo    MonMan Bot - GUI Mode
echo ================================
echo.

if not exist "MonManBot-GUI.exe" (
    echo ERROR: MonManBot-GUI.exe not found!
    echo Please ensure all files are extracted properly.
    pause
    exit /b 1
)

echo Starting GUI interface...
start "" "MonManBot-GUI.exe"

echo.
echo GUI launched! Check for the window or system tray.
echo You can close this window now.
echo.
pause
