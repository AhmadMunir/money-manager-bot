#!/usr/bin/env python3
import sqlite3
import os

# Check both databases
dbs = ['monman.db', 'finance_bot.db']
for db_name in dbs:
    if os.path.exists(db_name):
        print(f'\n=== {db_name} ===')
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()
        
        # Get table names
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        print(f'Tables: {[t[0] for t in tables]}')
        
        # Check if we have users
        if 'users' in [t[0] for t in tables]:
            cursor.execute('SELECT COUNT(*) FROM users')
            user_count = cursor.fetchone()[0]
            print(f'Users count: {user_count}')
            
        # Check if we have assets
        if 'assets' in [t[0] for t in tables]:
            cursor.execute('SELECT COUNT(*) FROM assets WHERE is_active = 1')
            asset_count = cursor.fetchone()[0]
            print(f'Active assets count: {asset_count}')
            
            if asset_count > 0:
                cursor.execute('SELECT id, name, symbol, asset_type, quantity, buy_price FROM assets WHERE is_active = 1 LIMIT 5')
                assets = cursor.fetchall()
                print('Sample assets:')
                for asset in assets:
                    print(f'  ID: {asset[0]}, Name: {asset[1]}, Symbol: {asset[2]}, Type: {asset[3]}, Qty: {asset[4]}, Price: {asset[5]}')
                    
        conn.close()
    else:
        print(f'{db_name} not found')
