#!/usr/bin/env python3
"""
Simple script to recreate database tables with correct schema
"""
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import after path setup
from src.models.database import Base, engine, SessionLocal
from sqlalchemy import text

def main():
    print("Recreating database tables...")
    
    # Drop and recreate all tables to ensure correct schema
    try:
        # This will create all tables with the current schema from the models
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables recreated successfully!")
        
        # Test that we can create a session
        db = SessionLocal()
        try:
            # Test a simple query
            result = db.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))
            tables = [row[0] for row in result]
            print(f"📋 Tables created: {tables}")
            
            # Check assets table schema
            if 'assets' in tables:
                result = db.execute(text("PRAGMA table_info(assets)"))
                columns = [row[1] for row in result]
                print(f"📈 Assets table columns: {columns}")
                
                if 'return_value' in columns and 'return_percent' in columns:
                    print("✅ Assets table has correct schema!")
                else:
                    print("❌ Assets table schema is still incorrect")
            else:
                print("❌ Assets table not found")
                
        finally:
            db.close()
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    if success:
        print("\n🎉 Database is ready! You can now restart the bot and test asset creation.")
    else:
        print("\n❌ Database setup failed.")
