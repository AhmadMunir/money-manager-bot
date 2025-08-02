#!/usr/bin/env python3
"""
Migration script to fix asset table column names to match the model
"""
import sqlite3
from datetime import datetime

def migrate():
    db_path = 'monman.db'
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check if the columns need to be renamed
        cursor.execute("PRAGMA table_info(assets)")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]
        
        print(f"Current columns: {column_names}")
        
        # Check if we need to rename return_value to return_amount
        if 'return_value' in column_names and 'return_amount' not in column_names:
            print("Renaming return_value to return_amount...")
            # SQLite doesn't support column rename directly, so we need to recreate the table
            
            # Create new table with correct column names
            cursor.execute('''
            CREATE TABLE assets_new (
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
                return_amount FLOAT DEFAULT 0.0,
                return_percentage FLOAT DEFAULT 0.0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT 1,
                FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY(wallet_id) REFERENCES wallets(id) ON DELETE CASCADE
            )
            ''')
            
            # Copy data from old table to new table
            cursor.execute('''
            INSERT INTO assets_new (
                id, user_id, wallet_id, name, asset_type, symbol, 
                quantity, buy_price, last_price, last_sync, 
                return_amount, return_percentage, created_at, updated_at, is_active
            )
            SELECT 
                id, user_id, wallet_id, name, asset_type, symbol,
                quantity, buy_price, last_price, last_sync,
                COALESCE(return_value, 0.0), COALESCE(return_percent, 0.0), 
                created_at, updated_at, is_active
            FROM assets
            ''')
            
            # Drop old table
            cursor.execute('DROP TABLE assets')
            
            # Rename new table
            cursor.execute('ALTER TABLE assets_new RENAME TO assets')
            
            print("Column renaming completed successfully!")
        else:
            print("Columns already have correct names or migration not needed.")
        
        conn.commit()
        
    except Exception as e:
        print(f"Error during migration: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    migrate()
