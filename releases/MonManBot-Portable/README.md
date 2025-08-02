# 💰 Money Manager Bot

Bot Telegram untuk mengelola keuangan pribadi dengan fitur manajemen aset, wallet, dan laporan keuangan yang komprehensif.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Telegram](https://img.shields.io/badge/Telegram-Bot%20API-blue.svg)
![SQLite](https://img.shields.io/badge/Database-SQLite-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## ✨ Fitur Utama

- 💼 **Manajemen Wallet**: Kelola berbagai jenis dompet (cash, bank, e-wallet, investasi)
- 📈 **Manajemen Aset**: Tracking saham dan cryptocurrency dengan sinkronisasi harga otomatis
- 💸 **Transaksi**: Catat pemasukan, pengeluaran, dan transfer antar wallet
- 📊 **Laporan**: Laporan keuangan harian, mingguan, dan bulanan
- ⏰ **Scheduler**: Pengingat dan laporan otomatis
- 🔄 **Sinkronisasi Harga**: Update harga aset secara real-time
- 📱 **Interface Intuitif**: Menu interaktif dengan keyboard inline

## 🏗️ Struktur Project

```
money-manager-bot/
├── 🚀 main.py                 # Entry point aplikasi
├── 📦 requirements.txt        # Dependencies Python
├── 📖 README.md              # Dokumentasi project
├── ⚙️ .env.example           # Template environment variables
├── 🚫 .gitignore            # Git ignore rules
│
├── 💻 src/                   # Source code utama
│   ├── 🤖 handlers/          # Bot command handlers
│   │   ├── start_handler.py
│   │   ├── wallet_handler.py
│   │   ├── transaction_handler.py
│   │   ├── asset_handler.py
│   │   └── report_handler.py
│   ├── 🗄️ models/            # Database models
│   │   └── database.py
│   ├── ⚙️ services/          # Business logic
│   │   ├── asset_service.py
│   │   ├── report_service.py
│   │   ├── scheduler_service.py
│   │   ├── user_service.py
│   │   ├── registration_service.py
│   │   └── message_logging_service.py
│   └── 🛠️ utils/             # Utility functions
│       ├── helpers.py
│       └── keyboards.py
│
├── 🗃️ migrations/            # Database migrations
├── 🧪 tests/                # Unit tests
├── 📜 scripts/              # Utility scripts
├── 📄 logs/                 # Log files
├── 📚 docs/                 # Documentation
└── 📊 data/                 # Data files
```

## 🚀 Quick Start

### 1. Prerequisites

- Python 3.8 atau lebih tinggi
- Bot Token dari Telegram BotFather
- Git (untuk clone repository)

### 2. Installation

```bash
# Clone repository
git clone https://github.com/AhmadMunir/money-manager-bot.git
cd money-manager-bot

# Install dependencies
pip install -r requirements.txt

# Setup environment variables
cp .env.example .env
```

### 3. Configuration

Edit file `.env` dan masukkan token bot Anda:

```env
BOT_TOKEN=your_telegram_bot_token_here
DATABASE_URL=sqlite:///finance_bot.db
```

### 4. Run Bot

```bash
python main.py
```

Bot akan mulai berjalan dan siap menerima perintah di Telegram!

## 🤖 Commands & Usage

### Basic Commands
- `/start` - Mulai menggunakan bot dan registrasi user
- `/help` - Bantuan dan daftar command

### Wallet Management
- `/wallet` - Kelola wallet/dompet
- `/saldo` - Cek saldo total semua wallet

### Asset Management  
- `/tambahaset` - Tambah aset investasi (saham/crypto)
- `/aset` - Lihat daftar aset dan portfolio
- `/sinkron` - Update harga aset terbaru

### Transaction Management
- `/transaksi` - Catat transaksi baru
- `/riwayat` - Lihat riwayat transaksi

### Reports
- `/laporan` - Generate laporan keuangan
- `/summary` - Ringkasan keuangan

## 💡 Fitur Detail

### 🏦 Wallet Management
- Support multiple wallet types (Cash, Bank, E-wallet, Investment)
- Real-time balance tracking
- Transfer antar wallet
- Wallet categorization

### 📈 Asset Portfolio
- **Saham**: Tracking saham Indonesia (IDX)
- **Cryptocurrency**: Bitcoin, Ethereum, dan crypto populer
- **Auto Sync**: Harga update otomatis
- **Return Calculation**: P&L real-time
- **Portfolio Analysis**: Performance tracking

### 💸 Transaction Tracking
- Income, Expense, Transfer recording
- Category management
- Date and time tracking
- Notes and descriptions
- Multi-currency support (IDR focus)

### 📊 Reporting
- Daily, Weekly, Monthly reports
- Income vs Expense analysis
- Asset performance reports
- Export to various formats
- Visual charts and graphs

## 🛠️ Development

### Running Tests
```bash
# Run all tests
python -m pytest tests/

# Run specific test
python -m pytest tests/test_bot.py -v

# Run with coverage
python -m pytest tests/ --cov=src/
```

### Database Management
```bash
# Initialize database
python migrations/init_db_enhanced.py

# Check database schema
python scripts/check_db.py

# Recreate database (WARNING: will delete all data)
python scripts/recreate_db.py
```

### Code Quality
```bash
# Format code with black
black src/ tests/

# Lint with flake8
flake8 src/ tests/

# Type checking with mypy
mypy src/
```

## 🗃️ Database Schema

### Core Tables
- **Users**: User information and settings
- **Wallets**: User wallets and balances
- **Transactions**: All financial transactions
- **Assets**: Investment assets (stocks, crypto)
- **Categories**: Transaction categories

### Relationships
- User → Wallets (1:N)
- User → Transactions (1:N)
- User → Assets (1:N)
- Wallet → Transactions (1:N)
- Asset → Wallet (N:1)

## 🔧 Configuration

### Environment Variables
```env
# Required
BOT_TOKEN=your_telegram_bot_token

# Optional
DATABASE_URL=sqlite:///finance_bot.db
LOG_LEVEL=INFO
TIMEZONE=Asia/Jakarta
```

### Logging
Log files disimpan di folder `logs/`:
- `bot.log` - Application logs
- `message_logs.log` - Message handling logs

## 🐛 Troubleshooting

### Common Issues

#### Bot tidak merespon
- Pastikan `BOT_TOKEN` benar di file `.env`
- Cek koneksi internet
- Lihat log di `logs/bot.log`

#### Database error
```bash
# Reset database
python scripts/recreate_db.py

# Check schema
python scripts/check_db.py
```

#### Asset price sync gagal
- Cek koneksi internet
- API rate limit (tunggu beberapa menit)
- Lihat log untuk detail error

## 🤝 Contributing

1. Fork repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

### Development Guidelines
- Follow PEP 8 style guide
- Add tests for new features
- Update documentation
- Use meaningful commit messages

## 📝 Changelog

### v1.0.0 (2025-08-02)
- ✅ Initial release
- ✅ Basic wallet management
- ✅ Asset tracking (stocks & crypto)
- ✅ Transaction recording
- ✅ Report generation
- ✅ Telegram bot interface

## 🔮 Roadmap

### v1.1.0 (Planned)
- [ ] Web dashboard interface
- [ ] Advanced portfolio analytics  
- [ ] Budget planning and alerts
- [ ] Multi-language support
- [ ] Data export/import features

### v1.2.0 (Future)
- [ ] Mobile app companion
- [ ] Integration with bank APIs
- [ ] AI-powered financial insights
- [ ] Social features (family sharing)

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [pyTelegramBotAPI](https://github.com/eternnoir/pyTelegramBotAPI) - Telegram Bot API wrapper
- [SQLAlchemy](https://www.sqlalchemy.org/) - Python SQL toolkit
- [Yahoo Finance](https://finance.yahoo.com/) - Stock price data
- [CoinGecko](https://www.coingecko.com/) - Cryptocurrency price data

## 📞 Support

- 🐛 **Issues**: [GitHub Issues](https://github.com/AhmadMunir/money-manager-bot/issues)
- 💬 **Discussions**: [GitHub Discussions](https://github.com/AhmadMunir/money-manager-bot/discussions)
- 📧 **Email**: [email-anda@domain.com](mailto:email-anda@domain.com)

---

<div align="center">
Made with ❤️ by <a href="https://github.com/AhmadMunir">AhmadMunir</a>
</div>

---

### 🌟 Star History

[![Star History Chart](https://api.star-history.com/svg?repos=AhmadMunir/money-manager-bot&type=Date)](https://star-history.com/#AhmadMunir/money-manager-bot&Date)
