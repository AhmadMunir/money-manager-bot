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
    print("[INIT] Creating database tables with optimizations...")
    create_tables()
    
    # Enable SQLite optimizations
    if 'sqlite' in str(engine.url):
        print("[PERF] Applying SQLite performance optimizations...")
        with engine.connect() as conn:
            conn.execute(text("PRAGMA journal_mode=WAL"))
            conn.execute(text("PRAGMA synchronous=NORMAL"))
            conn.execute(text("PRAGMA cache_size=10000"))
            conn.execute(text("PRAGMA temp_store=MEMORY"))
            conn.execute(text("PRAGMA mmap_size=268435456"))  # 256MB
            conn.commit()
    
    print("[DATA] Creating default categories...")
    create_default_categories()
    
    print("[OK] Enhanced database initialization completed!")

def create_default_categories():
    """Create default income and expense categories"""
    db = SessionLocal()
    try:
        # Check if categories already exist
        existing_categories = db.query(Category).filter(Category.is_system == True).count()
        if existing_categories > 0:
            print("[SKIP] Default categories already exist, skipping...")
            return
        
        # Income categories
        income_categories = [
            {"name": "Gaji", "type": "income", "icon": "[WORK]"},
            {"name": "Bonus", "type": "income", "icon": "[GIFT]"},
            {"name": "Freelance", "type": "income", "icon": "[COMP]"},
            {"name": "Investasi", "type": "income", "icon": "[STOCK]"},
            {"name": "Hadiah", "type": "income", "icon": "[PARTY]"},
            {"name": "Penjualan", "type": "income", "icon": "[SHOP]"},
            {"name": "Lainnya", "type": "income", "icon": "[MONEY]"},
        ]
        
        # Expense categories
        expense_categories = [
            {"name": "Makanan", "type": "expense", "icon": "[FOOD]"},
            {"name": "Transportasi", "type": "expense", "icon": "[CAR]"},
            {"name": "Belanja", "type": "expense", "icon": "[SHOP]"},
            {"name": "Tagihan", "type": "expense", "icon": "[BILL]"},
            {"name": "Kesehatan", "type": "expense", "icon": "[HEALTH]"},
            {"name": "Pendidikan", "type": "expense", "icon": "[BOOK]"},
            {"name": "Hiburan", "type": "expense", "icon": "[FUN]"},
            {"name": "Olahraga", "type": "expense", "icon": "[SPORT]"},
            {"name": "Asuransi", "type": "expense", "icon": "[INSUR]"},
            {"name": "Investasi", "type": "expense", "icon": "[INVEST]"},
            {"name": "Donasi", "type": "expense", "icon": "[GIVE]"},
            {"name": "Perbaikan", "type": "expense", "icon": "[FIX]"},
            {"name": "Pajak", "type": "expense", "icon": "[TAX]"},
            {"name": "Lainnya", "type": "expense", "icon": "[OTHER]"},
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
        print(f"[OK] Created {len(income_categories)} income categories")
        print(f"[OK] Created {len(expense_categories)} expense categories")
        
    except Exception as e:
        logger.error(f"Error creating default categories: {e}")
        db.rollback()
        raise
    finally:
        db.close()

def upgrade_existing_database():
    """Upgrade existing database schema to new optimized version"""
    print("[UPGRADE] Checking for database upgrades...")
    
    try:
        with engine.connect() as conn:
            # Check and add new user columns if they don't exist
            try:
                conn.execute(text("ALTER TABLE users ADD COLUMN language VARCHAR(10) DEFAULT 'id'"))
                print("[OK] Added language column to users")
            except Exception:
                pass
            
            try:
                conn.execute(text("ALTER TABLE users ADD COLUMN last_activity DATETIME DEFAULT CURRENT_TIMESTAMP"))
                print("[OK] Added last_activity column to users")
            except Exception:
                pass
            
            try:
                conn.execute(text("ALTER TABLE users ADD COLUMN updated_at DATETIME DEFAULT CURRENT_TIMESTAMP"))
                print("[OK] Added updated_at column to users")
            except Exception:
                pass
            
            # Check and add new category columns if they don't exist
            try:
                conn.execute(text("ALTER TABLE categories ADD COLUMN is_active BOOLEAN DEFAULT 1"))
                print("[OK] Added is_active column to categories")
            except Exception:
                pass
            
            conn.commit()
            print("[OK] Database upgrade completed")
    
    except Exception as e:
        logger.error(f"Error upgrading database: {e}")
        print(f"[WARN] Upgrade error (may be normal): {e}")

if __name__ == "__main__":
    try:
        # Try to upgrade existing database first
        upgrade_existing_database()
        
        # Initialize database
        init_database()
        
    except Exception as e:
        print(f"[ERROR] Error initializing database: {e}")
        sys.exit(1)
