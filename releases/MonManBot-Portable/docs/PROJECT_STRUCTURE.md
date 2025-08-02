# MonMan Bot - Project Structure

Struktur project yang diorganisasi dengan baik untuk development, build, dan deployment.

## 📁 Directory Structure

```
monman-bot/
├── 📂 src/                          # Source code utama
│   ├── handlers/                    # Bot command handlers
│   ├── models/                      # Database models
│   ├── services/                    # Business logic services
│   └── utils/                       # Utility functions
├── 📂 scripts/                      # Maintenance scripts
│   ├── backup_system.py            # Backup system
│   ├── auto_backup.py              # Auto backup integration
│   └── various maintenance scripts
├── 📂 migrations/                   # Database migrations
├── 📂 config/                       # Configuration files
│   ├── launcher_config.json        # Launcher settings
│   └── backup_config.json          # Backup settings
├── 📂 logs/                         # Log files
│   ├── bot.log                     # Main bot logs
│   ├── launcher.log                # Launcher logs
│   └── message_logs.log            # Message logs
├── 📂 docs/                         # Documentation
│   ├── README.md                   # Main documentation
│   ├── LAUNCHER_SYSTEM.md          # Launcher guide
│   ├── BACKUP_SYSTEM.md            # Backup guide
│   └── various guides
├── 📂 assets/                       # Static assets
│   ├── icon.ico                    # Application icon
│   └── other resources
├── 📂 specs/                        # PyInstaller spec files (generated)
├── 📂 build/                        # Build artifacts (temp)
├── 📂 dist/                         # Distribution files (executables)
├── 📂 releases/                     # Release packages
├── 📂 backups/                      # Database backups
├── 📂 tests/                        # Test files
├── 📄 main.py                       # Main bot application
├── 📄 gui_launcher.py               # Windows GUI launcher
├── 📄 cli_launcher.py               # Linux/macOS CLI launcher
├── 📄 monman.bat                    # Windows launcher script
├── 📄 monman                        # Linux/macOS launcher script
├── 📄 build.py                      # Advanced build system
├── 📄 simple_build.py               # Simple build script
├── 📄 build.bat                     # Windows build script
├── 📄 build.sh                      # Linux/macOS build script
├── 📄 create_icon.py                # Icon generation
├── 📄 setup_launcher.bat            # Windows setup
├── 📄 setup_launcher.sh             # Linux/macOS setup
├── 📄 requirements.txt              # Main dependencies
├── 📄 requirements_launcher.txt     # Launcher dependencies
├── 📄 requirements_build.txt        # Build dependencies
├── 📄 .env.example                  # Environment template
├── 📄 .gitignore                    # Git ignore rules
└── 📄 README.md                     # Project documentation
```

## 🎯 File Categories

### 🔧 Core Application
- `main.py` - Entry point bot utama
- `src/` - Semua source code terorganisir
- `config/` - File konfigurasi
- `logs/` - File log aplikasi

### 🖥️ Launchers & UI
- `gui_launcher.py` - Windows GUI interface
- `cli_launcher.py` - Linux/macOS CLI interface  
- `monman.bat` / `monman` - Platform-specific scripts

### 🔨 Build System
- `build.py` - Advanced build system dengan PyInstaller
- `simple_build.py` - Simple build untuk testing
- `build.bat` / `build.sh` - Interactive build scripts
- `requirements_build.txt` - Build dependencies

### 📦 Distribution
- `dist/` - Compiled executables (.exe, binaries)
- `releases/` - Release packages (.zip, installers)
- `specs/` - PyInstaller specification files

### 🛠️ Setup & Installation
- `setup_launcher.*` - Platform setup scripts
- `create_icon.py` - Icon generation utility
- `requirements_*.txt` - Various dependency files

### 📚 Documentation & Support
- `docs/` - Comprehensive documentation
- `README.md` - Main project documentation
- `tests/` - Test files and validation

## 🚀 Build Process

### 1. Simple Build (Quick Test)
```bash
# Windows
python simple_build.py gui
python simple_build.py cli

# Linux/macOS  
python3 simple_build.py gui
python3 simple_build.py cli
```

### 2. Interactive Build
```bash
# Windows
build.bat

# Linux/macOS
./build.sh
```

### 3. Advanced Build (Full Package)
```bash
# Install build dependencies
python build.py deps

# Build everything
python build.py

# Or specific components
python build.py gui
python build.py cli
python build.py bot
```

## 📋 Build Outputs

### Executables (dist/)
- `MonManBot-GUI.exe` - Windows GUI launcher
- `MonManBot-CLI.exe` - CLI launcher (cross-platform)
- `MonManBot.exe` - Main bot application

### Packages (releases/)
- `MonManBot-Portable-{version}.zip` - Portable package
- `MonManBot-Setup-{version}.exe` - Windows installer (if NSIS available)

## ⚙️ Configuration Files

### launcher_config.json
```json
{
  "log_level": "INFO",
  "bot_script": "main.py", 
  "log_file": "logs/bot.log",
  "max_log_lines": 1000,
  "auto_scroll": true,
  "auto_restart": false
}
```

### backup_config.json
```json
{
  "backup_retention_days": 30,
  "max_backups": 10,
  "auto_backup_enabled": true,
  "backup_on_startup": true,
  "backup_on_shutdown": true
}
```

## 🔄 Development Workflow

### 1. Code Changes
- Edit files in `src/`
- Test with `python main.py`
- Use launchers for GUI testing

### 2. Testing
- Run `./monman start` (Linux) or `monman.bat start` (Windows)
- Test GUI with `python gui_launcher.py`
- Check logs in `logs/` directory

### 3. Building
- Quick test: `python simple_build.py`
- Full build: `python build.py`
- Use interactive scripts for ease

### 4. Distribution
- Check `/dist` for executables
- Check `/releases` for packages
- Test executables before release

## 🧹 Maintenance

### Clean Build Files
```bash
python build.py clean
# Or delete: build/, dist/, specs/*.spec
```

### Update Dependencies
```bash
pip install -r requirements.txt --upgrade
pip install -r requirements_launcher.txt --upgrade
pip install -r requirements_build.txt --upgrade
```

### Backup Database
```bash
./monman # Interactive menu > Backup options
# Or use backup system directly
python scripts/backup_system.py
```

## 🎨 Customization

### Custom Icon
- Replace `assets/icon.ico` with your icon
- Or run `python create_icon.py` to generate new one

### Build Settings
- Edit `build.py` for advanced build options
- Modify `.spec` files for PyInstaller customization

### Launcher Themes
- Edit GUI colors in `gui_launcher.py`
- Modify CLI colors in `cli_launcher.py`

---

**Struktur ini memungkinkan development yang efisien dan deployment yang mudah! 🚀**
