#!/usr/bin/env python3
import sqlite3
import sys

def copy_data():
    try:
        # Connect to both databases
        source_conn = sqlite3.connect('monman.db')
        target_conn = sqlite3.connect('finance_bot.db')
        
        source_cursor = source_conn.cursor()
        target_cursor = target_conn.cursor()
        
        print("🔄 Copying data from monman.db to finance_bot.db...")
        
        # Copy users
        print("👤 Copying users...")
        source_cursor.execute("SELECT * FROM users")
        users = source_cursor.fetchall()
        for user in users:
            try:
                target_cursor.execute("INSERT OR REPLACE INTO users VALUES (?,?,?,?,?,?,?,?,?,?,?)", user)
                print(f"  ✅ User copied: Telegram ID {user[1]}")
            except Exception as e:
                print(f"  ❌ Error copying user: {e}")
        
        # Copy wallets
        print("💰 Copying wallets...")
        source_cursor.execute("SELECT * FROM wallets")
        wallets = source_cursor.fetchall()
        for wallet in wallets:
            try:
                target_cursor.execute("INSERT OR REPLACE INTO wallets VALUES (?,?,?,?,?,?,?,?)", wallet)
                print(f"  ✅ Wallet copied: {wallet[1]} - Rp {wallet[2]:,.0f}")
            except Exception as e:
                print(f"  ❌ Error copying wallet: {e}")
        
        # Copy transactions 
        print("📊 Copying transactions...")
        source_cursor.execute("SELECT * FROM transactions")
        transactions = source_cursor.fetchall()
        for txn in transactions:
            try:
                target_cursor.execute("INSERT OR REPLACE INTO transactions VALUES (?,?,?,?,?,?,?,?,?,?)", txn)
                print(f"  ✅ Transaction copied: {txn[1]} Rp {txn[2]:,.0f}")
            except Exception as e:
                print(f"  ❌ Error copying transaction: {e}")
        
        # Copy assets
        print("📈 Copying assets...")
        source_cursor.execute("SELECT * FROM assets")
        assets = source_cursor.fetchall()
        for asset in assets:
            try:
                target_cursor.execute("INSERT OR REPLACE INTO assets VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)", asset)
                print(f"  ✅ Asset copied: {asset[1]} ({asset[3]}) - {asset[4]} @ Rp {asset[5]:,.0f}")
            except Exception as e:
                print(f"  ❌ Error copying asset: {e}")
        
        # Copy categories
        print("📂 Copying categories...")
        try:
            source_cursor.execute("SELECT * FROM categories")
            categories = source_cursor.fetchall()
            for category in categories:
                try:
                    target_cursor.execute("INSERT OR REPLACE INTO categories VALUES (?,?,?,?,?,?,?)", category)
                    print(f"  ✅ Category copied: {category[1]}")
                except Exception as e:
                    print(f"  ❌ Error copying category: {e}")
        except Exception as e:
            print(f"  ℹ️  Categories table not found or empty: {e}")
        
        # Commit changes
        target_conn.commit()
        
        # Verify
        print("\n✅ VERIFICATION:")
        target_cursor.execute("SELECT COUNT(*) FROM users")
        users_count = target_cursor.fetchone()[0]
        print(f"Users: {users_count}")
        
        target_cursor.execute("SELECT COUNT(*) FROM wallets WHERE is_active = 1")
        wallets_count = target_cursor.fetchone()[0]
        print(f"Active Wallets: {wallets_count}")
        
        target_cursor.execute("SELECT COUNT(*) FROM assets WHERE is_active = 1")
        assets_count = target_cursor.fetchone()[0]
        print(f"Active Assets: {assets_count}")
        
        if assets_count > 0:
            print("\n💼 Your Restored Assets:")
            target_cursor.execute("SELECT name, symbol, asset_type, quantity, buy_price FROM assets WHERE is_active = 1")
            for i, asset in enumerate(target_cursor.fetchall(), 1):
                print(f"{i}. {asset[0]} ({asset[1]}) [{asset[2]}] - {asset[3]} @ Rp {asset[4]:,.0f}")
        
        print("\n🎉 DATA RECOVERY COMPLETED SUCCESSFULLY!")
        print("Your data has been restored to finance_bot.db")
        
        # Close connections
        source_conn.close()
        target_conn.close()
        
    except Exception as e:
        print(f"❌ Error during data copy: {e}")
        sys.exit(1)

if __name__ == "__main__":
    copy_data()
