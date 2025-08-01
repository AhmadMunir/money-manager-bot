import telebot
from telebot import types
from sqlalchemy.orm import sessionmaker
from src.models.database import SessionLocal, User, Wallet
from src.services.user_service import UserService
from src.utils.keyboards import (
    create_wallet_menu, create_wallet_types_keyboard, 
    create_wallet_list_keyboard, create_wallet_detail_keyboard,
    create_confirmation_keyboard, create_back_button, get_wallet_emoji
)
from src.utils.helpers import (
    format_currency_idr, validate_wallet_name, validate_transaction_amount,
    get_wallet_type_name, parse_amount, safe_answer_callback_query
)
import logging

logger = logging.getLogger(__name__)

# Store user states for multi-step processes
user_states = {}

def register_wallet_handlers(bot):
    """Register wallet management handlers"""
    
    @bot.callback_query_handler(func=lambda call: call.data == 'wallet_menu')
    def wallet_menu_callback(call):
        """Handle wallet menu callback"""
        try:
            markup = create_wallet_menu()
            bot.edit_message_text(
                "🏦 *Manajemen Kantong*\n\nKelola kantong/aset Anda:",
                call.message.chat.id,
                call.message.message_id,
                reply_markup=markup,
                parse_mode='Markdown'
            )
            safe_answer_callback_query(bot, call.id)
        except Exception as e:
            logger.error(f"Error in wallet menu: {e}")
            safe_answer_callback_query(bot, call.id, "❌ Terjadi kesalahan")
    
    @bot.callback_query_handler(func=lambda call: call.data == 'wallet_list')
    def wallet_list_callback(call):
        """Show wallet list"""
        try:
            db = SessionLocal()
            
            try:
                user_service = UserService(db)
                user = user_service.get_or_create_user(call.from_user)
                
                wallets = user_service.get_user_wallets(user.id, active_only=True)
                
                if not wallets:
                    text = "📭 *Tidak ada kantong*\n\nAnda belum memiliki kantong. Silakan tambah kantong pertama Anda!"
                    markup = types.InlineKeyboardMarkup()
                    btn_add = types.InlineKeyboardButton("➕ Tambah Kantong", callback_data="wallet_add")
                    btn_back = types.InlineKeyboardButton("🔙 Kembali", callback_data="wallet_menu")
                    markup.add(btn_add)
                    markup.add(btn_back)
                else:
                    text = "🏦 *Daftar Kantong Anda*\n\n"
                    total_balance = user.get_total_balance()
                    
                    for wallet in wallets:
                        emoji = get_wallet_emoji(wallet.type)
                        text += f"{emoji} *{wallet.name}*\n"
                        text += f"   💰 {format_currency_idr(wallet.balance)}\n"
                        text += f"   📝 {get_wallet_type_name(wallet.type)}\n\n"
                    
                    text += f"💯 *Total Saldo:* {format_currency_idr(total_balance)}"
                    markup = create_wallet_list_keyboard(wallets)
                
                bot.edit_message_text(
                    text,
                    call.message.chat.id,
                    call.message.message_id,
                    reply_markup=markup,
                    parse_mode='Markdown'
                )
                safe_answer_callback_query(bot, call.id)
                
            finally:
                db.close()
                
        except Exception as e:
            logger.error(f"Error in wallet list: {e}")
            safe_answer_callback_query(bot, call.id, "❌ Terjadi kesalahan")
    
    @bot.callback_query_handler(func=lambda call: call.data == 'wallet_add')
    def wallet_add_callback(call):
        """Start add wallet process"""
        try:
            markup = create_wallet_types_keyboard()
            bot.edit_message_text(
                "➕ *Tambah Kantong Baru*\n\nPilih jenis kantong:",
                call.message.chat.id,
                call.message.message_id,
                reply_markup=markup,
                parse_mode='Markdown'
            )
            safe_answer_callback_query(bot, call.id)
        except Exception as e:
            logger.error(f"Error in wallet add: {e}")
            safe_answer_callback_query(bot, call.id, "❌ Terjadi kesalahan")
    
    @bot.callback_query_handler(func=lambda call: call.data.startswith('wallet_type_'))
    def wallet_type_callback(call):
        """Handle wallet type selection"""
        try:
            wallet_type = call.data.replace('wallet_type_', '')
            user_id = call.from_user.id
            
            # Store user state
            user_states[user_id] = {
                'action': 'add_wallet',
                'type': wallet_type,
                'step': 'name'
            }
            
            type_name = get_wallet_type_name(wallet_type)
            emoji = get_wallet_emoji(wallet_type)
            
            markup = create_back_button('wallet_add')
            bot.edit_message_text(
                f"{emoji} *Tambah Kantong {type_name}*\n\n"
                f"Masukkan nama kantong:\n"
                f"(contoh: BCA, Dana, Dompet, dll)",
                call.message.chat.id,
                call.message.message_id,
                reply_markup=markup,
                parse_mode='Markdown'
            )
            
        except Exception as e:
            logger.error(f"Error in wallet type selection: {e}")
            safe_answer_callback_query(bot, call.id, "❌ Terjadi kesalahan")
    
    @bot.callback_query_handler(func=lambda call: call.data.startswith('wallet_detail_'))
    def wallet_detail_callback(call):
        """Show wallet detail"""
        try:
            wallet_id = int(call.data.replace('wallet_detail_', ''))
            db = SessionLocal()
            
            try:
                wallet = db.query(Wallet).filter(Wallet.id == wallet_id).first()
                if not wallet:
                    safe_answer_callback_query(bot, call.id, "❌ Kantong tidak ditemukan")
                    return
                
                emoji = get_wallet_emoji(wallet.type)
                type_name = get_wallet_type_name(wallet.type)
                
                text = f"{emoji} *{wallet.name}*\n\n"
                text += f"💰 *Saldo Saat Ini:* {format_currency_idr(wallet.balance)}\n"
                text += f"💵 *Saldo Awal:* {format_currency_idr(wallet.initial_balance)}\n"
                text += f"📝 *Jenis:* {type_name}\n"
                if wallet.description:
                    text += f"📄 *Deskripsi:* {wallet.description}\n"
                text += f"📅 *Dibuat:* {wallet.created_at.strftime('%d/%m/%Y')}\n"
                
                markup = create_wallet_detail_keyboard(wallet_id)
                bot.edit_message_text(
                    text,
                    call.message.chat.id,
                    call.message.message_id,
                    reply_markup=markup,
                    parse_mode='Markdown'
                )
                
            finally:
                db.close()
                
        except Exception as e:
            logger.error(f"Error in wallet detail: {e}")
            safe_answer_callback_query(bot, call.id, "❌ Terjadi kesalahan")
    
    @bot.callback_query_handler(func=lambda call: call.data.startswith('wallet_delete_'))
    def wallet_delete_callback(call):
        """Confirm wallet deletion"""
        try:
            wallet_id = int(call.data.replace('wallet_delete_', ''))
            db = SessionLocal()
            
            try:
                wallet = db.query(Wallet).filter(Wallet.id == wallet_id).first()
                if not wallet:
                    safe_answer_callback_query(bot, call.id, "❌ Kantong tidak ditemukan")
                    return
                
                text = f"🗑️ *Hapus Kantong*\n\n"
                text += f"Apakah Anda yakin ingin menghapus kantong:\n"
                text += f"*{wallet.name}* ({format_currency_idr(wallet.balance)})\n\n"
                text += f"⚠️ *Peringatan:* Semua transaksi terkait akan ikut terhapus!"
                
                markup = create_confirmation_keyboard('delete_wallet', wallet_id)
                bot.edit_message_text(
                    text,
                    call.message.chat.id,
                    call.message.message_id,
                    reply_markup=markup,
                    parse_mode='Markdown'
                )
                
            finally:
                db.close()
                
        except Exception as e:
            logger.error(f"Error in wallet delete: {e}")
            safe_answer_callback_query(bot, call.id, "❌ Terjadi kesalahan")
    
    @bot.callback_query_handler(func=lambda call: call.data.startswith('confirm_delete_wallet_'))
    def confirm_delete_wallet_callback(call):
        """Confirm and delete wallet"""
        try:
            wallet_id = int(call.data.replace('confirm_delete_wallet_', ''))
            db = SessionLocal()
            
            try:
                wallet = db.query(Wallet).filter(Wallet.id == wallet_id).first()
                if not wallet:
                    safe_answer_callback_query(bot, call.id, "❌ Kantong tidak ditemukan")
                    return
                
                wallet_name = wallet.name
                wallet.is_active = False  # Soft delete
                db.commit()
                
                safe_answer_callback_query(bot, call.id, f"✅ Kantong {wallet_name} berhasil dihapus")
                
                # Return to wallet list
                wallet_list_callback(call)
                
            finally:
                db.close()
                
        except Exception as e:
            logger.error(f"Error confirming wallet deletion: {e}")
            safe_answer_callback_query(bot, call.id, "❌ Terjadi kesalahan")
    
    @bot.message_handler(func=lambda message: message.from_user.id in user_states)
    def handle_wallet_input(message):
        """Handle wallet creation input"""
        try:
            user_id = message.from_user.id
            state = user_states.get(user_id)
            
            if not state or state['action'] != 'add_wallet':
                return
            
            if state['step'] == 'name':
                # Validate wallet name
                wallet_name = message.text.strip()
                if not validate_wallet_name(wallet_name):
                    bot.send_message(
                        message.chat.id,
                        "❌ Nama kantong tidak valid. Silakan masukkan nama yang valid (1-50 karakter):"
                    )
                    return
                
                # Check if wallet name already exists
                db = SessionLocal()
                try:
                    user_obj = db.query(User).filter(User.telegram_id == user_id).first()
                    existing_wallet = db.query(Wallet).filter(
                        Wallet.user_id == user_obj.id,
                        Wallet.name.ilike(wallet_name),
                        Wallet.is_active == True
                    ).first()
                    
                    if existing_wallet:
                        bot.send_message(
                            message.chat.id,
                            f"❌ Kantong dengan nama '{wallet_name}' sudah ada. Silakan gunakan nama lain:"
                        )
                        return
                    
                finally:
                    db.close()
                
                # Store name and ask for initial balance
                user_states[user_id]['name'] = wallet_name
                user_states[user_id]['step'] = 'balance'
                
                emoji = get_wallet_emoji(state['type'])
                bot.send_message(
                    message.chat.id,
                    f"{emoji} *Kantong: {wallet_name}*\n\n"
                    f"Masukkan saldo awal:\n"
                    f"(contoh: 100000 atau 0 jika kosong)",
                    parse_mode='Markdown'
                )
                
            elif state['step'] == 'balance':
                # Parse and validate balance
                balance = parse_amount(message.text)
                if balance is None:
                    bot.send_message(
                        message.chat.id,
                        "❌ Jumlah tidak valid. Silakan masukkan angka yang benar:"
                    )
                    return
                
                if balance < 0:
                    bot.send_message(
                        message.chat.id,
                        "❌ Saldo tidak boleh negatif. Silakan masukkan angka positif:"
                    )
                    return
                
                # Create wallet
                db = SessionLocal()
                try:
                    user_obj = db.query(User).filter(User.telegram_id == user_id).first()
                    
                    new_wallet = Wallet(
                        user_id=user_obj.id,
                        name=state['name'],
                        type=state['type'],
                        balance=balance,
                        initial_balance=balance
                    )
                    
                    db.add(new_wallet)
                    db.commit()
                    
                    emoji = get_wallet_emoji(state['type'])
                    type_name = get_wallet_type_name(state['type'])
                    
                    success_text = f"✅ *Kantong Berhasil Dibuat!*\n\n"
                    success_text += f"{emoji} *{state['name']}*\n"
                    success_text += f"📝 Jenis: {type_name}\n"
                    success_text += f"💰 Saldo Awal: {format_currency_idr(balance)}"
                    
                    markup = create_back_button('wallet_list')
                    bot.send_message(
                        message.chat.id,
                        success_text,
                        reply_markup=markup,
                        parse_mode='Markdown'
                    )
                    
                    # Clear user state
                    del user_states[user_id]
                    
                finally:
                    db.close()
                    
        except Exception as e:
            logger.error(f"Error handling wallet input: {e}")
            bot.send_message(
                message.chat.id,
                "❌ Terjadi kesalahan. Silakan coba lagi."
            )
            # Clear user state on error
            if user_id in user_states:
                del user_states[user_id]
    
    @bot.message_handler(commands=['wallet'])
    def wallet_command(message):
        """Handle /wallet command"""
        try:
            markup = create_wallet_menu()
            bot.send_message(
                message.chat.id,
                "🏦 *Manajemen Kantong*\n\nKelola kantong/aset Anda:",
                reply_markup=markup,
                parse_mode='Markdown'
            )
        except Exception as e:
            logger.error(f"Error in wallet command: {e}")
            bot.send_message(
                message.chat.id,
                "❌ Terjadi kesalahan. Silakan coba lagi."
            )
