import sqlite3
import shutil
import os

print("🔄 Data Recovery Process Started...")

# Backup current finance_bot.db if it exists
if os.path.exists('finance_bot.db'):
    shutil.copy('finance_bot.db', 'finance_bot_backup.db')
    print("✅ Backup created: finance_bot_backup.db")

# Simple approach: Copy monman.db to finance_bot.db
if os.path.exists('monman.db'):
    shutil.copy('monman.db', 'finance_bot.db')
    print("✅ Copied monman.db to finance_bot.db")
else:
    print("❌ monman.db not found!")

# Verify the copy worked
try:
    conn = sqlite3.connect('finance_bot.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT COUNT(*) FROM users')
    users = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM assets WHERE is_active = 1')
    assets = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM wallets WHERE is_active = 1')
    wallets = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM transactions WHERE is_active = 1')
    transactions = cursor.fetchone()[0]
    
    print(f"\n📊 Database Content:")
    print(f"Users: {users}")
    print(f"Wallets: {wallets}")
    print(f"Transactions: {transactions}")
    print(f"Assets: {assets}")
    
    if assets > 0:
        cursor.execute('SELECT name, symbol, asset_type, quantity, buy_price FROM assets WHERE is_active = 1')
        print(f"\n💼 Your Assets:")
        for asset in cursor.fetchall():
            print(f"  - {asset[0]} ({asset[1]}) [{asset[2]}]: {asset[3]} @ Rp {asset[4]:,.0f}")
    
    conn.close()
    
    print("\n✅ DATA RECOVERY SUCCESSFUL!")
    print("Your data is now restored in finance_bot.db")
    
except Exception as e:
    print(f"❌ Error checking data: {e}")
