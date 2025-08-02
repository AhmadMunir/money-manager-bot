# MonMan Bot Configuration Guide

Panduan lengkap untuk mengkonfigurasi MonMan Finance Bot melalui GUI dan CLI launcher.

## 🔧 Configuration Overview

MonMan Bot menggunakan file `.env` untuk menyimpan konfigurasi utama seperti:
- **Bot Token** - Token dari @BotFather
- **Admin ID** - Telegram ID admin
- **Database URL** - Konfigurasi database
- **Settings lainnya** - Timezone, log level, dll

## 🖥️ Windows GUI Configuration

### Akses Configuration
1. Buka `MonManBot-GUI.exe` atau `python gui_launcher.py`
2. Klik tombol **"⚙️ Config"** di control panel
3. Dialog konfigurasi akan terbuka

### Configuration Dialog Features

#### 🤖 Bot Token
- **Input Field**: Masked input untuk keamanan
- **Show/Hide Toggle**: Checkbox untuk menampilkan/menyembunyikan token
- **Validation**: Otomatis validasi format token
- **Test Connection**: Button untuk test koneksi ke Telegram

#### 👤 Admin ID
- **Input Field**: Telegram ID administrator
- **Validation**: Harus berupa angka
- **Info**: Petunjuk mendapatkan ID dari @userinfobot

#### 💾 Database URL
- **Input Field**: URL database (default: SQLite)
- **Examples**: 
  - SQLite: `sqlite:///monman.db`
  - PostgreSQL: `postgresql://user:pass@host/db`
  - MySQL: `mysql://user:pass@host/db`

#### 🔍 Test Connection
- Tombol untuk test koneksi bot ke Telegram API
- Menampilkan nama bot jika berhasil
- Error handling jika token invalid

#### 📄 Load Example
- Load konfigurasi dari `.env.example`
- Template konfigurasi standar
- Mudah untuk first-time setup

### GUI Dialog Actions
```
📄 Load Example  - Load template konfigurasi
💾 Save         - Simpan konfigurasi ke .env
❌ Cancel       - Batal tanpa menyimpan
```

## 🐧 Linux/macOS CLI Configuration

### Akses Configuration
```bash
./monman config              # Menu konfigurasi
python3 cli_launcher.py config
```

### Configuration Menu
```
Configuration Menu:
═══════════════════════════════════════
1. Bot Settings (Token & Admin ID)
2. Launcher Settings
3. Load Example Configuration  
4. Back to Main Menu
```

### 1. Bot Settings
Interactive setup untuk:

#### Bot Token Configuration
```bash
Current Bot Token: 1234567890:AAE...***
Get Bot Token from @BotFather on Telegram
Enter Bot Token (Enter to keep current): [input]
```

#### Admin ID Configuration  
```bash
Current Admin ID: 123456789
Get your Telegram ID from @userinfobot
Enter Admin Telegram ID (Enter to keep current): [input]
```

#### Database Configuration
```bash
Current Database URL: sqlite:///monman.db
Enter Database URL (Enter to keep current): [input]
```

#### Connection Test
```bash
Test bot connection? [y/N]: y
✅ Bot connected: MonMan Finance Bot
```

### 2. Launcher Settings
Konfigurasi launcher-specific:
- **Log Level**: DEBUG/INFO/WARNING/ERROR/CRITICAL
- **Bot Script Path**: Path ke main bot script
- **Auto Restart**: Enable/disable auto restart
- **Max Log Lines**: Maksimal baris log ditampilkan

### 3. Load Example Configuration
```bash
Example Configuration:
BOT_TOKEN: ********************
ADMIN_ID: your_telegram_id_here
DATABASE_URL: sqlite:///monman.db

Load this configuration? [y/N]: y
✅ Example configuration loaded!
```

## 📋 Configuration Process

### First-Time Setup
1. **Install Bot**: Clone repository dan install dependencies
2. **Create Bot**: Contact @BotFather untuk mendapatkan token
3. **Get Admin ID**: Contact @userinfobot untuk mendapatkan Telegram ID
4. **Configure**: Gunakan GUI atau CLI untuk setup
5. **Test**: Test koneksi sebelum menjalankan bot
6. **Start Bot**: Jalankan bot dengan launcher

### Step-by-Step Guide

#### 1. Create Telegram Bot
```
1. Open Telegram
2. Search for @BotFather
3. Send /newbot
4. Follow instructions
5. Copy the token (format: 123456:ABC-DEF...)
```

#### 2. Get Your Telegram ID
```
1. Search for @userinfobot
2. Send /start
3. Copy your ID (numeric, e.g., 123456789)
```

#### 3. Configure via GUI (Windows)
```
1. Run MonManBot-GUI.exe
2. Click ⚙️ Config button
3. Paste Bot Token
4. Enter Admin ID
5. Click Test Connection
6. Click Save
```

#### 4. Configure via CLI (Linux/macOS)
```bash
./monman config
# Select option 1: Bot Settings
# Enter token and admin ID
# Test connection
# Save configuration
```

## 🔒 Security Features

### Token Security
- **Masked Input**: Token disembunyikan di GUI
- **No Logging**: Token tidak di-log ke file
- **Secure Storage**: Disimpan di .env (add to .gitignore)

### Validation
- **Token Format**: Validasi format Telegram token
- **Admin ID**: Validasi numeric ID
- **Connection Test**: Test real connection ke Telegram

### File Permissions
```bash
# Set secure permissions for .env
chmod 600 .env
```

## 🐛 Troubleshooting

### Common Issues

#### "Invalid Bot Token"
```bash
# Solutions:
1. Check token format (should contain :)
2. Verify from @BotFather  
3. Regenerate token if needed
4. Check for extra spaces
```

#### "Connection Test Failed"
```bash
# Solutions:
1. Check internet connection
2. Verify token is correct
3. Check firewall settings
4. Try again later (Telegram API issue)
```

#### "Admin ID must be numeric"
```bash
# Solutions:
1. Use @userinfobot to get correct ID
2. Remove any letters or symbols
3. Use your personal Telegram ID, not username
```

#### ".env file not found"
```bash
# Solutions:
1. Use configuration GUI/CLI first
2. Copy from .env.example
3. Create manually with correct format
```

### Configuration Validation
```bash
# Check current configuration
./monman status

# Test configuration
python3 -c "
import os
from dotenv import load_dotenv
load_dotenv()
print('BOT_TOKEN:', '✅' if os.getenv('BOT_TOKEN') else '❌')
print('ADMIN_ID:', '✅' if os.getenv('ADMIN_ID') else '❌')
"
```

## 📁 Configuration Files

### .env (Main Configuration)
```bash
BOT_TOKEN=1234567890:AABBCCDDEE...
ADMIN_ID=123456789
DATABASE_URL=sqlite:///monman.db
LOG_LEVEL=INFO
TIMEZONE=Asia/Jakarta
```

### .env.example (Template)
Template dengan contoh values dan dokumentasi lengkap.

### config/launcher_config.json (Launcher Settings)
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

## 🎯 Best Practices

### Security
- ✅ Keep `.env` file private (add to .gitignore)
- ✅ Use strong bot token from @BotFather
- ✅ Limit admin access to trusted users only
- ✅ Regular token rotation if compromised

### Configuration Management
- ✅ Use configuration GUI/CLI untuk setup
- ✅ Test connection sebelum deployment
- ✅ Backup konfigurasi penting
- ✅ Document custom settings

### Production Deployment
- ✅ Validate semua settings sebelum production
- ✅ Use production database (PostgreSQL/MySQL)
- ✅ Set appropriate log level (INFO/WARNING)
- ✅ Enable auto-restart untuk production

---

**Configuration yang benar adalah kunci kesuksesan MonMan Bot! 🚀**
