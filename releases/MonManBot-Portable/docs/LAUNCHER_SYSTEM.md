# MonMan Bot Launcher System

Sistem launcher multi-platform untuk MonMan Finance Bot dengan interface GUI (Windows) dan CLI (Linux/macOS).

## 🚀 Fitur Utama

### Windows GUI Launcher (`gui_launcher.py`)
- **Interface grafis lengkap** dengan tkinter
- **Start/Stop/Restart bot** dengan tombol
- **Real-time log monitoring** dengan color coding
- **Pilihan log level** (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- **Auto-scroll logs** dan limit baris maksimal
- **Save logs** ke file
- **Status monitoring** proses bot
- **Konfigurasi GUI** yang mudah

### Linux/macOS CLI Launcher (`cli_launcher.py`)
- **Command-line interface** dengan warna
- **Daemon mode** untuk background service
- **Interactive menu** untuk navigasi mudah
- **Real-time log following** (seperti tail -f)
- **Process management** dengan PID tracking
- **System integration** dengan systemd
- **Colored output** untuk berbagai log level

## 📦 Instalasi

### Windows
```bash
# 1. Clone repository
git clone https://github.com/AhmadMunir/money-manager-bot.git
cd money-manager-bot

# 2. Install dependencies
pip install -r requirements.txt
pip install -r requirements_launcher.txt

# 3. Setup launcher
setup_launcher.bat

# 4. Jalankan
monman.bat          # GUI launcher
monman.bat start    # CLI start
```

### Linux/macOS
```bash
# 1. Clone repository
git clone https://github.com/AhmadMunir/money-manager-bot.git
cd money-manager-bot

# 2. Install dependencies
pip3 install -r requirements.txt
pip3 install -r requirements_launcher.txt

# 3. Setup launcher
chmod +x setup_launcher.sh
./setup_launcher.sh

# 4. Jalankan
./monman            # Interactive menu
./monman start      # Start bot
python3 gui_launcher.py  # GUI (jika tersedia)
```

## 🎯 Penggunaan

### Windows

#### GUI Mode (Default)
```bash
monman.bat                    # Launch GUI
monman.bat gui                # Explicit GUI launch
python gui_launcher.py        # Direct GUI launch
```

#### CLI Mode
```bash
monman.bat start              # Start bot
monman.bat stop               # Stop bot
monman.bat restart            # Restart bot
monman.bat status             # Show status
monman.bat logs               # Show logs
monman.bat logs --follow      # Follow logs
monman.bat menu               # Interactive menu
```

### Linux/macOS

#### Command Line
```bash
./monman start                # Start bot
./monman stop                 # Stop bot
./monman restart              # Restart bot
./monman status               # Show status
./monman logs                 # Show last 100 lines
./monman logs -f              # Follow logs
./monman logs -n 50           # Show last 50 lines
./monman config               # Configure settings
./monman menu                 # Interactive menu

# Daemon mode
./monman start --daemon       # Start as background service
./monman restart --daemon     # Restart as background service
```

#### Direct Python
```bash
python3 cli_launcher.py start --daemon
python3 cli_launcher.py logs --follow
python3 gui_launcher.py       # GUI mode (jika X11/Wayland tersedia)
```

## ⚙️ Konfigurasi

Konfigurasi disimpan di `config/launcher_config.json`:

```json
{
  "log_level": "INFO",
  "bot_script": "main.py",
  "log_file": "logs/bot.log",
  "max_log_lines": 1000,
  "auto_scroll": true,
  "auto_restart": false,
  "restart_delay": 5
}
```

### Opsi Konfigurasi

| Parameter | Deskripsi | Default |
|-----------|-----------|---------|
| `log_level` | Level log (DEBUG/INFO/WARNING/ERROR/CRITICAL) | INFO |
| `bot_script` | Path ke script bot utama | main.py |
| `log_file` | Path ke file log bot | logs/bot.log |
| `max_log_lines` | Maksimal baris log di display | 1000 |
| `auto_scroll` | Auto-scroll log display | true |
| `auto_restart` | Restart otomatis jika crash | false |
| `restart_delay` | Delay restart dalam detik | 5 |

## 🖥️ Interface

### GUI Windows Features
- **Control Panel**: Start/Stop/Restart buttons
- **Status Display**: Real-time bot status
- **Log Viewer**: Scrollable log dengan syntax highlighting
- **Log Controls**: Level filter, auto-scroll, clear, save
- **Configuration**: GUI settings panel

### CLI Features
- **Colored Output**: Different colors for log levels
- **Interactive Menu**: Numbered menu untuk navigasi
- **Process Monitoring**: PID tracking dan resource usage
- **Log Following**: Real-time log streaming
- **Configuration**: Interactive config editor

## 🔧 Log Management

### Log Levels
- **DEBUG**: Informasi detail untuk debugging
- **INFO**: Informasi umum operasi bot
- **WARNING**: Peringatan yang tidak menghentikan operasi
- **ERROR**: Error yang perlu perhatian
- **CRITICAL**: Error critical yang menghentikan bot

### Log Display
- **Real-time**: Update otomatis saat bot berjalan
- **Color Coding**: Warna berbeda per level
- **Filtering**: Filter berdasarkan level
- **Export**: Save ke file untuk analisis

## 🌐 System Integration

### Windows Service (NSSM)
```bash
# Install NSSM dari https://nssm.cc/
nssm install MonManBot python "C:\path\to\main.py"
nssm set MonManBot AppDirectory "C:\path\to\bot"
nssm start MonManBot
```

### Linux Systemd Service
```bash
# Service file dibuat otomatis oleh setup script
systemctl --user start monman-bot
systemctl --user enable monman-bot
systemctl --user status monman-bot
```

### Desktop Integration
- **Windows**: Desktop shortcut otomatis
- **Linux**: Desktop entry untuk application launcher
- **macOS**: Dock integration

## 🚨 Troubleshooting

### Common Issues

#### "Python not found"
```bash
# Windows
# Install Python dari python.org
# Pastikan "Add to PATH" dicentang

# Linux/macOS
sudo apt install python3 python3-pip  # Ubuntu/Debian
brew install python3                   # macOS
```

#### "Permission denied"
```bash
# Linux/macOS
chmod +x monman
chmod +x setup_launcher.sh
```

#### "Bot won't start"
```bash
# Check dependencies
pip install -r requirements.txt

# Check config
./monman config

# Check logs
./monman logs -f
```

#### "GUI doesn't work on Linux"
```bash
# Install tkinter
sudo apt install python3-tk  # Ubuntu/Debian
```

### Log Locations
- **Launcher logs**: `logs/launcher.log`
- **Bot logs**: `logs/bot.log`
- **Error logs**: Console output dan file logs

## 📁 File Structure

```
├── gui_launcher.py          # Windows GUI launcher
├── cli_launcher.py          # Linux/macOS CLI launcher
├── monman.bat              # Windows batch script
├── monman                  # Linux/macOS shell script
├── setup_launcher.bat      # Windows setup
├── setup_launcher.sh       # Linux/macOS setup
├── requirements_launcher.txt # Launcher dependencies
├── config/
│   └── launcher_config.json # Launcher configuration
└── logs/
    ├── launcher.log        # Launcher logs
    └── bot.log            # Bot logs
```

## 🎨 Customization

### GUI Themes
Modifikasi `gui_launcher.py` untuk custom themes:
```python
# Add custom colors
self.log_text.tag_config("CUSTOM", foreground="purple")

# Custom window styling
self.root.configure(bg="dark gray")
```

### CLI Colors
Modifikasi `cli_launcher.py` untuk custom colors:
```python
class Colors:
    CUSTOM = '\033[95m'  # Custom purple
    # Add more custom colors
```

## 🔄 Updates

Launcher system mendukung:
- **Auto-update configuration**
- **Backward compatibility**
- **Settings migration**
- **Plugin system** (future)

## 📞 Support

Jika mengalami issues:
1. Check log files di `logs/`
2. Jalankan dengan debug mode: `--log-level DEBUG`
3. Check system requirements
4. Restart launcher dan bot

---

**Enjoy managing your MonMan Finance Bot with style! 🚀💰**
