import telebot
import os
import logging
from dotenv import load_dotenv
from datetime import datetime

from src.models.database import create_tables
from src.handlers.start_handler import register_start_handlers
from src.handlers.wallet_handler import register_wallet_handlers
from src.handlers.transaction_handler import register_transaction_handlers  
from src.handlers.report_handler import register_report_handlers
from src.services.scheduler_service import SchedulerService
from src.services.message_logging_service import message_logger
from migrations.init_db_enhanced import init_database, upgrade_existing_database

# Load environment variables
load_dotenv()

# Configure enhanced logging with detailed format for debugging and monitoring
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(funcName)s() - %(message)s',
    handlers=[
        logging.FileHandler('bot.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class EnhancedFinanceBotApp:
    """Enhanced Finance Bot with user isolation and performance optimizations"""
    
    def __init__(self):
        self.bot_token = os.getenv('BOT_TOKEN')
        if not self.bot_token:
            raise ValueError("BOT_TOKEN not found in environment variables")
        
        self.bot = telebot.TeleBot(self.bot_token)
        self.scheduler = SchedulerService()
        
        # Initialize enhanced database with user isolation and performance optimizations
        logger.info("🔧 Initializing enhanced database system...")
        try:
            upgrade_existing_database()
            init_database()
        except Exception as e:
            logger.error(f"Database initialization failed: {e}")
            raise
        
        # Register handlers
        self._register_handlers()
        
        logger.info("✅ Enhanced Finance Bot initialized successfully with user isolation")
    
    def _register_handlers(self):
        """Register all command and message handlers with comprehensive logging"""
        logger.info("📝 Registering bot handlers with message logging...")
        
        # Register handlers
        register_start_handlers(self.bot)
        register_wallet_handlers(self.bot)
        register_transaction_handlers(self.bot)
        register_report_handlers(self.bot)
        
        # Register global message handler for logging
        @self.bot.message_handler(content_types=['text'])
        def log_all_messages(message):
            """Log all incoming text messages for monitoring"""
            if not message.text.startswith('/'):  # Don't double-log commands
                message_logger.log_incoming_message(message)
        
        logger.info("✅ All handlers registered successfully with message logging")
        
        # Log available commands and features
        logger.info("🤖 Available commands: /start, /help, /menu, /status")
        logger.info("💰 Features: Multi-user wallets, transactions, reports with full data isolation")
        logger.info("📝 Message logging: ALL interactions will be logged to message_logs.log")
    
    def start_polling(self):
        """Start the bot with enhanced error handling and performance monitoring"""
        try:
            logger.info("🚀 Starting Enhanced Mon-Man Bot...")
            logger.info("👥 Multi-user support: ENABLED")
            logger.info("🔒 Data isolation: ENABLED") 
            logger.info("⚡ Performance optimizations: ENABLED")
            logger.info("📊 Enhanced reporting: ENABLED")
            
            # Start scheduler for automated reports
            self.scheduler.start()
            logger.info("📅 Scheduler service started")
            
            # Start bot polling with enhanced settings
            logger.info("🎯 Bot is ready to handle requests...")
            self.bot.infinity_polling(
                timeout=60,
                long_polling_timeout=60,
                logger_level=logging.INFO,
                allowed_updates=['message', 'callback_query'],
                none_stop=True
            )
            
        except Exception as e:
            logger.error(f"❌ Error starting bot: {e}")
            raise
    
    def stop(self):
        """Stop the bot and scheduler gracefully"""
        logger.info("🛑 Stopping Enhanced Finance Bot...")
        try:
            self.scheduler.stop()
            logger.info("📅 Scheduler stopped")
            
            self.bot.stop_polling()
            logger.info("🤖 Bot polling stopped")
            
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")

def main():
    """Main entry point for Enhanced Finance Bot"""
    try:
        logger.info("=" * 60)
        logger.info("🏦 MON-MAN ENHANCED FINANCE BOT")
        logger.info("=" * 60)
        logger.info("🔹 Version: 2.0 Enhanced")
        logger.info("🔹 Features: Multi-user, Performance Optimized")
        logger.info("🔹 Database: SQLite with WAL mode")
        logger.info("🔹 User Isolation: Complete data separation")
        logger.info("=" * 60)
        
        app = EnhancedFinanceBotApp()
        app.start_polling()
        
    except KeyboardInterrupt:
        logger.info("🛑 Bot stopped by user (Ctrl+C)")
    except ValueError as e:
        logger.error(f"❌ Configuration error: {e}")
        logger.error("💡 Please check your .env file and ensure BOT_TOKEN is set")
    except Exception as e:
        logger.error(f"💥 Fatal error: {e}")
        raise
    finally:
        logger.info("👋 Enhanced Finance Bot shutdown complete")

if __name__ == "__main__":
    main()
