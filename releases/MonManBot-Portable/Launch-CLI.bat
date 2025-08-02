@echo off
title MonMan Bot - CLI Interface
echo.
echo ================================
echo    MonMan Bot - CLI Mode
echo ================================
echo.

if not exist "MonManBot-CLI.exe" (
    echo ERROR: MonManBot-CLI.exe not found!
    echo Please ensure all files are extracted properly.
    pause
    exit /b 1
)

echo Starting CLI interface...
"MonManBot-CLI.exe" menu

pause
