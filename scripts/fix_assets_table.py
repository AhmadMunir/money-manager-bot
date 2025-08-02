#!/usr/bin/env python3
"""
Fix the assets table in finance_bot.db to match the model expectations
"""
import sqlite3
import os
from datetime import datetime

def main():
    db_path = 'finance_bot.db'
    print(f"Working with {db_path}")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check if assets table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='assets'")
        table_exists = cursor.fetchone() is not None
        
        if table_exists:
            print("Assets table exists, checking schema...")
            cursor.execute('PRAGMA table_info(assets)')
            columns = cursor.fetchall()
            column_names = [col[1] for col in columns]
            print(f"Current columns: {column_names}")
            
            # Check if we have the correct columns
            has_return_value = 'return_value' in column_names
            has_return_percent = 'return_percent' in column_names
            
            if not has_return_value or not has_return_percent:
                print("Need to recreate table with correct schema...")
                
                # Get existing data if any
                cursor.execute('SELECT COUNT(*) FROM assets')
                count = cursor.fetchone()[0]
                
                if count > 0:
                    print(f"Backing up {count} existing records...")
                    cursor.execute('ALTER TABLE assets RENAME TO assets_backup')
                else:
                    print("No existing data, dropping table...")
                    cursor.execute('DROP TABLE assets')
                
                # Create new table with correct schema
                print("Creating new assets table...")
                cursor.execute('''
                CREATE TABLE assets (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    wallet_id INTEGER,
                    name VARCHAR(100) NOT NULL,
                    asset_type VARCHAR(20) NOT NULL,
                    symbol VARCHAR(20) NOT NULL,
                    quantity FLOAT NOT NULL DEFAULT 0.0,
                    buy_price FLOAT NOT NULL DEFAULT 0.0,
                    last_price FLOAT,
                    last_sync DATETIME,
                    return_value FLOAT DEFAULT 0.0,
                    return_percent FLOAT DEFAULT 0.0,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    is_active BOOLEAN DEFAULT 1,
                    FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE,
                    FOREIGN KEY(wallet_id) REFERENCES wallets(id) ON DELETE CASCADE
                )
                ''')
                
                # Restore data if we had any
                if count > 0:
                    print("Restoring data...")
                    try:
                        # Try to copy from backup, mapping old column names
                        cursor.execute('''
                        INSERT INTO assets (
                            id, user_id, wallet_id, name, asset_type, symbol, 
                            quantity, buy_price, last_price, last_sync, 
                            return_value, return_percent, created_at, updated_at, is_active
                        )
                        SELECT 
                            id, user_id, wallet_id, name, asset_type, symbol,
                            quantity, buy_price, last_price, last_sync,
                            0.0, 0.0, 
                            created_at, updated_at, is_active
                        FROM assets_backup
                        ''')
                        cursor.execute('DROP TABLE assets_backup')
                        print("Data restored successfully")
                    except Exception as e:
                        print(f"Error restoring data: {e}")
                        print("Continuing with empty table...")
                
                print("Table recreated successfully!")
            else:
                print("Schema is already correct!")
        else:
            print("Assets table doesn't exist, creating it...")
            cursor.execute('''
            CREATE TABLE assets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                wallet_id INTEGER,
                name VARCHAR(100) NOT NULL,
                asset_type VARCHAR(20) NOT NULL,
                symbol VARCHAR(20) NOT NULL,
                quantity FLOAT NOT NULL DEFAULT 0.0,
                buy_price FLOAT NOT NULL DEFAULT 0.0,
                last_price FLOAT,
                last_sync DATETIME,
                return_value FLOAT DEFAULT 0.0,
                return_percent FLOAT DEFAULT 0.0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT 1,
                FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY(wallet_id) REFERENCES wallets(id) ON DELETE CASCADE
            )
            ''')
            print("Assets table created!")
        
        conn.commit()
        
        # Verify the final schema
        cursor.execute('PRAGMA table_info(assets)')
        columns = cursor.fetchall()
        print("\nFinal schema:")
        for col in columns:
            print(f"  {col[1]} ({col[2]})")
            
    except Exception as e:
        print(f"Error: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == '__main__':
    main()
