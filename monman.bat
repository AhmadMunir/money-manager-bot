@echo off
REM MonMan Bot Launcher Batch Script for Windows
REM This script provides easy commands to manage the bot

setlocal EnableDelayedExpansion

set SCRIPT_DIR=%~dp0
set GUI_LAUNCHER=%SCRIPT_DIR%gui_launcher.py
set CLI_LAUNCHER=%SCRIPT_DIR%cli_launcher.py

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH
    echo Please install Python 3.8+ and add it to your PATH
    pause
    exit /b 1
)

REM Check if GUI launcher exists
if not exist "%GUI_LAUNCHER%" (
    echo [ERROR] GUI launcher not found: %GUI_LAUNCHER%
    pause
    exit /b 1
)

REM Parse command line arguments
set COMMAND=%1
set USE_CLI=false

if "%COMMAND%"=="cli" (
    set USE_CLI=true
    shift
    set COMMAND=%1
)

if "%COMMAND%"=="-h" goto :show_help
if "%COMMAND%"=="--help" goto :show_help
if "%COMMAND%"=="help" goto :show_help

REM If no command specified or GUI requested, launch GUI
if "%COMMAND%"=="" (
    echo [INFO] Starting MonMan Bot GUI Launcher...
    python "%GUI_LAUNCHER%"
    goto :eof
)

if "%COMMAND%"=="gui" (
    echo [INFO] Starting MonMan Bot GUI Launcher...
    python "%GUI_LAUNCHER%"
    goto :eof
)

REM Use CLI for specific commands
if "%USE_CLI%"=="true" (
    python "%CLI_LAUNCHER%" %*
) else (
    REM Check if command is CLI-only
    if "%COMMAND%"=="start" goto :use_cli
    if "%COMMAND%"=="stop" goto :use_cli
    if "%COMMAND%"=="restart" goto :use_cli
    if "%COMMAND%"=="status" goto :use_cli
    if "%COMMAND%"=="logs" goto :use_cli
    if "%COMMAND%"=="config" goto :use_cli
    if "%COMMAND%"=="menu" goto :use_cli
    
    REM Unknown command, show help
    goto :show_help
)

goto :eof

:use_cli
python "%CLI_LAUNCHER%" %*
goto :eof

:show_help
echo.
echo MonMan Bot Launcher for Windows
echo.
echo Usage: %~nx0 [COMMAND] [OPTIONS]
echo.
echo Commands:
echo   gui       - Launch GUI interface (default)
echo   cli       - Use CLI interface for following commands
echo   start     - Start the bot
echo   stop      - Stop the bot  
echo   restart   - Restart the bot
echo   status    - Show bot status
echo   logs      - Show bot logs
echo   config    - Configure settings
echo   menu      - Interactive CLI menu
echo.
echo Options (for CLI commands):
echo   -d, --daemon    - Run as background service
echo   -f, --follow    - Follow logs in real-time
echo   -n, --lines N   - Show N lines of logs
echo   --log-level L   - Set log level
echo.
echo Examples:
echo   %~nx0                    # Launch GUI (default)
echo   %~nx0 gui                # Launch GUI explicitly
echo   %~nx0 start              # Start bot via CLI
echo   %~nx0 cli start --daemon # Start bot as service via CLI
echo   %~nx0 logs --follow      # Follow logs via CLI
echo   %~nx0 menu               # Interactive CLI menu
echo.
goto :eof
