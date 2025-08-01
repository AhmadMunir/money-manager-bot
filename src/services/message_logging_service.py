"""
Message logging service for comprehensive bot interaction tracking
"""
import logging
from datetime import datetime
from typing import Optional
import json

logger = logging.getLogger(__name__)

class MessageLoggingService:
    """Service for logging all bot interactions and messages"""
    
    def __init__(self):
        # Create separate logger for message tracking
        self.message_logger = logging.getLogger('message_tracker')
        self.message_logger.setLevel(logging.INFO)
        
        # Create file handler for message logs
        if not self.message_logger.handlers:
            message_handler = logging.FileHandler('message_logs.log', encoding='utf-8')
            message_formatter = logging.Formatter(
                '%(asctime)s - MESSAGE - %(message)s'
            )
            message_handler.setFormatter(message_formatter)
            self.message_logger.addHandler(message_handler)
    
    def log_incoming_message(self, message):
        """Log incoming message from user"""
        try:
            user_info = {
                'user_id': message.from_user.id,
                'username': message.from_user.username,
                'first_name': message.from_user.first_name,
                'last_name': message.from_user.last_name
            }
            
            message_info = {
                'type': 'incoming_message',
                'chat_id': message.chat.id,
                'message_id': message.message_id,
                'text': message.text,
                'timestamp': datetime.now().isoformat(),
                'user': user_info
            }
            
            self.message_logger.info(f"📨 INCOMING: {json.dumps(message_info, ensure_ascii=False)}")
            
            # Also log to main logger with summary
            logger.info(f"📨 Message from @{message.from_user.username} ({message.from_user.id}): {message.text[:100]}...")
            
        except Exception as e:
            logger.error(f"❌ Error logging incoming message: {e}")
    
    def log_outgoing_message(self, chat_id: int, text: str, user_id: int = None, message_type: str = "reply"):
        """Log outgoing message to user"""
        try:
            message_info = {
                'type': 'outgoing_message',
                'message_type': message_type,
                'chat_id': chat_id,
                'user_id': user_id,
                'text': text,
                'timestamp': datetime.now().isoformat()
            }
            
            self.message_logger.info(f"📤 OUTGOING: {json.dumps(message_info, ensure_ascii=False)}")
            
            # Also log to main logger with summary
            logger.info(f"📤 Reply to user {user_id} ({chat_id}): {text[:100]}...")
            
        except Exception as e:
            logger.error(f"❌ Error logging outgoing message: {e}")
    
    def log_callback_query(self, call):
        """Log callback query from inline keyboards"""
        try:
            user_info = {
                'user_id': call.from_user.id,
                'username': call.from_user.username,
                'first_name': call.from_user.first_name
            }
            
            callback_info = {
                'type': 'callback_query',
                'callback_data': call.data,
                'message_id': call.message.message_id if call.message else None,
                'chat_id': call.message.chat.id if call.message else None,
                'timestamp': datetime.now().isoformat(),
                'user': user_info
            }
            
            self.message_logger.info(f"🔘 CALLBACK: {json.dumps(callback_info, ensure_ascii=False)}")
            
            # Also log to main logger
            logger.info(f"🔘 Callback from @{call.from_user.username} ({call.from_user.id}): {call.data}")
            
        except Exception as e:
            logger.error(f"❌ Error logging callback query: {e}")
    
    def log_command_execution(self, user_id: int, command: str, success: bool = True, error: str = None):
        """Log command execution results"""
        try:
            command_info = {
                'type': 'command_execution',
                'user_id': user_id,
                'command': command,
                'success': success,
                'error': error,
                'timestamp': datetime.now().isoformat()
            }
            
            self.message_logger.info(f"⚙️ COMMAND: {json.dumps(command_info, ensure_ascii=False)}")
            
            # Also log to main logger
            status = "✅ SUCCESS" if success else "❌ FAILED"
            logger.info(f"⚙️ Command {command} for user {user_id}: {status}")
            if error:
                logger.error(f"❌ Command error: {error}")
                
        except Exception as e:
            logger.error(f"❌ Error logging command execution: {e}")
    
    def log_user_registration(self, user_id: int, username: str, first_name: str):
        """Log new user registration"""
        try:
            registration_info = {
                'type': 'user_registration',
                'user_id': user_id,
                'username': username,
                'first_name': first_name,
                'timestamp': datetime.now().isoformat()
            }
            
            self.message_logger.info(f"🆕 REGISTRATION: {json.dumps(registration_info, ensure_ascii=False)}")
            
            # Also log to main logger
            logger.info(f"🆕 New user registered: @{username} ({first_name}) - ID: {user_id}")
            
        except Exception as e:
            logger.error(f"❌ Error logging user registration: {e}")
    
    def log_transaction_created(self, user_id: int, transaction_type: str, amount: float, description: str):
        """Log transaction creation"""
        try:
            transaction_info = {
                'type': 'transaction_created',
                'user_id': user_id,
                'transaction_type': transaction_type,
                'amount': amount,
                'description': description,
                'timestamp': datetime.now().isoformat()
            }
            
            self.message_logger.info(f"💰 TRANSACTION: {json.dumps(transaction_info, ensure_ascii=False)}")
            
            # Also log to main logger
            logger.info(f"💰 Transaction created by user {user_id}: {transaction_type} - {amount} - {description}")
            
        except Exception as e:
            logger.error(f"❌ Error logging transaction: {e}")
    
    def log_wallet_created(self, user_id: int, wallet_name: str, wallet_type: str, initial_balance: float):
        """Log wallet creation"""
        try:
            wallet_info = {
                'type': 'wallet_created',
                'user_id': user_id,
                'wallet_name': wallet_name,
                'wallet_type': wallet_type,
                'initial_balance': initial_balance,
                'timestamp': datetime.now().isoformat()
            }
            
            self.message_logger.info(f"🏦 WALLET: {json.dumps(wallet_info, ensure_ascii=False)}")
            
            # Also log to main logger
            logger.info(f"🏦 Wallet created by user {user_id}: {wallet_name} ({wallet_type}) - Balance: {initial_balance}")
            
        except Exception as e:
            logger.error(f"❌ Error logging wallet creation: {e}")
    
    def log_report_generated(self, user_id: int, report_type: str, date_range: str = None):
        """Log report generation"""
        try:
            report_info = {
                'type': 'report_generated',
                'user_id': user_id,
                'report_type': report_type,
                'date_range': date_range,
                'timestamp': datetime.now().isoformat()
            }
            
            self.message_logger.info(f"📊 REPORT: {json.dumps(report_info, ensure_ascii=False)}")
            
            # Also log to main logger
            logger.info(f"📊 Report generated by user {user_id}: {report_type} - {date_range}")
            
        except Exception as e:
            logger.error(f"❌ Error logging report generation: {e}")
    
    def log_error_occurred(self, user_id: int, error_type: str, error_message: str, context: str = None):
        """Log error that occurred during user interaction"""
        try:
            error_info = {
                'type': 'error_occurred',
                'user_id': user_id,
                'error_type': error_type,
                'error_message': error_message,
                'context': context,
                'timestamp': datetime.now().isoformat()
            }
            
            self.message_logger.error(f"💥 ERROR: {json.dumps(error_info, ensure_ascii=False)}")
            
            # Also log to main logger
            logger.error(f"💥 Error for user {user_id} in {context}: {error_type} - {error_message}")
            
        except Exception as e:
            logger.error(f"❌ Error logging error occurrence: {e}")

# Global instance
message_logger = MessageLoggingService()
