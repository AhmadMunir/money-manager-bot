#!/usr/bin/env python3
"""
Quick verification that database schema is correct
"""
import sqlite3

# Check finance_bot.db schema
try:
    conn = sqlite3.connect('finance_bot.db')
    cursor = conn.cursor()
    
    # Check if assets table exists and has correct columns
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='assets'")
    if cursor.fetchone():
        cursor.execute('PRAGMA table_info(assets)')
        columns = [col[1] for col in cursor.fetchall()]
        print(f"Assets table columns: {columns}")
        
        required = ['return_value', 'return_percent']
        missing = [col for col in required if col not in columns]
        
        if not missing:
            print("✅ Schema is correct! Asset creation should work now.")
        else:
            print(f"❌ Missing columns: {missing}")
    else:
        print("❌ Assets table not found")
        
    conn.close()
    
except Exception as e:
    print(f"Error: {e}")
