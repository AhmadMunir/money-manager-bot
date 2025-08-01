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
from migrations.init_db_enhanced import init_database, upgrade_existing_database

# Load environment variables
load_dotenv()

# Configure logging with more detailed format
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
    handlers=[
        logging.FileHandler('bot.log'),
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
        
        # Create database tables and initialize default data
        init_database()
        
        # Register handlers
        self._register_handlers()
        
        logger.info("Finance Bot initialized successfully")
    
    def _register_handlers(self):
        """Register all command and message handlers"""
        register_start_handlers(self.bot)
        register_wallet_handlers(self.bot)
        register_transaction_handlers(self.bot)
        register_report_handlers(self.bot)
    
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
        self.scheduler.stop()
        self.bot.stop_polling()

def main():
    """Main entry point"""
    try:
        app = FinanceBotApp()
        app.start_polling()
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        raise

if __name__ == "__main__":
    main()
