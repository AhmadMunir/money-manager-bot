#!/usr/bin/env python3
import sqlite3

def main():
    conn = sqlite3.connect('monman.db')
    cursor = conn.cursor()
    
    try:
        print('Before migration:')
        cursor.execute('PRAGMA table_info(assets)')
        columns = cursor.fetchall()
        for col in columns:
            print(f'  {col[1]} ({col[2]})')
        
        column_names = [col[1] for col in columns]
        
        if 'return_value' in column_names and 'return_amount' not in column_names:
            print('\nRunning migration...')
            
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
            
            # Drop old table and rename new table
            cursor.execute('DROP TABLE assets')
            cursor.execute('ALTER TABLE assets_new RENAME TO assets')
            
            conn.commit()
            print('Migration completed successfully!')
            
            # Verify the new structure
            print('\nAfter migration:')
            cursor.execute('PRAGMA table_info(assets)')
            for col in cursor.fetchall():
                print(f'  {col[1]} ({col[2]})')
        else:
            print('\nMigration not needed - columns already correct')
            
    except Exception as e:
        print(f'Error during migration: {e}')
        conn.rollback()
        raise
    finally:
        conn.close()

if __name__ == '__main__':
    main()
