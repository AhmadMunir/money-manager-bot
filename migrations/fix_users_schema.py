#!/usr/bin/env python3
"""
Database migration to add missing columns to users table
Fixes the 'no such column: users.updated_at' error
"""

import sqlite3
import os
from datetime import datetime

def migrate_users_table():
    """Add missing columns to users table"""
    db_path = 'monman.db'
    
    if not os.path.exists(db_path):
        print(f"❌ Database file {db_path} not found!")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check current schema
        cursor.execute("PRAGMA table_info(users)")
        existing_columns = [row[1] for row in cursor.fetchall()]
        print(f"📋 Current columns: {existing_columns}")
        
        # Add missing columns if they don't exist
        columns_to_add = [
            ('updated_at', 'DATETIME'),
            ('last_activity', 'DATETIME')
        ]
        
        for column_name, column_type in columns_to_add:
            if column_name not in existing_columns:
                print(f"➕ Adding column: {column_name}")
                default_value = datetime.utcnow().isoformat()
                cursor.execute(f"ALTER TABLE users ADD COLUMN {column_name} {column_type} DEFAULT '{default_value}'")
                
                # Update existing rows with current timestamp
                cursor.execute(f"UPDATE users SET {column_name} = ? WHERE {column_name} IS NULL", (default_value,))
                print(f"✅ Column {column_name} added successfully")
            else:
                print(f"⏭️  Column {column_name} already exists")
        
        # Verify the updated schema
        cursor.execute("PRAGMA table_info(users)")
        updated_columns = [row[1] for row in cursor.fetchall()]
        print(f"✅ Updated columns: {updated_columns}")
        
        conn.commit()
        conn.close()
        
        print("🎉 Database migration completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        if 'conn' in locals():
            conn.rollback()
            conn.close()
        return False

if __name__ == "__main__":
    print("🚀 Starting database migration...")
    success = migrate_users_table()
    if success:
        print("✅ Migration completed successfully!")
    else:
        print("❌ Migration failed!")
