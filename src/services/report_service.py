"""
Report service layer for optimized financial reporting per user
"""
from sqlalchemy.orm import Session
from sqlalchemy import and_, func, desc, extract
from src.models.database import User, Wallet, Transaction, Category
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class ReportService:
    """Service class for generating financial reports with performance optimizations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_daily_report(self, user_id: int, target_date: datetime = None):
        """Generate daily financial report for user"""
        if not target_date:
            target_date = datetime.now()
        
        start_of_day = target_date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_day = start_of_day + timedelta(days=1)
        
        # Get daily transactions
        daily_income = self.db.query(func.sum(Transaction.amount)).filter(
            and_(
                Transaction.user_id == user_id,
                Transaction.type == 'income',
                Transaction.transaction_date >= start_of_day,
                Transaction.transaction_date < end_of_day
            )
        ).scalar() or 0.0
        
        daily_expense = self.db.query(func.sum(Transaction.amount)).filter(
            and_(
                Transaction.user_id == user_id,
                Transaction.type == 'expense',
                Transaction.transaction_date >= start_of_day,
                Transaction.transaction_date < end_of_day
            )
        ).scalar() or 0.0
        
        # Get transaction count
        transaction_count = self.db.query(func.count(Transaction.id)).filter(
            and_(
                Transaction.user_id == user_id,
                Transaction.transaction_date >= start_of_day,
                Transaction.transaction_date < end_of_day
            )
        ).scalar() or 0
        
        # Get current total balance
        total_balance = self.db.query(func.sum(Wallet.balance)).filter(
            and_(Wallet.user_id == user_id, Wallet.is_active == True)
        ).scalar() or 0.0
        
        return {
            'date': target_date.strftime('%Y-%m-%d'),
            'daily_income': daily_income,
            'daily_expense': daily_expense,
            'daily_net': daily_income - daily_expense,
            'transaction_count': transaction_count,
            'total_balance': total_balance
        }
    
    def get_weekly_report(self, user_id: int, target_date: datetime = None):
        """Generate weekly financial report for user"""
        if not target_date:
            target_date = datetime.now()
        
        # Get start of week (Monday)
        start_of_week = target_date - timedelta(days=target_date.weekday())
        start_of_week = start_of_week.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_week = start_of_week + timedelta(days=7)
        
        weekly_income = self.db.query(func.sum(Transaction.amount)).filter(
            and_(
                Transaction.user_id == user_id,
                Transaction.type == 'income',
                Transaction.transaction_date >= start_of_week,
                Transaction.transaction_date < end_of_week
            )
        ).scalar() or 0.0
        
        weekly_expense = self.db.query(func.sum(Transaction.amount)).filter(
            and_(
                Transaction.user_id == user_id,
                Transaction.type == 'expense',
                Transaction.transaction_date >= start_of_week,
                Transaction.transaction_date < end_of_week
            )
        ).scalar() or 0.0
        
        # Get previous week for comparison
        prev_start = start_of_week - timedelta(days=7)
        prev_end = start_of_week
        
        prev_weekly_expense = self.db.query(func.sum(Transaction.amount)).filter(
            and_(
                Transaction.user_id == user_id,
                Transaction.type == 'expense',
                Transaction.transaction_date >= prev_start,
                Transaction.transaction_date < prev_end
            )
        ).scalar() or 0.0
        
        # Calculate WoW change
        wow_change = 0.0
        if prev_weekly_expense > 0:
            wow_change = ((weekly_expense - prev_weekly_expense) / prev_weekly_expense) * 100
        
        return {
            'week_start': start_of_week.strftime('%Y-%m-%d'),
            'week_end': (end_of_week - timedelta(days=1)).strftime('%Y-%m-%d'),
            'weekly_income': weekly_income,
            'weekly_expense': weekly_expense,
            'weekly_net': weekly_income - weekly_expense,
            'prev_weekly_expense': prev_weekly_expense,
            'wow_change': wow_change
        }
    
    def get_monthly_report(self, user_id: int, target_date: datetime = None):
        """Generate monthly financial report for user"""
        if not target_date:
            target_date = datetime.now()
        
        start_of_month = target_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        # Calculate end of month
        if target_date.month == 12:
            end_of_month = start_of_month.replace(year=target_date.year + 1, month=1)
        else:
            end_of_month = start_of_month.replace(month=target_date.month + 1)
        
        monthly_income = self.db.query(func.sum(Transaction.amount)).filter(
            and_(
                Transaction.user_id == user_id,
                Transaction.type == 'income',
                Transaction.transaction_date >= start_of_month,
                Transaction.transaction_date < end_of_month
            )
        ).scalar() or 0.0
        
        monthly_expense = self.db.query(func.sum(Transaction.amount)).filter(
            and_(
                Transaction.user_id == user_id,
                Transaction.type == 'expense',
                Transaction.transaction_date >= start_of_month,
                Transaction.transaction_date < end_of_month
            )
        ).scalar() or 0.0
        
        # Get previous month for comparison
        if start_of_month.month == 1:
            prev_start = start_of_month.replace(year=start_of_month.year - 1, month=12)
        else:
            prev_start = start_of_month.replace(month=start_of_month.month - 1)
        
        prev_monthly_expense = self.db.query(func.sum(Transaction.amount)).filter(
            and_(
                Transaction.user_id == user_id,
                Transaction.type == 'expense',
                Transaction.transaction_date >= prev_start,
                Transaction.transaction_date < start_of_month
            )
        ).scalar() or 0.0
        
        # Calculate MoM change
        mom_change = 0.0
        if prev_monthly_expense > 0:
            mom_change = ((monthly_expense - prev_monthly_expense) / prev_monthly_expense) * 100
        
        # Get spending by category for current month
        category_breakdown = self.db.query(
            Category.name,
            Category.icon,
            func.sum(Transaction.amount).label('total_amount')
        ).join(
            Transaction, Transaction.category_id == Category.id
        ).filter(
            and_(
                Transaction.user_id == user_id,
                Transaction.type == 'expense',
                Transaction.transaction_date >= start_of_month,
                Transaction.transaction_date < end_of_month
            )
        ).group_by(Category.id, Category.name, Category.icon).order_by(desc('total_amount')).limit(10).all()
        
        return {
            'month': start_of_month.strftime('%Y-%m'),
            'monthly_income': monthly_income,
            'monthly_expense': monthly_expense,
            'monthly_net': monthly_income - monthly_expense,
            'prev_monthly_expense': prev_monthly_expense,
            'mom_change': mom_change,
            'category_breakdown': [
                {
                    'name': cat.name,
                    'icon': cat.icon,
                    'amount': float(cat.total_amount),
                    'percentage': (float(cat.total_amount) / monthly_expense * 100) if monthly_expense > 0 else 0
                }
                for cat in category_breakdown
            ]
        }
    
    def get_spending_trends(self, user_id: int, months: int = 6):
        """Get spending trends over specified months"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=months * 30)
        
        # Get monthly spending data
        monthly_data = self.db.query(
            extract('year', Transaction.transaction_date).label('year'),
            extract('month', Transaction.transaction_date).label('month'),
            func.sum(Transaction.amount).label('total_expense')
        ).filter(
            and_(
                Transaction.user_id == user_id,
                Transaction.type == 'expense',
                Transaction.transaction_date >= start_date,
                Transaction.transaction_date <= end_date
            )
        ).group_by(
            extract('year', Transaction.transaction_date),
            extract('month', Transaction.transaction_date)
        ).order_by('year', 'month').all()
        
        return [
            {
                'period': f"{int(data.year)}-{int(data.month):02d}",
                'amount': float(data.total_expense)
            }
            for data in monthly_data
        ]
    
    def get_wallet_breakdown(self, user_id: int):
        """Get current wallet balance breakdown"""
        wallets = self.db.query(Wallet).filter(
            and_(Wallet.user_id == user_id, Wallet.is_active == True)
        ).order_by(desc(Wallet.balance)).all()
        
        total_balance = sum(wallet.balance for wallet in wallets)
        
        return {
            'total_balance': total_balance,
            'wallets': [
                {
                    'name': wallet.name,
                    'type': wallet.type,
                    'balance': wallet.balance,
                    'percentage': (wallet.balance / total_balance * 100) if total_balance > 0 else 0
                }
                for wallet in wallets
            ]
        }
    
    def get_recent_transactions(self, user_id: int, limit: int = 10):
        """Get recent transactions for user"""
        transactions = self.db.query(Transaction).filter(
            Transaction.user_id == user_id
        ).order_by(desc(Transaction.transaction_date)).limit(limit).all()
        
        result = []
        for trans in transactions:
            transaction_data = {
                'id': trans.id,
                'type': trans.type,
                'amount': trans.amount,
                'description': trans.description,
                'date': trans.transaction_date.strftime('%Y-%m-%d %H:%M'),
                'category': trans.category.name if trans.category else None,
                'from_wallet': trans.from_wallet.name if trans.from_wallet else None,
                'to_wallet': trans.to_wallet.name if trans.to_wallet else None
            }
            result.append(transaction_data)
        
        return result
