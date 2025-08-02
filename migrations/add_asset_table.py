#!/usr/bin/env python3
"""
Migration script to add Asset table for stocks/crypto assets
"""
import sqlite3
from datetime import datetime

def migrate():
    db_path = 'monman.db'
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    # Check if assets table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='assets'")
    if cursor.fetchone():
        print('Table assets already exists.')
        return
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
        return_value FLOAT,
        return_percent FLOAT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        is_active BOOLEAN DEFAULT 1,
        FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE,
        FOREIGN KEY(wallet_id) REFERENCES wallets(id) ON DELETE CASCADE
    )
    ''')
    print('Table assets created.')
    conn.commit()
    conn.close()

if __name__ == "__main__":
    migrate()
