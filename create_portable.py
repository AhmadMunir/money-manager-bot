# MonMan Bot - Portable Package Creator
# Creates a portable zip package with all executables and necessary files

import os
import shutil
import zipfile
from pathlib import Path
from datetime import datetime

def create_portable_package():
    """Create portable package"""
    print("📦 Creating MonMan Bot Portable Package...")
    
    # Paths
    root_dir = Path(".")
    dist_dir = Path("dist")
    portable_dir = Path("releases/MonManBot-Portable")
    
    # Version info
    version = "2.0.0"
    timestamp = datetime.now().strftime("%Y%m%d")
    
    # Clean and create portable directory
    if portable_dir.exists():
        shutil.rmtree(portable_dir)
    portable_dir.mkdir(parents=True, exist_ok=True)
    
    print("📁 Creating portable directory structure...")
    
    # Copy executables if they exist
    executables = [
        "MonManBot-GUI.exe",
        "MonManBot-CLI.exe", 
        "MonManBot.exe"
    ]
    
    for exe in executables:
        exe_path = dist_dir / exe
        if exe_path.exists():
            shutil.copy2(exe_path, portable_dir)
            print(f"✅ Copied {exe}")
        else:
            print(f"⚠️  {exe} not found, skipping")
    
    # Copy essential files
    essential_files = [
        "README.md",
        ".env.example",
        "requirements.txt",
        "requirements_launcher.txt"
    ]
    
    for file in essential_files:
        file_path = root_dir / file
        if file_path.exists():
            shutil.copy2(file_path, portable_dir)
            print(f"✅ Copied {file}")
    
    # Copy directories
    dirs_to_copy = [
        ("config", "config"),
        ("assets", "assets"),
        ("docs", "docs")
    ]
    
    for src, dst in dirs_to_copy:
        src_path = root_dir / src
        if src_path.exists():
            shutil.copytree(src_path, portable_dir / dst, dirs_exist_ok=True)
            print(f"✅ Copied {src}/ directory")
    
    # Create logs directory
    logs_dir = portable_dir / "logs"
    logs_dir.mkdir(exist_ok=True)
    
    # Create .gitkeep for logs
    (logs_dir / ".gitkeep").write_text("")
    
    # Create launcher batch files
    create_launcher_scripts(portable_dir)
    
    # Create README for portable
    create_portable_readme(portable_dir)
    
    # Create ZIP package
    zip_name = f"MonManBot-Portable-v{version}-{timestamp}.zip"
    zip_path = Path("releases") / zip_name
    
    print(f"🗜️  Creating ZIP package: {zip_name}")
    
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(portable_dir):
            for file in files:
                file_path = Path(root) / file
                arc_name = file_path.relative_to(portable_dir)
                zipf.write(file_path, arc_name)
    
    # Calculate sizes
    portable_size = sum(f.stat().st_size for f in portable_dir.rglob('*') if f.is_file())
    zip_size = zip_path.stat().st_size
    
    print("🎉 Portable package created successfully!")
    print(f"📁 Portable folder: {portable_dir} ({portable_size / 1024 / 1024:.1f} MB)")
    print(f"📦 ZIP package: {zip_path} ({zip_size / 1024 / 1024:.1f} MB)")
    
    return zip_path

def create_launcher_scripts(portable_dir):
    """Create launcher scripts for portable package"""
    
    # GUI Launcher
    gui_script = portable_dir / "Launch-GUI.bat"
    gui_script.write_text("""@echo off
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
""")
    
    # CLI Launcher
    cli_script = portable_dir / "Launch-CLI.bat"
    cli_script.write_text("""@echo off
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
""")
    
    # Bot Direct Launch
    bot_script = portable_dir / "Run-Bot.bat"
    bot_script.write_text("""@echo off
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
""")
    
    print("✅ Created launcher scripts")

def create_portable_readme(portable_dir):
    """Create README for portable package"""
    
    readme_content = """# MonMan Bot - Portable Package

Welcome to MonMan Bot Portable! This package contains all the executables and files needed to run the bot without installation.

## 🚀 Quick Start

### Method 1: GUI Interface (Recommended for Windows)
1. Double-click `Launch-GUI.bat`
2. Use the graphical interface to start/stop the bot
3. Monitor logs and configure settings through the GUI

### Method 2: Command Line Interface
1. Double-click `Launch-CLI.bat`
2. Use the interactive menu to manage the bot
3. Great for advanced users and automation

### Method 3: Direct Bot Launch
1. Configure your `.env` file (copy from `.env.example`)
2. Double-click `Run-Bot.bat`
3. Bot will start directly (for experienced users)

## ⚙️ Configuration

### First Time Setup
1. Copy `.env.example` to `.env`
2. Edit `.env` with your Telegram bot token:
   ```
   TELEGRAM_BOT_TOKEN=your_bot_token_here
   DATABASE_URL=sqlite:///monman.db
   ```
3. Save the file and launch the bot

### Config Files
- `config/launcher_config.json` - Launcher settings
- `config/backup_config.json` - Backup system settings
- `.env` - Environment variables (create from .env.example)

## 📁 Files Included

### Executables
- `MonManBot-GUI.exe` - Windows GUI launcher
- `MonManBot-CLI.exe` - Command-line interface
- `MonManBot.exe` - Main bot application

### Launcher Scripts
- `Launch-GUI.bat` - Start GUI interface
- `Launch-CLI.bat` - Start CLI interface  
- `Run-Bot.bat` - Direct bot launch

### Supporting Files
- `config/` - Configuration files
- `assets/` - Application assets (icons, etc.)
- `docs/` - Documentation
- `logs/` - Log files (created automatically)
- Various requirement and readme files

## 🔧 Troubleshooting

### "Bot won't start"
1. Check your `.env` file configuration
2. Ensure your bot token is valid
3. Check `logs/bot.log` for error messages

### "Executable won't run"
1. Right-click executable → Properties → Unblock (if present)
2. Run as Administrator if needed
3. Check Windows Defender/antivirus settings

### "Permission denied"
1. Extract to a folder where you have write permissions
2. Avoid extracting to Program Files or system directories
3. Try running as Administrator

## 📚 Documentation

Check the `docs/` folder for detailed documentation:
- `LAUNCHER_SYSTEM.md` - Launcher system guide
- `BACKUP_SYSTEM.md` - Backup system guide
- `PROJECT_STRUCTURE.md` - Project structure
- Various other guides and documentation

## 🔄 Updates

To update:
1. Download the latest portable package
2. Extract to a new folder
3. Copy your `.env` and `config/` files from the old version
4. Copy your `logs/` folder if you want to keep history

## 💡 Tips

- **GUI Mode**: Best for everyday use, easy monitoring
- **CLI Mode**: Great for automation and advanced features
- **Direct Mode**: For experienced users who want full control
- **Logs**: Always check logs if something goes wrong
- **Backup**: The bot has automatic backup features built-in

## 🆘 Support

If you encounter issues:
1. Check the logs in `logs/` folder
2. Review the documentation in `docs/`
3. Check the GitHub repository for updates
4. Report issues on the GitHub issue tracker

---

**Enjoy using MonMan Bot! 🤖💰**

Package Version: 2.0.0
Build Date: """ + datetime.now().strftime("%Y-%m-%d") + """
"""
    
    readme_path = portable_dir / "README-PORTABLE.txt"
    readme_path.write_text(readme_content)
    
    print("✅ Created portable README")

if __name__ == "__main__":
    create_portable_package()
