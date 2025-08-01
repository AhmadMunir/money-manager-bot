"""
Enhanced database initialization with performance optimizations and user isolation
"""
import os
import sys

# Add the parent directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.models.database import SessionLocal, Category, create_tables, engine
from sqlalchemy import text
import logging

logger = logging.getLogger(__name__)

def init_database():
    """Initialize database with tables, indexes, and default data"""
    print("🔧 Creating database tables with optimizations...")
    create_tables()
    
    # Enable SQLite optimizations
    if 'sqlite' in str(engine.url):
        print("🚀 Applying SQLite performance optimizations...")
        with engine.connect() as conn:
            conn.execute(text("PRAGMA journal_mode=WAL"))
            conn.execute(text("PRAGMA synchronous=NORMAL"))
            conn.execute(text("PRAGMA cache_size=10000"))
            conn.execute(text("PRAGMA temp_store=MEMORY"))
            conn.execute(text("PRAGMA mmap_size=268435456"))  # 256MB
            conn.commit()
    
    print("📊 Creating default categories...")
    create_default_categories()
    
    print("✅ Enhanced database initialization completed!")

def create_default_categories():
    """Create default income and expense categories"""
    db = SessionLocal()
    try:
        # Check if categories already exist
        existing_categories = db.query(Category).filter(Category.is_system == True).count()
        if existing_categories > 0:
            print("⚠️ Default categories already exist, skipping...")
            return
        
        # Income categories
        income_categories = [
            {"name": "Gaji", "type": "income", "icon": "💼"},
            {"name": "Bonus", "type": "income", "icon": "🎁"},
            {"name": "Freelance", "type": "income", "icon": "💻"},
            {"name": "Investasi", "type": "income", "icon": "📈"},
            {"name": "Hadiah", "type": "income", "icon": "🎉"},
            {"name": "Penjualan", "type": "income", "icon": "🛒"},
            {"name": "Lainnya", "type": "income", "icon": "💰"},
        ]
        
        # Expense categories
        expense_categories = [
            {"name": "Makanan", "type": "expense", "icon": "🍽️"},
            {"name": "Transportasi", "type": "expense", "icon": "🚗"},
            {"name": "Belanja", "type": "expense", "icon": "🛍️"},
            {"name": "Tagihan", "type": "expense", "icon": "📋"},
            {"name": "Kesehatan", "type": "expense", "icon": "🏥"},
            {"name": "Pendidikan", "type": "expense", "icon": "📚"},
            {"name": "Hiburan", "type": "expense", "icon": "🎬"},
            {"name": "Olahraga", "type": "expense", "icon": "⚽"},
            {"name": "Asuransi", "type": "expense", "icon": "🛡️"},
            {"name": "Investasi", "type": "expense", "icon": "📊"},
            {"name": "Donasi", "type": "expense", "icon": "💝"},
            {"name": "Perbaikan", "type": "expense", "icon": "🔧"},
            {"name": "Pajak", "type": "expense", "icon": "🏛️"},
            {"name": "Lainnya", "type": "expense", "icon": "💸"},
        ]
        
        # Add income categories
        for cat_data in income_categories:
            category = Category(
                name=cat_data["name"],
                type=cat_data["type"],
                icon=cat_data["icon"],
                is_system=True
            )
            db.add(category)
        
        # Add expense categories
        for cat_data in expense_categories:
            category = Category(
                name=cat_data["name"],
                type=cat_data["type"],
                icon=cat_data["icon"],
                is_system=True
            )
            db.add(category)
        
        db.commit()
        print(f"✅ Created {len(income_categories)} income categories")
        print(f"✅ Created {len(expense_categories)} expense categories")
        
    except Exception as e:
        logger.error(f"Error creating default categories: {e}")
        db.rollback()
        raise
    finally:
        db.close()

def upgrade_existing_database():
    """Upgrade existing database schema to new optimized version"""
    print("🔄 Checking for database upgrades...")
    
    try:
        with engine.connect() as conn:
            # Check and add new user columns if they don't exist
            try:
                conn.execute(text("ALTER TABLE users ADD COLUMN language VARCHAR(10) DEFAULT 'id'"))
                print("✅ Added language column to users")
            except Exception:
                pass
            
            try:
                conn.execute(text("ALTER TABLE users ADD COLUMN last_activity DATETIME DEFAULT CURRENT_TIMESTAMP"))
                print("✅ Added last_activity column to users")
            except Exception:
                pass
            
            try:
                conn.execute(text("ALTER TABLE users ADD COLUMN updated_at DATETIME DEFAULT CURRENT_TIMESTAMP"))
                print("✅ Added updated_at column to users")
            except Exception:
                pass
            
            # Check and add new category columns if they don't exist
            try:
                conn.execute(text("ALTER TABLE categories ADD COLUMN is_active BOOLEAN DEFAULT 1"))
                print("✅ Added is_active column to categories")
            except Exception:
                pass
            
            conn.commit()
            print("✅ Database upgrade completed")
    
    except Exception as e:
        logger.error(f"Error upgrading database: {e}")
        print(f"⚠️ Upgrade error (may be normal): {e}")

if __name__ == "__main__":
    try:
        # Try to upgrade existing database first
        upgrade_existing_database()
        
        # Initialize database
        init_database()
        
    except Exception as e:
        print(f"❌ Error initializing database: {e}")
        sys.exit(1)
