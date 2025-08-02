import telebot
import os
import logging
import atexit
from dotenv import load_dotenv

from src.handlers.start_handler import register_start_handlers
from src.handlers.wallet_handler import register_wallet_handlers
from src.handlers.transaction_handler import register_transaction_handlers  
from src.handlers.report_handler import register_report_handlers
from src.handlers.asset_handler import register_asset_handlers
from src.services.scheduler_service import SchedulerService
from migrations.init_db_enhanced import init_database
from scripts.auto_backup import AutoBackupIntegration

# Load environment variables
load_dotenv()

# Configure logging with more detailed format
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
    handlers=[
        logging.FileHandler('logs/bot.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class EnhancedFinanceBotApp:
    def __init__(self):
        self.bot_token = os.getenv('BOT_TOKEN')
        if not self.bot_token:
            raise ValueError("BOT_TOKEN not found in environment variables")
        
        self.bot = telebot.TeleBot(self.bot_token)
        self.scheduler = SchedulerService()
        self.auto_backup = AutoBackupIntegration()
        
        # Create pre-startup backup
        logger.info("Creating pre-startup backup...")
        self.auto_backup.backup_before_bot_restart()
        
        # Create database tables and initialize default data
        init_database()
        
        # Register handlers
        self._register_handlers()
        
        # Register cleanup on exit
        atexit.register(self._cleanup_on_exit)
        
        logger.info("Finance Bot initialized successfully")
    
    def _register_handlers(self):
        """Register all command and message handlers"""
        register_start_handlers(self.bot)
        register_wallet_handlers(self.bot)
        register_transaction_handlers(self.bot)
        register_report_handlers(self.bot)
        register_asset_handlers(self.bot)
    
    def start_polling(self):
        """Start the bot with polling"""
        try:
            logger.info("Starting bot polling...")
            # Start scheduler for automated reports
            self.scheduler.start()
            
            # Start bot polling
            self.bot.infinity_polling(none_stop=True)
        except Exception as e:
            logger.error(f"Error starting bot: {e}")
            raise
    
    def stop(self):
        """Stop the bot and scheduler"""
        logger.info("Stopping bot...")
        
        # Create backup before shutdown
        logger.info("Creating backup before shutdown...")
        self.auto_backup.backup_before_bot_restart()
        
        self.scheduler.stop()
        self.bot.stop_polling()
    
    def _cleanup_on_exit(self):
        """Cleanup function called on exit"""
        logger.info("Bot shutting down - creating final backup...")
        try:
            self.auto_backup.backup_before_bot_restart()
        except Exception as e:
            logger.error(f"Failed to create shutdown backup: {e}")

def main():
    """Main entry point"""
    try:
        app = EnhancedFinanceBotApp()
        app.start_polling()
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        raise

if __name__ == "__main__":
    main()
