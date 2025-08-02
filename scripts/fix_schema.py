#!/usr/bin/env python3
"""
Simple script to check and fix asset table schema
"""
import sqlite3

def main():
    conn = sqlite3.connect('monman.db')
    cursor = conn.cursor()
    
    # Check current schema
    cursor.execute('PRAGMA table_info(assets)')
    columns = cursor.fetchall()
    print("Current columns:")
    for col in columns:
        print(f"  {col[1]} ({col[2]})")
    
    column_names = [col[1] for col in columns]
    
    # Check if we need to migrate
    needs_migration = 'return_value' not in column_names or 'return_percent' not in column_names
    
    if needs_migration:
        print("\nNeed to migrate columns...")
        
        # Create new table with correct schema
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
            return_value FLOAT DEFAULT 0.0,
            return_percent FLOAT DEFAULT 0.0,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            is_active BOOLEAN DEFAULT 1,
            FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY(wallet_id) REFERENCES wallets(id) ON DELETE CASCADE
        )
        ''')
        
        # Copy data if old table has data
        try:
            cursor.execute('SELECT COUNT(*) FROM assets')
            count = cursor.fetchone()[0]
            if count > 0:
                print(f"Copying {count} records...")
                # Map old columns to new ones
                if 'return_amount' in column_names:
                    # Old schema: return_amount, return_percentage
                    cursor.execute('''
                    INSERT INTO assets_new (
                        id, user_id, wallet_id, name, asset_type, symbol, 
                        quantity, buy_price, last_price, last_sync, 
                        return_value, return_percent, created_at, updated_at, is_active
                    )
                    SELECT 
                        id, user_id, wallet_id, name, asset_type, symbol,
                        quantity, buy_price, last_price, last_sync,
                        COALESCE(return_amount, 0.0), COALESCE(return_percentage, 0.0), 
                        created_at, updated_at, is_active
                    FROM assets
                    ''')
                else:
                    # Already has return_value, return_percent but might be missing
                    cursor.execute('''
                    INSERT INTO assets_new (
                        id, user_id, wallet_id, name, asset_type, symbol, 
                        quantity, buy_price, last_price, last_sync, 
                        return_value, return_percent, created_at, updated_at, is_active
                    )
                    SELECT 
                        id, user_id, wallet_id, name, asset_type, symbol,
                        quantity, buy_price, last_price, last_sync,
                        COALESCE(return_value, 0.0), COALESCE(return_percent, 0.0), 
                        created_at, updated_at, is_active
                    FROM assets
                    ''')
        except Exception as e:
            print(f"Error copying data: {e}")
        
        # Drop old table and rename new one
        cursor.execute('DROP TABLE assets')
        cursor.execute('ALTER TABLE assets_new RENAME TO assets')
        
        conn.commit()
        print("Migration completed!")
        
        # Verify new schema
        cursor.execute('PRAGMA table_info(assets)')
        columns = cursor.fetchall()
        print("\nNew columns:")
        for col in columns:
            print(f"  {col[1]} ({col[2]})")
    else:
        print("Schema is already correct!")
    
    conn.close()

if __name__ == '__main__':
    main()
