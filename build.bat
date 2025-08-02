@echo off
REM Quick Build Script for Windows
REM Builds MonMan Bot executables using PyInstaller

echo.
echo ================================
echo   MonMan Bot Build System
echo ================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://python.org
    pause
    exit /b 1
)

REM Check if build.py exists
if not exist "build.py" (
    echo [ERROR] build.py not found
    echo Please run this script from the project root directory
    pause
    exit /b 1
)

REM Show options
echo Select build option:
echo 1. Build All (GUI + CLI + Bot + Package)
echo 2. Build GUI Launcher only
echo 3. Build CLI Launcher only  
echo 4. Build Main Bot only
echo 5. Create Portable Package only
echo 6. Install Build Dependencies only
echo 7. Clean Build Files
echo.

set /p choice="Enter your choice [1-7]: "

if "%choice%"=="1" (
    echo [INFO] Building all executables...
    python build.py
) else if "%choice%"=="2" (
    echo [INFO] Building GUI Launcher...
    python build.py gui
) else if "%choice%"=="3" (
    echo [INFO] Building CLI Launcher...
    python build.py cli
) else if "%choice%"=="4" (
    echo [INFO] Building Main Bot...
    python build.py bot
) else if "%choice%"=="5" (
    echo [INFO] Creating Portable Package...
    python build.py package
) else if "%choice%"=="6" (
    echo [INFO] Installing Build Dependencies...
    python build.py deps
) else if "%choice%"=="7" (
    echo [INFO] Cleaning Build Files...
    python build.py clean
) else (
    echo [ERROR] Invalid choice
    pause
    exit /b 1
)

echo.
echo Build process completed!
echo Check the 'dist' folder for output files.
echo.
pause
