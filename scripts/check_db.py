#!/usr/bin/env python3
import sqlite3
import os

# Check both databases
for db_name in ['finance_bot.db', 'monman.db']:
    if os.path.exists(db_name):
        print(f"\n=== {db_name} ===")
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()
        
        try:
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='assets'")
            if cursor.fetchone():
                cursor.execute('PRAGMA table_info(assets)')
                columns = cursor.fetchall()
                print("Assets table columns:")
                for col in columns:
                    print(f"  {col[1]} ({col[2]})")
                    
                column_names = [col[1] for col in columns]
                
                # Check if we need to fix the schema
                if 'return_value' not in column_names and 'return_amount' in column_names:
                    print(f"  -> Needs migration: return_amount -> return_value")
                elif 'return_value' not in column_names and 'return_percent' not in column_names:
                    print(f"  -> Needs migration: missing return columns")
                else:
                    print(f"  -> Schema OK")
            else:
                print("No assets table found")
        except Exception as e:
            print(f"Error: {e}")
        finally:
            conn.close()
    else:
        print(f"{db_name} not found")
