"""
Database initialization and default data
"""
import os
import sys

# Add the parent directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.models.database import SessionLocal, Category, create_tables
import logging

logger = logging.getLogger(__name__)

def init_database():
    """Initialize database with tables and default data"""
    try:
        # Create all tables
        create_tables()
        logger.info("Database tables created successfully")
        
        # Add default categories
        add_default_categories()
        logger.info("Default categories added successfully")
        
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        raise

def add_default_categories():
    """Add default income and expense categories"""
    db = SessionLocal()
    
    try:
        # Check if categories already exist
        existing_categories = db.query(Category).first()
        if existing_categories:
            logger.info("Categories already exist, skipping default category creation")
            return
        
        # Default income categories
        income_categories = [
            {"name": "Gaji", "type": "income", "icon": "💰", "is_system": True},
            {"name": "Bisnis", "type": "income", "icon": "💼", "is_system": True},
            {"name": "Hadiah", "type": "income", "icon": "🎁", "is_system": True},
            {"name": "Hasil Investasi", "type": "income", "icon": "📈", "is_system": True},
            {"name": "Sewa", "type": "income", "icon": "🏠", "is_system": True},
            {"name": "Pemasukan Lainnya", "type": "income", "icon": "🎯", "is_system": True}
        ]
        
        # Default expense categories
        expense_categories = [
            {"name": "Makanan", "type": "expense", "icon": "🍽️", "is_system": True},
            {"name": "Rumah Tangga", "type": "expense", "icon": "🏠", "is_system": True},
            {"name": "Transportasi", "type": "expense", "icon": "🚗", "is_system": True},
            {"name": "Belanja", "type": "expense", "icon": "👕", "is_system": True},
            {"name": "Kesehatan", "type": "expense", "icon": "🏥", "is_system": True},
            {"name": "Pendidikan", "type": "expense", "icon": "📚", "is_system": True},
            {"name": "Hiburan", "type": "expense", "icon": "🎬", "is_system": True},
            {"name": "Pengeluaran Lainnya", "type": "expense", "icon": "🎯", "is_system": True}
        ]
        
        # Add all categories
        all_categories = income_categories + expense_categories
        
        for cat_data in all_categories:
            category = Category(**cat_data)
            db.add(category)
        
        db.commit()
        logger.info(f"Added {len(all_categories)} default categories")
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error adding default categories: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    init_database()
