import telebot
from telebot import types
from datetime import datetime
from sqlalchemy.orm import sessionmaker
from src.models.database import SessionLocal
from src.services.user_service import UserService
from src.services.registration_service import UserRegistrationService
from src.services.report_service import ReportService
from src.services.message_logging_service import message_logger
from src.utils.keyboards import create_main_menu, create_back_button
from src.utils.helpers import format_currency_idr, safe_answer_callback_query
import logging

logger = logging.getLogger(__name__)

def register_start_handlers(bot):
    """Register handlers for start command and main menu"""
    
    @bot.message_handler(commands=['start'])
    def start_command(message):
        """Handle /start command with comprehensive user registration"""
        # Log incoming message
        message_logger.log_incoming_message(message)
        
        try:
            # Create database session
            db = SessionLocal()
            try:
                # Initialize services
                user_service = UserService(db)
                registration_service = UserRegistrationService(db)
                
                # Check if user is already registered
                is_registered = registration_service.is_user_registered(message.from_user.id)
                
                if not is_registered:
                    # Register new user
                    logger.info(f"🆕 New user detected: {message.from_user.id} (@{message.from_user.username})")
                    message_logger.log_user_registration(
                        message.from_user.id,
                        message.from_user.username,
                        message.from_user.first_name
                    )
                    
                    user = registration_service.register_new_user(message.from_user)
                    welcome_text = registration_service.get_registration_welcome_message(user)
                    
                    # Log successful registration
                    registration_service.log_user_activity(user, "user_registered", "First time registration")
                    
                else:
                    # Existing user
                    user = user_service.get_or_create_user(message.from_user)
                    welcome_text = registration_service.get_returning_user_message(user)
                    
                    # Log user return
                    registration_service.log_user_activity(user, "user_returned", "Returning user")
                
                # Get user summary for display
                summary = user_service.get_user_summary(user.id)
                
                # Add financial summary to welcome message
                financial_summary = f"""

📊 *Ringkasan Keuangan Anda:*
💰 Total Saldo: {format_currency_idr(summary['total_balance'])}
🏦 Jumlah Kantong: {summary['wallet_count']}
📈 Pemasukan Bulan Ini: {format_currency_idr(summary['monthly_income'])}
📉 Pengeluaran Bulan Ini: {format_currency_idr(summary['monthly_expense'])}
💵 Net Bulan Ini: {format_currency_idr(summary['monthly_net'])}

Pilih menu di bawah untuk memulai:"""

                final_message = welcome_text + financial_summary
                markup = create_main_menu()
                
                # Send response
                bot.reply_to(message, final_message, reply_markup=markup, parse_mode='Markdown')
                
                # Log outgoing message
                message_logger.log_outgoing_message(
                    message.chat.id, 
                    final_message, 
                    message.from_user.id, 
                    "start_command_response"
                )
                
                # Log command execution
                message_logger.log_command_execution(message.from_user.id, "/start", True)
                
            finally:
                db.close()
                
        except Exception as e:
            logger.error(f"❌ Error in start command: {e}")
            
            # Log error
            message_logger.log_error_occurred(
                message.from_user.id,
                "start_command_error",
                str(e),
                "start_command execution"
            )
            
            error_message = "❌ Terjadi kesalahan saat memproses permintaan Anda. Tim teknis telah diberitahu. Silakan coba lagi dalam beberapa saat."
            bot.reply_to(message, error_message)
            
            message_logger.log_outgoing_message(
                message.chat.id,
                error_message,
                message.from_user.id,
                "error_response"
            )
    
    @bot.message_handler(commands=['help'])
    def help_command(message):
        """Handle /help command"""
        help_text = """🆘 *Bantuan Mon-Man Bot*

*🏦 Manajemen Kantong:*
• Tambah/edit/hapus kantong (Dompet, Bank, E-Wallet, dll.)
• Lihat saldo dan rincian kantong

*💸 Pencatatan Transaksi:*
• `/in [jumlah] [deskripsi] [dari kantong]` - Catat pemasukan
• `/out [jumlah] [deskripsi] [dari kantong]` - Catat pengeluaran  
• `/transfer [jumlah] [dari] [ke]` - Transfer antar kantong

*Contoh:*
• `/in 500000 gaji dari BCA`
• `/out 25000 makan siang dari Dompet`
• `/transfer 100000 BCA Dana`

*📊 Laporan:*
• Laporan harian, mingguan, bulanan
• Analisis perbandingan dan tren
• Breakdown pengeluaran per kategori

*⚙️ Pengaturan:*
• `/settings` - Pengaturan akun
• `/export` - Export data keuangan

Gunakan menu untuk navigasi yang mudah!"""

        try:
            bot.reply_to(message, help_text, parse_mode='Markdown')
            
            # Log outgoing message and command execution
            message_logger.log_outgoing_message(
                message.chat.id,
                help_text,
                message.from_user.id,
                "help_command_response"
            )
            message_logger.log_command_execution(message.from_user.id, "/help", True)
            
        except Exception as e:
            logger.error(f"❌ Error in help command: {e}")
            message_logger.log_error_occurred(
                message.from_user.id,
                "help_command_error", 
                str(e),
                "help_command execution"
            )
    
    @bot.message_handler(commands=['status', 'info'])
    def status_command(message):
        """Handle /status command to show user registration info"""
        # Log incoming message
        message_logger.log_incoming_message(message)
        
        try:
            db = SessionLocal()
            try:
                user_service = UserService(db)
                registration_service = UserRegistrationService(db)
                
                user = user_service.get_or_create_user(message.from_user)
                stats = registration_service.get_user_statistics(user)
                
                status_text = f"""📊 *Status Akun Anda*

👤 *Informasi Pengguna:*
• Nama: {stats['name'] or 'Tidak diatur'}
• Username: @{stats['username'] or 'Tidak diatur'}
• ID Telegram: `{stats['telegram_id']}`
• ID Internal: `{stats['user_id']}`

📅 *Informasi Akun:*
• Terdaftar sejak: {stats['days_registered']} hari yang lalu
• Aktivitas terakhir: {stats['last_activity']}

💰 *Ringkasan Keuangan:*
• Total Saldo: {format_currency_idr(stats['total_balance'])}
• Jumlah Kantong: {stats['wallet_count']}
• Pemasukan Bulan Ini: {format_currency_idr(stats['monthly_income'])}
• Pengeluaran Bulan Ini: {format_currency_idr(stats['monthly_expense'])}

🤖 *Status Bot:* Aktif dan Berfungsi Normal
📝 *Data Tersimpan:* Aman dan Terenkripsi"""

                bot.reply_to(message, status_text, parse_mode='Markdown')
                
                # Log activity and messages
                registration_service.log_user_activity(user, "status_checked", "User checked account status")
                message_logger.log_outgoing_message(
                    message.chat.id,
                    status_text,
                    message.from_user.id,
                    "status_command_response"
                )
                message_logger.log_command_execution(message.from_user.id, "/status", True)
                
            finally:
                db.close()
                
        except Exception as e:
            logger.error(f"❌ Error in status command: {e}")
            message_logger.log_error_occurred(
                message.from_user.id,
                "status_command_error",
                str(e),
                "status_command execution"
            )
            bot.reply_to(message, "❌ Terjadi kesalahan saat mengambil informasi status.")
    
    @bot.message_handler(commands=['menu'])
    def menu_command(message):
        """Handle /menu command"""
        try:
            db = SessionLocal()
            try:
                user_service = UserService(db)
                user = user_service.get_or_create_user(message.from_user)
                summary = user_service.get_user_summary(user.id)
                
                menu_text = f"""� *Menu Utama*

💰 Total Saldo: {format_currency_idr(summary['total_balance'])}
🏦 Kantong: {summary['wallet_count']}

Pilih opsi yang Anda inginkan:"""

                markup = create_main_menu()
                bot.reply_to(message, menu_text, reply_markup=markup, parse_mode='Markdown')
                
            finally:
                db.close()
                
        except Exception as e:
            logger.error(f"Error in menu command: {e}")
            bot.reply_to(message, "❌ Terjadi kesalahan. Silakan coba lagi.")
    
    @bot.callback_query_handler(func=lambda call: call.data == 'main_menu')
    def main_menu_callback(call):
        """Handle main menu callback"""
        try:
            db = SessionLocal()
            try:
                user_service = UserService(db)
                user = user_service.get_or_create_user(call.from_user)
                summary = user_service.get_user_summary(user.id)
                
                menu_text = f"""📱 *Menu Utama*

💰 Total Saldo: {format_currency_idr(summary['total_balance'])}
🏦 Kantong: {summary['wallet_count']}

Pilih opsi yang Anda inginkan:"""

                markup = create_main_menu()
                bot.edit_message_text(
                    menu_text,
                    call.message.chat.id,
                    call.message.message_id,
                    reply_markup=markup,
                    parse_mode='Markdown'
                )
                safe_answer_callback_query(bot, call.id)
                
            finally:
                db.close()
                
        except Exception as e:
            logger.error(f"Error in main menu callback: {e}")
            safe_answer_callback_query(bot, call.id, "❌ Terjadi kesalahan")
    
    @bot.callback_query_handler(func=lambda call: call.data == 'help')
    def help_callback(call):
        """Handle help callback"""
        try:
            help_text = """📖 *Panduan Penggunaan Mon-Man Bot*

🏦 *Manajemen Kantong:*
• Tambah kantong baru dengan saldo awal
• Edit nama dan saldo kantong
• Hapus kantong yang tidak digunakan

💸 *Pencatatan Transaksi:*
• `/in [jumlah] [deskripsi] [kantong]` - Catat pemasukan
• `/out [jumlah] [deskripsi] [kantong]` - Catat pengeluaran
• `/transfer [jumlah] [dari] [ke]` - Transfer antar kantong

*Contoh:*
• `/in 50000 gaji dari BCA`
• `/out 15000 makan siang dari Dompet`
• `/transfer 100000 BCA Dompet`

📊 *Laporan:*
• Laporan harian, mingguan, bulanan
• Perbandingan periode (WoW, MoM)
• Breakdown pengeluaran per kategori

⚙️ *Lainnya:*
• `/menu` - Tampilkan menu utama
• `/help` - Panduan ini

❓ *Butuh bantuan?* Gunakan tombol menu untuk navigasi yang mudah!"""
            
            markup = create_back_button('main_menu')
            bot.edit_message_text(
                help_text,
                call.message.chat.id,
                call.message.message_id,
                reply_markup=markup,
                parse_mode='Markdown'
            )
            safe_answer_callback_query(bot, call.id)
            
        except Exception as e:
            logger.error(f"Error in help callback: {e}")
            safe_answer_callback_query(bot, call.id, "❌ Terjadi kesalahan")
