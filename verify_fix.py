#!/usr/bin/env python3
"""
Test script untuk memverifikasi fix schema database
"""

import sqlite3
import sys
import os

def test_database_schema():
    """Test apakah schema database sudah benar"""
    try:
        print("🔍 Testing database schema...")
        
        # Connect to database
        conn = sqlite3.connect('monman.db')
        cursor = conn.cursor()
        
        # Test query yang sebelumnya error
        query = """
        SELECT id, telegram_id, username, first_name, last_name, 
               timezone, language, created_at, updated_at, last_activity, is_active 
        FROM users 
        WHERE telegram_id = 413217834 AND is_active = 1 
        LIMIT 1
        """
        
        cursor.execute(query)
        result = cursor.fetchone()
        
        if result:
            print("✅ Query berhasil! Data user ditemukan:")
            columns = ['id', 'telegram_id', 'username', 'first_name', 'last_name', 
                      'timezone', 'language', 'created_at', 'updated_at', 'last_activity', 'is_active']
            for i, col in enumerate(columns):
                print(f"  {col}: {result[i]}")
        else:
            print("✅ Query berhasil! Tidak ada user dengan telegram_id tersebut.")
        
        print("🎉 Schema fix berhasil - tidak ada lagi error kolom!")
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        if 'conn' in locals():
            conn.close()
        return False

def test_user_service():
    """Test UserService dengan schema yang sudah diperbaiki"""
    try:
        print("\n🔍 Testing UserService...")
        sys.path.append('src')
        from services.user_service import UserService
        
        user_service = UserService()
        print("✅ UserService berhasil diinisialisasi")
        
        # Test get user
        user = user_service.get_user_by_telegram_id(413217834)
        if user:
            print(f"✅ User ditemukan: {user.username or user.first_name}")
            print(f"   Updated at: {user.updated_at}")
            print(f"   Last activity: {user.last_activity}")
        else:
            print("ℹ️  User tidak ditemukan (normal untuk user baru)")
            
        print("✅ UserService test berhasil!")
        return True
        
    except Exception as e:
        print(f"❌ UserService error: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Starting schema fix verification...")
    
    # Test database schema
    schema_ok = test_database_schema()
    
    # Test UserService
    service_ok = test_user_service()
    
    if schema_ok and service_ok:
        print("\n🎉 Semua test berhasil! Error 'no such column: users.updated_at' sudah teratasi!")
        print("✅ Bot siap dijalankan dengan perintah: python main_enhanced.py")
    else:
        print("\n❌ Masih ada masalah yang perlu diperbaiki")
