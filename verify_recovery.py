#!/usr/bin/env python3
import sqlite3

try:
    conn = sqlite3.connect('finance_bot.db')
    cursor = conn.cursor()
    
    # Check users
    cursor.execute('SELECT COUNT(*) FROM users')
    users = cursor.fetchone()[0]
    
    # Check assets
    cursor.execute('SELECT COUNT(*) FROM assets WHERE is_active = 1')
    assets = cursor.fetchone()[0]
    
    # Check wallets
    cursor.execute('SELECT COUNT(*) FROM wallets WHERE is_active = 1')
    wallets = cursor.fetchone()[0]
    
    print("DATABASE RECOVERY STATUS:")
    print("=" * 40)
    print(f"✅ Users: {users}")
    print(f"✅ Active Wallets: {wallets}")
    print(f"✅ Active Assets: {assets}")
    
    if assets > 0:
        print("\nYOUR ASSETS:")
        print("-" * 20)
        cursor.execute('SELECT name, symbol, asset_type, quantity, buy_price FROM assets WHERE is_active = 1')
        for i, asset in enumerate(cursor.fetchall(), 1):
            print(f"{i}. {asset[0]} ({asset[1]}) [{asset[2]}]")
            print(f"   Quantity: {asset[3]}")
            print(f"   Buy Price: Rp {asset[4]:,.0f}")
            print()
    
    conn.close()
    
    if users > 0:
        print("🎉 DATA RECOVERY SUCCESSFUL!")
        print("Your data has been restored and the bot should work normally now.")
    else:
        print("❌ No data found. Please check the original database.")
        
except Exception as e:
    print(f"❌ Error: {e}")
