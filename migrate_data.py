#!/usr/bin/env python3
"""
Script untuk memindahkan data dari monman.db ke finance_bot.db
"""
import sqlite3
import os
from datetime import datetime

def migrate_data():
    # Connect to both databases
    old_db = sqlite3.connect('monman.db')
    new_db = sqlite3.connect('finance_bot.db')
    
    old_cursor = old_db.cursor()
    new_cursor = new_db.cursor()
    
    print("🔄 Starting data migration...")
    
    # Migrate users
    print("📤 Migrating users...")
    old_cursor.execute("SELECT * FROM users")
    users = old_cursor.fetchall()
    
    for user in users:
        try:
            new_cursor.execute("""
                INSERT OR REPLACE INTO users 
                (id, telegram_id, username, first_name, last_name, timezone, language, created_at, updated_at, last_activity, is_active)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, user)
            print(f"✅ User migrated: ID {user[0]}, Telegram ID {user[1]}")
        except Exception as e:
            print(f"❌ Error migrating user {user[0]}: {e}")
    
    # Migrate categories
    print("📤 Migrating categories...")
    old_cursor.execute("SELECT * FROM categories")
    categories = old_cursor.fetchall()
    
    for category in categories:
        try:
            new_cursor.execute("""
                INSERT OR REPLACE INTO categories 
                (id, name, type, user_id, description, created_at, is_active)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, category)
            print(f"✅ Category migrated: {category[1]}")
        except Exception as e:
            print(f"❌ Error migrating category {category[0]}: {e}")
    
    # Migrate wallets
    print("📤 Migrating wallets...")
    old_cursor.execute("SELECT * FROM wallets")
    wallets = old_cursor.fetchall()
    
    for wallet in wallets:
        try:
            new_cursor.execute("""
                INSERT OR REPLACE INTO wallets 
                (id, name, balance, user_id, description, created_at, updated_at, is_active)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, wallet)
            print(f"✅ Wallet migrated: {wallet[1]} - {wallet[2]}")
        except Exception as e:
            print(f"❌ Error migrating wallet {wallet[0]}: {e}")
    
    # Migrate transactions
    print("📤 Migrating transactions...")
    old_cursor.execute("SELECT * FROM transactions")
    transactions = old_cursor.fetchall()
    
    for transaction in transactions:
        try:
            new_cursor.execute("""
                INSERT OR REPLACE INTO transactions 
                (id, type, amount, description, category_id, wallet_id, user_id, transaction_date, created_at, is_active)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, transaction)
            print(f"✅ Transaction migrated: {transaction[1]} - {transaction[2]}")
        except Exception as e:
            print(f"❌ Error migrating transaction {transaction[0]}: {e}")
    
    # Migrate assets
    print("📤 Migrating assets...")
    old_cursor.execute("SELECT * FROM assets")
    assets = old_cursor.fetchall()
    
    for asset in assets:
        try:
            new_cursor.execute("""
                INSERT OR REPLACE INTO assets 
                (id, name, asset_type, symbol, quantity, buy_price, last_price, return_value, return_percent, wallet_id, user_id, created_at, updated_at, is_active)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, asset)
            print(f"✅ Asset migrated: {asset[1]} ({asset[3]}) - {asset[4]} @ {asset[5]}")
        except Exception as e:
            print(f"❌ Error migrating asset {asset[0]}: {e}")
    
    # Commit changes
    new_db.commit()
    
    # Close connections
    old_db.close()
    new_db.close()
    
    print("✅ Migration completed!")
    
    # Verify migration
    print("\n🔍 Verifying migration...")
    new_db = sqlite3.connect('finance_bot.db')
    cursor = new_db.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM users")
    user_count = cursor.fetchone()[0]
    print(f"Users in new database: {user_count}")
    
    cursor.execute("SELECT COUNT(*) FROM wallets WHERE is_active = 1")
    wallet_count = cursor.fetchone()[0]
    print(f"Active wallets in new database: {wallet_count}")
    
    cursor.execute("SELECT COUNT(*) FROM transactions WHERE is_active = 1")
    transaction_count = cursor.fetchone()[0]
    print(f"Active transactions in new database: {transaction_count}")
    
    cursor.execute("SELECT COUNT(*) FROM assets WHERE is_active = 1")
    asset_count = cursor.fetchone()[0]
    print(f"Active assets in new database: {asset_count}")
    
    if asset_count > 0:
        cursor.execute("SELECT name, symbol, asset_type, quantity, buy_price FROM assets WHERE is_active = 1")
        assets = cursor.fetchall()
        print("\n📊 Your assets:")
        for asset in assets:
            print(f"  - {asset[0]} ({asset[1]}) [{asset[2]}]: {asset[3]} @ Rp {asset[4]:,.0f}")
    
    new_db.close()

if __name__ == "__main__":
    if os.path.exists('monman.db') and os.path.exists('finance_bot.db'):
        migrate_data()
    else:
        print("❌ Database files not found!")
