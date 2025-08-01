"""
User registration service with comprehensive onboarding flow
"""
from sqlalchemy.orm import Session
from src.models.database import User, get_user_by_telegram_id, SessionLocal
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class UserRegistrationService:
    """Service for handling user registration and onboarding"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def is_user_registered(self, telegram_id: int) -> bool:
        """Check if user is already registered"""
        user = get_user_by_telegram_id(self.db, telegram_id)
        return user is not None
    
    def register_new_user(self, telegram_user, language='id') -> User:
        """Register a new user with comprehensive data collection"""
        logger.info(f"📝 Starting registration for new user: {telegram_user.id}")
        
        try:
            # Create new user with complete information
            new_user = User(
                telegram_id=telegram_user.id,
                username=telegram_user.username,
                first_name=telegram_user.first_name,
                last_name=telegram_user.last_name,
                language=language,
                created_at=datetime.utcnow(),
                last_activity=datetime.utcnow(),
                is_active=True
            )
            
            self.db.add(new_user)
            self.db.commit()
            self.db.refresh(new_user)
            
            logger.info(f"✅ User registered successfully: ID={new_user.id}, Telegram={telegram_user.id}")
            logger.info(f"👤 User details: {telegram_user.first_name} (@{telegram_user.username})")
            
            return new_user
            
        except Exception as e:
            logger.error(f"❌ Failed to register user {telegram_user.id}: {e}")
            self.db.rollback()
            raise
    
    def get_registration_welcome_message(self, user: User) -> str:
        """Generate personalized welcome message for new user"""
        name = user.first_name or "User"
        
        welcome_message = f"""🎉 *Selamat datang di Mon-Man Bot, {name}!*

Terima kasih telah bergabung dengan Mon-Man Bot - asisten keuangan pribadi Anda yang cerdas! 🤖💰

📋 *Informasi Akun Anda:*
👤 Nama: {name}
🆔 ID: {user.telegram_id}
📅 Terdaftar: {user.created_at.strftime('%d %B %Y')}

🚀 *Langkah Selanjutnya:*
1️⃣ Buat kantong pertama Anda (Dompet, Bank, E-Wallet)
2️⃣ Mulai catat transaksi harian
3️⃣ Nikmati laporan keuangan otomatis

💡 *Tips untuk Pemula:*
• Gunakan `/help` untuk panduan lengkap
• Mulai dengan kantong utama (misal: Dompet)
• Catat transaksi secara rutin untuk hasil terbaik

Mari mulai perjalanan finansial Anda! 🎯"""

        return welcome_message
    
    def get_returning_user_message(self, user: User) -> str:
        """Generate personalized message for returning user"""
        name = user.first_name or "User"
        
        # Update last activity
        user.last_activity = datetime.utcnow()
        self.db.commit()
        
        # Calculate days since registration
        days_registered = (datetime.utcnow() - user.created_at).days
        
        return_message = f"""👋 *Selamat datang kembali, {name}!*

Senang melihat Anda lagi di Mon-Man Bot! 😊

📊 *Info Akun:*
📅 Bergabung sejak: {days_registered} hari yang lalu
🕐 Aktivitas terakhir: {user.last_activity.strftime('%d %B %Y, %H:%M')}

Silakan pilih menu di bawah untuk melanjutkan pengelolaan keuangan Anda."""

        return return_message
    
    def log_user_activity(self, user: User, activity: str, details: str = None):
        """Log user activity for analytics and debugging"""
        user.last_activity = datetime.utcnow()
        self.db.commit()
        
        log_message = f"👤 User Activity - ID: {user.telegram_id}, Activity: {activity}"
        if details:
            log_message += f", Details: {details}"
        
        logger.info(log_message)
    
    def get_user_statistics(self, user: User) -> dict:
        """Get user registration and usage statistics"""
        from src.services.user_service import UserService
        
        user_service = UserService(self.db)
        summary = user_service.get_user_summary(user.id)
        
        days_registered = (datetime.utcnow() - user.created_at).days
        
        return {
            'user_id': user.id,
            'telegram_id': user.telegram_id,
            'name': user.first_name,
            'username': user.username,
            'days_registered': days_registered,
            'total_balance': summary['total_balance'],
            'wallet_count': summary['wallet_count'],
            'monthly_income': summary['monthly_income'],
            'monthly_expense': summary['monthly_expense'],
            'last_activity': user.last_activity.strftime('%Y-%m-%d %H:%M:%S') if user.last_activity else None
        }
