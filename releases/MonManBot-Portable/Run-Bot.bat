@echo off
title MonMan Bot - Direct Launch
echo.
echo ================================
echo    MonMan Bot - Direct Mode
echo ================================
echo.

if not exist "MonManBot.exe" (
    echo ERROR: MonManBot.exe not found!
    echo Please ensure all files are extracted properly.
    pause
    exit /b 1
)

echo IMPORTANT: Make sure you have configured .env file!
echo Press any key to start the bot, or Ctrl+C to cancel.
pause

echo.
echo Starting MonMan Bot...
"MonManBot.exe"

echo.
echo Bot stopped. Check the output above for any errors.
pause
