"""
User service layer for optimized user management and data isolation
"""
from sqlalchemy.orm import Session
from sqlalchemy import and_, func, desc
from src.models.database import User, Wallet, Transaction, Category, get_user_by_telegram_id, create_or_update_user
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class UserService:
    """Service class for user-related operations with performance optimizations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_or_create_user(self, telegram_user) -> User:
        """Get existing user or create new one"""
        return create_or_update_user(self.db, telegram_user)
    
    def get_user_wallets(self, user_id: int, active_only: bool = True):
        """Get user's wallets with optimized query"""
        query = self.db.query(Wallet).filter(Wallet.user_id == user_id)
        
        if active_only:
            query = query.filter(Wallet.is_active == True)
        
        return query.order_by(Wallet.name).all()
    
    def get_user_wallet_by_id(self, user_id: int, wallet_id: int):
        """Get specific wallet for user with validation"""
        return self.db.query(Wallet).filter(
            and_(
                Wallet.id == wallet_id,
                Wallet.user_id == user_id,
                Wallet.is_active == True
            )
        ).first()
    
    def get_user_wallet_by_name(self, user_id: int, wallet_name: str):
        """Get wallet by name for specific user"""
        return self.db.query(Wallet).filter(
            and_(
                Wallet.user_id == user_id,
                Wallet.name.ilike(f"%{wallet_name}%"),
                Wallet.is_active == True
            )
        ).first()
    
    def create_wallet(self, user_id: int, name: str, wallet_type: str, initial_balance: float = 0.0, description: str = None):
        """Create new wallet for user"""
        wallet = Wallet(
            user_id=user_id,
            name=name,
            type=wallet_type,
            balance=initial_balance,
            initial_balance=initial_balance,
            description=description
        )
        
        self.db.add(wallet)
        self.db.commit()
        self.db.refresh(wallet)
        return wallet
    
    def update_wallet_balance(self, wallet_id: int, amount: float, operation: str = 'add'):
        """Update wallet balance with proper validation"""
        wallet = self.db.query(Wallet).filter(Wallet.id == wallet_id).first()
        if wallet:
            wallet.update_balance(amount, operation)
            self.db.commit()
            return wallet
        return None
    
    def get_user_transactions(self, user_id: int, limit: int = 50, offset: int = 0, 
                            transaction_type: str = None, start_date: datetime = None, end_date: datetime = None):
        """Get user's transactions with filtering and pagination"""
        query = self.db.query(Transaction).filter(Transaction.user_id == user_id)
        
        if transaction_type:
            query = query.filter(Transaction.type == transaction_type)
        
        if start_date:
            query = query.filter(Transaction.transaction_date >= start_date)
        
        if end_date:
            query = query.filter(Transaction.transaction_date <= end_date)
        
        return query.order_by(desc(Transaction.transaction_date)).offset(offset).limit(limit).all()
    
    def create_transaction(self, user_id: int, transaction_type: str, amount: float, 
                          description: str = None, category_id: int = None,
                          from_wallet_id: int = None, to_wallet_id: int = None,
                          transaction_date: datetime = None):
        """Create new transaction with wallet balance updates"""
        if not transaction_date:
            transaction_date = datetime.utcnow()
        
        # Create transaction record
        transaction = Transaction(
            user_id=user_id,
            type=transaction_type,
            amount=amount,
            description=description,
            category_id=category_id,
            from_wallet_id=from_wallet_id,
            to_wallet_id=to_wallet_id,
            transaction_date=transaction_date
        )
        
        self.db.add(transaction)
        
        # Update wallet balances
        if transaction_type == 'income' and to_wallet_id:
            self.update_wallet_balance(to_wallet_id, amount, 'add')
        elif transaction_type == 'expense' and from_wallet_id:
            self.update_wallet_balance(from_wallet_id, amount, 'subtract')
        elif transaction_type == 'transfer' and from_wallet_id and to_wallet_id:
            self.update_wallet_balance(from_wallet_id, amount, 'subtract')
            self.update_wallet_balance(to_wallet_id, amount, 'add')
        
        self.db.commit()
        self.db.refresh(transaction)
        return transaction
    
    def get_user_summary(self, user_id: int):
        """Get user's financial summary with optimized queries"""
        # Get total balance
        total_balance = self.db.query(func.sum(Wallet.balance)).filter(
            and_(Wallet.user_id == user_id, Wallet.is_active == True)
        ).scalar() or 0.0
        
        # Get wallet count
        wallet_count = self.db.query(func.count(Wallet.id)).filter(
            and_(Wallet.user_id == user_id, Wallet.is_active == True)
        ).scalar() or 0
        
        # Get this month's transactions
        start_of_month = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        monthly_income = self.db.query(func.sum(Transaction.amount)).filter(
            and_(
                Transaction.user_id == user_id,
                Transaction.type == 'income',
                Transaction.transaction_date >= start_of_month
            )
        ).scalar() or 0.0
        
        monthly_expense = self.db.query(func.sum(Transaction.amount)).filter(
            and_(
                Transaction.user_id == user_id,
                Transaction.type == 'expense',
                Transaction.transaction_date >= start_of_month
            )
        ).scalar() or 0.0
        
        return {
            'total_balance': total_balance,
            'wallet_count': wallet_count,
            'monthly_income': monthly_income,
            'monthly_expense': monthly_expense,
            'monthly_net': monthly_income - monthly_expense
        }
    
    def get_spending_by_category(self, user_id: int, start_date: datetime, end_date: datetime):
        """Get spending breakdown by category for user"""
        return self.db.query(
            Category.name,
            Category.icon,
            func.sum(Transaction.amount).label('total_amount')
        ).join(
            Transaction, Transaction.category_id == Category.id
        ).filter(
            and_(
                Transaction.user_id == user_id,
                Transaction.type == 'expense',
                Transaction.transaction_date >= start_date,
                Transaction.transaction_date <= end_date
            )
        ).group_by(Category.id, Category.name, Category.icon).order_by(desc('total_amount')).all()
    
    def delete_wallet(self, user_id: int, wallet_id: int):
        """Soft delete wallet (mark as inactive) with validation"""
        wallet = self.get_user_wallet_by_id(user_id, wallet_id)
        if wallet:
            wallet.is_active = False
            wallet.updated_at = datetime.utcnow()
            self.db.commit()
            return True
        return False
