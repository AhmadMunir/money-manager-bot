from telebot import types

def create_main_menu():
    """Create main menu keyboard"""
    markup = types.InlineKeyboardMarkup(row_width=2)
    
    # Row 1: Wallet and Transaction management
    btn_wallet = types.InlineKeyboardButton("🏦 Kantong", callback_data="wallet_menu")
    btn_transaction = types.InlineKeyboardButton("💸 Transaksi", callback_data="transaction_menu")
    markup.add(btn_wallet, btn_transaction)
    
    # Row 2: Reports and Analysis
    btn_report = types.InlineKeyboardButton("📊 Laporan", callback_data="report_menu")
    btn_analysis = types.InlineKeyboardButton("📈 Analisis", callback_data="analysis_menu")
    markup.add(btn_report, btn_analysis)
    
    # Row 3: Settings and Help
    btn_settings = types.InlineKeyboardButton("⚙️ Pengaturan", callback_data="settings_menu")
    btn_help = types.InlineKeyboardButton("❓ Bantuan", callback_data="help")
    markup.add(btn_settings, btn_help)
    
    return markup

def create_wallet_menu():
    """Create wallet management menu"""
    markup = types.InlineKeyboardMarkup(row_width=2)
    
    btn_list = types.InlineKeyboardButton("📋 Daftar Kantong", callback_data="wallet_list")
    btn_add = types.InlineKeyboardButton("➕ Tambah Kantong", callback_data="wallet_add")
    markup.add(btn_list, btn_add)
    
    btn_back = types.InlineKeyboardButton("🔙 Kembali", callback_data="main_menu")
    markup.add(btn_back)
    
    return markup

def create_transaction_menu():
    """Create transaction menu"""
    markup = types.InlineKeyboardMarkup(row_width=2)
    
    btn_income = types.InlineKeyboardButton("💰 Pemasukan", callback_data="transaction_income")
    btn_expense = types.InlineKeyboardButton("💸 Pengeluaran", callback_data="transaction_expense")
    markup.add(btn_income, btn_expense)
    
    btn_transfer = types.InlineKeyboardButton("🔄 Transfer", callback_data="transaction_transfer")
    btn_history = types.InlineKeyboardButton("📝 Riwayat", callback_data="transaction_history")
    markup.add(btn_transfer, btn_history)
    
    btn_back = types.InlineKeyboardButton("🔙 Kembali", callback_data="main_menu")
    markup.add(btn_back)
    
    return markup

def create_report_menu():
    """Create report menu"""
    markup = types.InlineKeyboardMarkup(row_width=2)
    
    btn_daily = types.InlineKeyboardButton("📅 Harian", callback_data="report_daily")
    btn_weekly = types.InlineKeyboardButton("📆 Mingguan", callback_data="report_weekly")
    markup.add(btn_daily, btn_weekly)
    
    btn_monthly = types.InlineKeyboardButton("🗓️ Bulanan", callback_data="report_monthly")
    btn_custom = types.InlineKeyboardButton("📊 Custom", callback_data="report_custom")
    markup.add(btn_monthly, btn_custom)
    
    btn_back = types.InlineKeyboardButton("🔙 Kembali", callback_data="main_menu")
    markup.add(btn_back)
    
    return markup

def create_analysis_menu():
    """Create analysis menu"""
    markup = types.InlineKeyboardMarkup(row_width=2)
    
    btn_wow = types.InlineKeyboardButton("📈 WoW", callback_data="analysis_wow")
    btn_mom = types.InlineKeyboardButton("📊 MoM", callback_data="analysis_mom")
    markup.add(btn_wow, btn_mom)
    
    btn_category = types.InlineKeyboardButton("🏷️ Per Kategori", callback_data="analysis_category")
    btn_trend = types.InlineKeyboardButton("📉 Trend", callback_data="analysis_trend")
    markup.add(btn_category, btn_trend)
    
    btn_back = types.InlineKeyboardButton("🔙 Kembali", callback_data="main_menu")
    markup.add(btn_back)
    
    return markup

def create_wallet_types_keyboard():
    """Create wallet types selection keyboard"""
    markup = types.InlineKeyboardMarkup(row_width=2)
    
    wallet_types = [
        ("💵 Kas/Tunai", "cash"),
        ("🏦 Bank", "bank"),
        ("📱 E-Wallet", "e-wallet"),
        ("💳 Kartu", "card"),
        ("📈 Investasi", "investment"),
        ("🏠 Aset", "asset"),
        ("💸 Hutang", "debt"),
        ("💰 Piutang", "receivable"),
        ("🎯 Lainnya", "other")
    ]
    
    for name, data in wallet_types:
        btn = types.InlineKeyboardButton(name, callback_data=f"wallet_type_{data}")
        markup.add(btn)
    
    btn_back = types.InlineKeyboardButton("🔙 Kembali", callback_data="wallet_menu")
    markup.add(btn_back)
    
    return markup

def create_wallet_list_keyboard(wallets):
    """Create keyboard for wallet list"""
    markup = types.InlineKeyboardMarkup(row_width=2)
    
    for wallet in wallets:
        btn_text = f"{get_wallet_emoji(wallet.type)} {wallet.name}"
        btn = types.InlineKeyboardButton(
            btn_text, 
            callback_data=f"wallet_detail_{wallet.id}"
        )
        markup.add(btn)
    
    btn_add = types.InlineKeyboardButton("➕ Tambah Kantong", callback_data="wallet_add")
    btn_back = types.InlineKeyboardButton("🔙 Kembali", callback_data="wallet_menu")
    markup.add(btn_add, btn_back)
    
    return markup

def create_wallet_detail_keyboard(wallet_id):
    """Create keyboard for wallet detail actions"""
    markup = types.InlineKeyboardMarkup(row_width=2)
    
    btn_edit = types.InlineKeyboardButton("✏️ Edit", callback_data=f"wallet_edit_{wallet_id}")
    btn_delete = types.InlineKeyboardButton("🗑️ Hapus", callback_data=f"wallet_delete_{wallet_id}")
    markup.add(btn_edit, btn_delete)
    
    btn_transactions = types.InlineKeyboardButton("📝 Transaksi", callback_data=f"wallet_transactions_{wallet_id}")
    markup.add(btn_transactions)
    
    btn_back = types.InlineKeyboardButton("🔙 Kembali", callback_data="wallet_list")
    markup.add(btn_back)
    
    return markup

def create_confirmation_keyboard(action, item_id=None):
    """Create confirmation keyboard (Yes/No)"""
    markup = types.InlineKeyboardMarkup(row_width=2)
    
    if item_id:
        btn_yes = types.InlineKeyboardButton("✅ Ya", callback_data=f"confirm_{action}_{item_id}")
        btn_no = types.InlineKeyboardButton("❌ Tidak", callback_data=f"cancel_{action}_{item_id}")
    else:
        btn_yes = types.InlineKeyboardButton("✅ Ya", callback_data=f"confirm_{action}")
        btn_no = types.InlineKeyboardButton("❌ Tidak", callback_data=f"cancel_{action}")
    
    markup.add(btn_yes, btn_no)
    
    return markup

def create_back_button(callback_data):
    """Create a simple back button"""
    markup = types.InlineKeyboardMarkup()
    btn_back = types.InlineKeyboardButton("🔙 Kembali", callback_data=callback_data)
    markup.add(btn_back)
    return markup

def create_wallet_selection_keyboard(wallets, action):
    """Create keyboard for selecting wallet"""
    markup = types.InlineKeyboardMarkup(row_width=2)
    
    for wallet in wallets:
        btn_text = f"{get_wallet_emoji(wallet.type)} {wallet.name}"
        btn = types.InlineKeyboardButton(
            btn_text, 
            callback_data=f"{action}_wallet_{wallet.id}"
        )
        markup.add(btn)
    
    btn_back = types.InlineKeyboardButton("🔙 Kembali", callback_data="transaction_menu")
    markup.add(btn_back)
    
    return markup

def get_wallet_emoji(wallet_type):
    """Get emoji for wallet type"""
    emojis = {
        'cash': '💵',
        'bank': '🏦',
        'e-wallet': '📱',
        'card': '💳',
        'investment': '📈',
        'asset': '🏠',
        'debt': '💸',
        'receivable': '💰',
        'other': '🎯'
    }
    return emojis.get(wallet_type, '💼')

def create_category_keyboard(transaction_type):
    """Create keyboard for category selection"""
    markup = types.InlineKeyboardMarkup(row_width=2)
    
    if transaction_type == 'income':
        categories = [
            ("💰 Gaji", "salary"),
            ("💼 Bisnis", "business"),
            ("🎁 Hadiah", "gift"),
            ("📈 Investasi", "investment_income"),
            ("🏠 Sewa", "rental"),
            ("🎯 Lainnya", "other_income")
        ]
    else:  # expense
        categories = [
            ("🍽️ Makanan", "food"),
            ("🏠 Rumah", "housing"),
            ("🚗 Transport", "transport"),
            ("👕 Belanja", "shopping"),
            ("🏥 Kesehatan", "health"),
            ("📚 Pendidikan", "education"),
            ("🎬 Hiburan", "entertainment"),
            ("🎯 Lainnya", "other_expense")
        ]
    
    for name, data in categories:
        btn = types.InlineKeyboardButton(name, callback_data=f"category_{data}")
        markup.add(btn)
    
    btn_back = types.InlineKeyboardButton("🔙 Kembali", callback_data="transaction_menu")
    markup.add(btn_back)
    
    return markup
