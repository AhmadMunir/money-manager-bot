# Mon-Man Bot 💰

Bot Telegram untuk manajemen keuangan pribadi yang membantu Anda mencatat dan memantau keuangan dengan mudah.

## ✨ Fitur Utama

### 🏦 Manajemen Kantong/Aset
- ➕ Tambah/Edit/Hapus kantong (Dompet, Bank, E-Wallet, Investasi, dll.)
- 💰 Set saldo awal saat membuat kantong
- 📊 Lihat total saldo semua kantong

### 💸 Pencatatan Transaksi
- **Pemasukan**: Catat penghasilan dari berbagai sumber
- **Pengeluaran**: Catat pengeluaran dengan kategori
- **Transfer**: Transfer uang antar kantong
- **Format Cepat**: 
  - `/in 50000 gaji dari BCA`
  - `/out 25000 makan siang dari Dompet`
  - `/transfer 100000 BCA Dana`

### 📊 Laporan Keuangan
- 📅 Laporan harian, mingguan, bulanan
- 📈 Analisis perbandingan (WoW, MoM)
- 💡 Insight otomatis untuk pengeluaran
- 🔔 Notifikasi laporan otomatis (opsional)

### 📈 Analisis Perbandingan
- **Week over Week (WoW)**: Perbandingan minggu ini vs minggu lalu
- **Month over Month (MoM)**: Perbandingan bulan ini vs bulan lalu
- **Highlight**: Perubahan signifikan dan trend

## 🚀 Quick Start

### 1. Persiapan
```bash
# Clone repository
git clone <repository-url>
cd mon-man

# Install dependencies
pip install -r requirements.txt
```

### 2. Konfigurasi
```bash
# Copy file konfigurasi
cp .env.example .env

# Edit file .env
nano .env
```

Isi konfigurasi di `.env`:
```env
# Bot Configuration
TELEGRAM_BOT_TOKEN=your_bot_token_here
DATABASE_URL=sqlite:///finance_bot.db
TIMEZONE=Asia/Jakarta

# Report Settings
AUTO_REPORT_ENABLED=True
DAILY_REPORT_TIME=08:00

# Admin Users (opsional)
ADMIN_USER_IDS=123456789
```

### 3. Dapatkan Bot Token
1. Chat dengan [@BotFather](https://t.me/BotFather) di Telegram
2. Kirim `/newbot` dan ikuti instruksi
3. Copy token dan masukkan ke `.env`

### 4. Jalankan Bot
```bash
python main.py
```

## Struktur Database

- **users**: Data pengguna bot
- **wallets**: Kantong/asset pengguna
- **transactions**: Semua transaksi keuangan
- **categories**: Kategori transaksi

## Commands

- `/start` - Mulai menggunakan bot
- `/help` - Bantuan penggunaan
- `/wallet` - Manajemen kantong
- `/add` - Tambah transaksi
- `/report` - Lihat laporan
- `/settings` - Pengaturan bot

## Pattern Transaksi

- **Pemasukan**: `/in [jumlah] [deskripsi] dari [kantong]`
- **Pengeluaran**: `/out [jumlah] [deskripsi] dari [kantong]`
- **Transfer**: `/transfer [jumlah] dari [kantong1] ke [kantong2]`

## Kontribusi

Silakan buat issue atau pull request untuk improvement.

## License

MIT License
