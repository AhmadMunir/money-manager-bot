from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean, ForeignKey, Index, text, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    telegram_id = Column(Integer, unique=True, nullable=False, index=True)
    username = Column(String(100), index=True)
    first_name = Column(String(100))
    last_name = Column(String(100))
    timezone = Column(String(50), default='Asia/Jakarta')
    language = Column(String(10), default='id')  # Language preference
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_activity = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True, index=True)
    
    # Relationships with lazy loading for performance
    wallets = relationship("Wallet", back_populates="user", cascade="all, delete-orphan", lazy='dynamic')
    transactions = relationship("Transaction", back_populates="user", cascade="all, delete-orphan", lazy='dynamic')
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_user_telegram_active', 'telegram_id', 'is_active'),
        Index('idx_user_activity', 'last_activity', 'is_active'),
    )
    
    def __repr__(self):
        return f"<User(telegram_id={self.telegram_id}, username={self.username})>"
    
    def get_active_wallets(self):
        """Get user's active wallets with optimized query"""
        return self.wallets.filter_by(is_active=True).order_by(Wallet.name)
    
    def get_total_balance(self):
        """Get total balance across all active wallets"""
        return sum(wallet.balance for wallet in self.get_active_wallets())

class Wallet(Base):
    __tablename__ = 'wallets'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    type = Column(String(50), nullable=False, index=True)  # cash, bank, e-wallet, investment, debt, etc.
    balance = Column(Float, default=0.0, index=True)
    initial_balance = Column(Float, default=0.0)
    currency = Column(String(10), default='IDR')
    description = Column(String(255))
    is_active = Column(Boolean, default=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="wallets")
    transactions_from = relationship("Transaction", foreign_keys="Transaction.from_wallet_id", back_populates="from_wallet", lazy='dynamic')
    transactions_to = relationship("Transaction", foreign_keys="Transaction.to_wallet_id", back_populates="to_wallet", lazy='dynamic')
    
    # Composite indexes for performance
    __table_args__ = (
        Index('idx_wallet_user_active', 'user_id', 'is_active'),
        Index('idx_wallet_user_type', 'user_id', 'type', 'is_active'),
        Index('idx_wallet_balance', 'user_id', 'balance', 'is_active'),
    )
    
    def __repr__(self):
        return f"<Wallet(name={self.name}, balance={self.balance})>"
    
    def update_balance(self, amount, operation='add'):
        """Update wallet balance with proper validation"""
        if operation == 'add':
            self.balance += amount
        elif operation == 'subtract':
            self.balance -= amount
        elif operation == 'set':
            self.balance = amount
        self.updated_at = datetime.utcnow()

class Category(Base):
    __tablename__ = 'categories'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False, index=True)
    type = Column(String(20), nullable=False, index=True)  # income, expense
    icon = Column(String(10))  # emoji icon
    parent_id = Column(Integer, ForeignKey('categories.id', ondelete='SET NULL'))  # for subcategories
    is_system = Column(Boolean, default=False, index=True)  # system categories cannot be deleted
    is_active = Column(Boolean, default=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    parent = relationship("Category", remote_side=[id])
    transactions = relationship("Transaction", back_populates="category", lazy='dynamic')
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_category_type_active', 'type', 'is_active'),
        Index('idx_category_system_active', 'is_system', 'is_active'),
    )
    
    def __repr__(self):
        return f"<Category(name={self.name}, type={self.type})>"

class Transaction(Base):
    __tablename__ = 'transactions'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    type = Column(String(20), nullable=False, index=True)  # income, expense, transfer
    amount = Column(Float, nullable=False, index=True)
    description = Column(String(255))
    category_id = Column(Integer, ForeignKey('categories.id', ondelete='SET NULL'), index=True)
    from_wallet_id = Column(Integer, ForeignKey('wallets.id', ondelete='SET NULL'), index=True)  # for expense and transfer
    to_wallet_id = Column(Integer, ForeignKey('wallets.id', ondelete='SET NULL'), index=True)    # for income and transfer
    transaction_date = Column(DateTime, default=datetime.utcnow, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    notes = Column(String(500))
    
    # Relationships
    user = relationship("User", back_populates="transactions")
    category = relationship("Category", back_populates="transactions")
    from_wallet = relationship("Wallet", foreign_keys=[from_wallet_id])
    to_wallet = relationship("Wallet", foreign_keys=[to_wallet_id])
    
    # Composite indexes for performance
    __table_args__ = (
        Index('idx_transaction_user_date', 'user_id', 'transaction_date'),
        Index('idx_transaction_user_type', 'user_id', 'type'),
        Index('idx_transaction_user_amount', 'user_id', 'amount'),
        Index('idx_transaction_date_type', 'transaction_date', 'type'),
        Index('idx_transaction_wallets', 'from_wallet_id', 'to_wallet_id'),
        Index('idx_transaction_category', 'user_id', 'category_id'),
    )
    
    def __repr__(self):
        return f"<Transaction(type={self.type}, amount={self.amount}, description={self.description})>"

# Database engine and session with optimizations
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///finance_bot.db')

# SQLite optimizations
if 'sqlite' in DATABASE_URL:
    engine = create_engine(
        DATABASE_URL, 
        echo=False,
        pool_pre_ping=True,
        connect_args={
            "check_same_thread": False,
            "timeout": 30
        }
    )
    # Enable WAL mode and other optimizations for SQLite
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA synchronous=NORMAL")
        cursor.execute("PRAGMA cache_size=10000")
        cursor.execute("PRAGMA temp_store=MEMORY")
        cursor.execute("PRAGMA mmap_size=268435456")  # 256MB
        cursor.close()
else:
    engine = create_engine(DATABASE_URL, echo=False, pool_pre_ping=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def create_tables():
    """Create all tables with indexes"""
    Base.metadata.create_all(bind=engine)

def get_db():
    """Get database session with proper cleanup"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_user_by_telegram_id(db, telegram_id: int):
    """Get user by telegram ID with optimized query"""
    return db.query(User).filter(
        User.telegram_id == telegram_id,
        User.is_active == True
    ).first()

def create_or_update_user(db, telegram_user):
    """Create new user or update existing user info"""
    user = get_user_by_telegram_id(db, telegram_user.id)
    
    if not user:
        user = User(
            telegram_id=telegram_user.id,
            username=telegram_user.username,
            first_name=telegram_user.first_name,
            last_name=telegram_user.last_name
        )
        db.add(user)
    else:
        # Update user info
        user.username = telegram_user.username
        user.first_name = telegram_user.first_name
        user.last_name = telegram_user.last_name
        user.last_activity = datetime.utcnow()
    
    db.commit()
    db.refresh(user)
    return user

class Asset(Base):
    __tablename__ = 'assets'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    wallet_id = Column(Integer, ForeignKey('wallets.id', ondelete='CASCADE'), nullable=False, index=True)
    asset_type = Column(String(20), nullable=False, index=True)  # 'saham' or 'kripto'
    symbol = Column(String(20), nullable=False, index=True)  # Stock/crypto symbol
    name = Column(String(100), nullable=False)  # Full name
    quantity = Column(Float, nullable=False, default=0.0)
    buy_price = Column(Float, nullable=False, default=0.0)  # Average buy price
    last_price = Column(Float, default=0.0)  # Current market price
    return_value = Column(Float, default=0.0)  # Calculated return
    return_percent = Column(Float, default=0.0)  # Return percentage
    last_sync = Column(DateTime)  # Last price sync
    is_active = Column(Boolean, default=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", backref="assets")
    wallet = relationship("Wallet", backref="assets")
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_asset_user_active', 'user_id', 'is_active'),
        Index('idx_asset_wallet_active', 'wallet_id', 'is_active'),
        Index('idx_asset_type_symbol', 'asset_type', 'symbol'),
        Index('idx_asset_user_type', 'user_id', 'asset_type', 'is_active'),
    )
    
    def __repr__(self):
        return f"<Asset(symbol={self.symbol}, quantity={self.quantity}, buy_price={self.buy_price})>"
    
    def get_actual_quantity(self):
        """Get actual quantity considering lot size for stocks"""
        if self.asset_type == 'saham':
            return self.quantity * 100  # 1 lot = 100 lembar saham
        return self.quantity
    
    def calculate_return(self):
        """Calculate return amount and percentage"""
        if self.last_price and self.buy_price:
            actual_quantity = self.get_actual_quantity()
            self.return_value = (self.last_price - self.buy_price) * actual_quantity
            self.return_percent = ((self.last_price - self.buy_price) / self.buy_price) * 100
        else:
            self.return_value = 0.0
            self.return_percent = 0.0
    
    def get_current_value(self):
        """Get current market value"""
        actual_quantity = self.get_actual_quantity()
        if self.last_price:
            return self.last_price * actual_quantity
        return self.buy_price * actual_quantity
    
    def get_total_cost(self):
        """Get total purchase cost"""
        actual_quantity = self.get_actual_quantity()
        return self.buy_price * actual_quantity
