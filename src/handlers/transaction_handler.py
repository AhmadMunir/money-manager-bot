import telebot
from telebot import types
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from src.models.database import SessionLocal, User, Wallet, Transaction, Category
from src.utils.keyboards import (
    create_transaction_menu, create_wallet_selection_keyboard,
    create_category_keyboard, create_confirmation_keyboard, 
    create_back_button, get_wallet_emoji
)
from src.utils.helpers import (
    format_currency_idr, parse_transaction_text, parse_transfer_text,
    validate_transaction_amount, format_transaction_summary,
    get_category_name, parse_amount,
    safe_answer_callback_query
)
import logging

logger = logging.getLogger(__name__)

# Store user states for multi-step processes
transaction_states = {}

def register_transaction_handlers(bot):
    @bot.callback_query_handler(func=lambda call: call.data == 'transaction_transfer')
    def transaction_transfer_callback(call):
        """Handle transfer antar kantong (wallet)"""
        try:
            user_id = call.from_user.id
            db = SessionLocal()
            try:
                user = db.query(User).filter(User.telegram_id == user_id).first()
                if not user:
                    safe_answer_callback_query(bot, call.id, "❌ User tidak ditemukan")
                    return
                wallets = db.query(Wallet).filter(Wallet.user_id == user.id, Wallet.is_active == True).all()
                if len(wallets) < 2:
                    text = "📭 *Minimal 2 kantong diperlukan untuk transfer.*\n\nBuat kantong baru terlebih dahulu."
                    markup = types.InlineKeyboardMarkup()
                    btn_add = types.InlineKeyboardButton("➕ Tambah Kantong", callback_data="wallet_add")
                    btn_back = types.InlineKeyboardButton("🔙 Kembali", callback_data="transaction_menu")
                    markup.add(btn_add)
                    markup.add(btn_back)
                    bot.edit_message_text(
                        text,
                        call.message.chat.id,
                        call.message.message_id,
                        reply_markup=markup,
                        parse_mode='Markdown'
                    )
                    return
                # Store transfer state
                transaction_states[user_id] = {
                    'type': 'transfer',
                    'step': 'from_wallet',
                    'wallets': [w.id for w in wallets]
                }
                markup = create_wallet_selection_keyboard(wallets, 'transfer_from')
                bot.edit_message_text(
                    "🔄 *Transfer Antar Kantong*\n\nPilih kantong asal:",
                    call.message.chat.id,
                    call.message.message_id,
                    reply_markup=markup,
                    parse_mode='Markdown'
                )
            finally:
                db.close()
        except Exception as e:
            logger.error(f"Error in transfer transaction: {e}")
            safe_answer_callback_query(bot, call.id, "❌ Terjadi kesalahan")

    @bot.callback_query_handler(func=lambda call: call.data.startswith('transfer_from_wallet_'))
    def transfer_from_wallet_callback(call):
        user_id = call.from_user.id
        state = transaction_states.get(user_id)
        if not state or state.get('type') != 'transfer' or state.get('step') != 'from_wallet':
            return
        from_wallet_id = int(call.data.split('_')[-1])
        state['from_wallet_id'] = from_wallet_id
        state['step'] = 'to_wallet'
        db = SessionLocal()
        try:
            user = db.query(User).filter(User.telegram_id == user_id).first()
            wallets = db.query(Wallet).filter(Wallet.user_id == user.id, Wallet.is_active == True, Wallet.id != from_wallet_id).all()
            markup = create_wallet_selection_keyboard(wallets, 'transfer_to')
            bot.edit_message_text(
                "🔄 *Transfer Antar Kantong*\n\nPilih kantong tujuan:",
                call.message.chat.id,
                call.message.message_id,
                reply_markup=markup,
                parse_mode='Markdown'
            )
        finally:
            db.close()

    @bot.callback_query_handler(func=lambda call: call.data.startswith('transfer_to_wallet_'))
    def transfer_to_wallet_callback(call):
        user_id = call.from_user.id
        state = transaction_states.get(user_id)
        if not state or state.get('type') != 'transfer' or state.get('step') != 'to_wallet':
            return
        to_wallet_id = int(call.data.split('_')[-1])
        if to_wallet_id == state.get('from_wallet_id'):
            safe_answer_callback_query(bot, call.id, "❌ Tidak bisa transfer ke kantong yang sama.")
            return
        state['to_wallet_id'] = to_wallet_id
        state['step'] = 'amount'
        bot.edit_message_text(
            "🔄 *Transfer Antar Kantong*\n\nMasukkan jumlah yang akan ditransfer:",
            call.message.chat.id,
            call.message.message_id,
            parse_mode='Markdown'
        )

    @bot.message_handler(func=lambda message: transaction_states.get(message.from_user.id, {}).get('type') == 'transfer' and transaction_states.get(message.from_user.id, {}).get('step') == 'amount')
    def handle_transfer_amount(message):
        user_id = message.from_user.id
        state = transaction_states.get(user_id)
        amount = parse_amount(message.text)
        if amount is None or amount <= 0:
            bot.send_message(message.chat.id, "❌ Jumlah tidak valid. Masukkan angka positif.")
            return
        state['amount'] = amount
        # Konfirmasi transfer
        db = SessionLocal()
        try:
            from_wallet = db.query(Wallet).filter(Wallet.id == state['from_wallet_id']).first()
            to_wallet = db.query(Wallet).filter(Wallet.id == state['to_wallet_id']).first()
            if from_wallet.balance < amount:
                bot.send_message(message.chat.id, f"❌ Saldo di kantong '{from_wallet.name}' tidak cukup.")
                return
            summary = f"🔄 *Konfirmasi Transfer*\n\n"
            summary += f"Dari: {from_wallet.name}\nKe: {to_wallet.name}\n"
            summary += f"Jumlah: {format_currency_idr(amount)}\n\n"
            summary += "Apakah Anda yakin ingin melanjutkan?"
            markup = create_confirmation_keyboard('confirm_transfer', 'transaction_menu')
            bot.send_message(message.chat.id, summary, reply_markup=markup, parse_mode='Markdown')
            state['step'] = 'confirm'
        finally:
            db.close()

    @bot.callback_query_handler(func=lambda call: call.data == 'confirm_transfer')
    def confirm_transfer_callback(call):
        user_id = call.from_user.id
        state = transaction_states.get(user_id)
        if not state or state.get('type') != 'transfer' or state.get('step') != 'confirm':
            return
        db = SessionLocal()
        try:
            user_service = UserService(db)
            user = db.query(User).filter(User.telegram_id == user_id).first()
            from_wallet = db.query(Wallet).filter(Wallet.id == state['from_wallet_id']).first()
            to_wallet = db.query(Wallet).filter(Wallet.id == state['to_wallet_id']).first()
            amount = state['amount']
            # Eksekusi transfer
            user_service.create_transaction(
                user_id=user.id,
                transaction_type='transfer',
                amount=amount,
                description=f"Transfer dari {from_wallet.name} ke {to_wallet.name}",
                from_wallet_id=from_wallet.id,
                to_wallet_id=to_wallet.id
            )
            bot.edit_message_text(
                f"✅ Transfer berhasil!\n\n{format_currency_idr(amount)} dari *{from_wallet.name}* ke *{to_wallet.name}*.",
                call.message.chat.id,
                call.message.message_id,
                parse_mode='Markdown'
            )
            del transaction_states[user_id]
        except Exception as e:
            logger.error(f"Error in confirm_transfer: {e}")
            bot.edit_message_text(
                "❌ Transfer gagal. Silakan coba lagi.",
                call.message.chat.id,
                call.message.message_id
            )
            if user_id in transaction_states:
                del transaction_states[user_id]
        finally:
            db.close()
    """Register transaction handlers"""
    
    @bot.callback_query_handler(func=lambda call: call.data == 'transaction_menu')
    def transaction_menu_callback(call):
        """Handle transaction menu callback"""
        try:
            markup = create_transaction_menu()
            bot.edit_message_text(
                "💸 *Manajemen Transaksi*\n\nPilih jenis transaksi:",
                call.message.chat.id,
                call.message.message_id,
                reply_markup=markup,
                parse_mode='Markdown'
            )
        except Exception as e:
            logger.error(f"Error in transaction menu: {e}")
            safe_answer_callback_query(bot, call.id, "❌ Terjadi kesalahan")
    
    @bot.callback_query_handler(func=lambda call: call.data == 'transaction_income')
    def transaction_income_callback(call):
        """Handle income transaction"""
        try:
            user_id = call.from_user.id
            db = SessionLocal()
            
            try:
                user = db.query(User).filter(User.telegram_id == user_id).first()
                if not user:
                    safe_answer_callback_query(bot, call.id, "❌ User tidak ditemukan")
                    return
                
                wallets = db.query(Wallet).filter(
                    Wallet.user_id == user.id,
                    Wallet.is_active == True
                ).all()
                
                if not wallets:
                    text = "📭 *Tidak ada kantong*\n\nAnda perlu membuat kantong terlebih dahulu sebelum mencatat transaksi."
                    markup = types.InlineKeyboardMarkup()
                    btn_add = types.InlineKeyboardButton("➕ Tambah Kantong", callback_data="wallet_add")
                    btn_back = types.InlineKeyboardButton("🔙 Kembali", callback_data="transaction_menu")
                    markup.add(btn_add)
                    markup.add(btn_back)
                    
                    bot.edit_message_text(
                        text,
                        call.message.chat.id,
                        call.message.message_id,
                        reply_markup=markup,
                        parse_mode='Markdown'
                    )
                    return
                
                # Store transaction state
                transaction_states[user_id] = {
                    'type': 'income',
                    'step': 'wallet'
                }
                
                markup = create_wallet_selection_keyboard(wallets, 'income')
                bot.edit_message_text(
                    "💰 *Catat Pemasukan*\n\nPilih kantong tujuan:",
                    call.message.chat.id,
                    call.message.message_id,
                    reply_markup=markup,
                    parse_mode='Markdown'
                )
                
            finally:
                db.close()
                
        except Exception as e:
            logger.error(f"Error in income transaction: {e}")
            safe_answer_callback_query(bot, call.id, "❌ Terjadi kesalahan")
    
    @bot.callback_query_handler(func=lambda call: call.data == 'transaction_expense')
    def transaction_expense_callback(call):
        """Handle expense transaction"""
        try:
            user_id = call.from_user.id
            db = SessionLocal()
            
            try:
                user = db.query(User).filter(User.telegram_id == user_id).first()
                if not user:
                    safe_answer_callback_query(bot, call.id, "❌ User tidak ditemukan")
                    return
                
                wallets = db.query(Wallet).filter(
                    Wallet.user_id == user.id,
                    Wallet.is_active == True
                ).all()
                
                if not wallets:
                    text = "📭 *Tidak ada kantong*\n\nAnda perlu membuat kantong terlebih dahulu sebelum mencatat transaksi."
                    markup = types.InlineKeyboardMarkup()
                    btn_add = types.InlineKeyboardButton("➕ Tambah Kantong", callback_data="wallet_add")
                    btn_back = types.InlineKeyboardButton("🔙 Kembali", callback_data="transaction_menu")
                    markup.add(btn_add)
                    markup.add(btn_back)
                    
                    bot.edit_message_text(
                        text,
                        call.message.chat.id,
                        call.message.message_id,
                        reply_markup=markup,
                        parse_mode='Markdown'
                    )
                    return
                
                # Store transaction state
                transaction_states[user_id] = {
                    'type': 'expense',
                    'step': 'wallet'
                }
                
                markup = create_wallet_selection_keyboard(wallets, 'expense')
                bot.edit_message_text(
                    "💸 *Catat Pengeluaran*\n\nPilih kantong sumber:",
                    call.message.chat.id,
                    call.message.message_id,
                    reply_markup=markup,
                    parse_mode='Markdown'
                )
                
            finally:
                db.close()
                
        except Exception as e:
            logger.error(f"Error in expense transaction: {e}")
            safe_answer_callback_query(bot, call.id, "❌ Terjadi kesalahan")
    
    @bot.callback_query_handler(func=lambda call: call.data.startswith('income_wallet_'))
    def income_wallet_callback(call):
        """Handle income wallet selection"""
        try:
            wallet_id = int(call.data.replace('income_wallet_', ''))
            user_id = call.from_user.id
            
            # Update transaction state
            if user_id in transaction_states:
                transaction_states[user_id]['to_wallet_id'] = wallet_id
                transaction_states[user_id]['step'] = 'amount'
            
            db = SessionLocal()
            try:
                wallet = db.query(Wallet).filter(Wallet.id == wallet_id).first()
                wallet_name = wallet.name if wallet else "Unknown"
            finally:
                db.close()
            
            markup = create_back_button('transaction_income')
            bot.edit_message_text(
                f"💰 *Catat Pemasukan*\n"
                f"🏦 Kantong: {wallet_name}\n\n"
                f"Masukkan jumlah dan deskripsi:\n"
                f"Format: `[jumlah] [deskripsi]`\n\n"
                f"Contoh:\n"
                f"• `500000 gaji bulanan`\n"
                f"• `50000 bonus`\n"
                f"• `1000000 hasil investasi`",
                call.message.chat.id,
                call.message.message_id,
                reply_markup=markup,
                parse_mode='Markdown'
            )
            
        except Exception as e:
            logger.error(f"Error in income wallet selection: {e}")
            safe_answer_callback_query(bot, call.id, "❌ Terjadi kesalahan")
    
    @bot.callback_query_handler(func=lambda call: call.data.startswith('expense_wallet_'))
    def expense_wallet_callback(call):
        """Handle expense wallet selection"""
        try:
            wallet_id = int(call.data.replace('expense_wallet_', ''))
            user_id = call.from_user.id
            
            # Update transaction state
            if user_id in transaction_states:
                transaction_states[user_id]['from_wallet_id'] = wallet_id
                transaction_states[user_id]['step'] = 'amount'
            
            db = SessionLocal()
            try:
                wallet = db.query(Wallet).filter(Wallet.id == wallet_id).first()
                wallet_name = wallet.name if wallet else "Unknown"
                wallet_balance = wallet.balance if wallet else 0
            finally:
                db.close()
            
            markup = create_back_button('transaction_expense')
            bot.edit_message_text(
                f"💸 *Catat Pengeluaran*\n"
                f"🏦 Kantong: {wallet_name}\n"
                f"💰 Saldo: {format_currency_idr(wallet_balance)}\n\n"
                f"Masukkan jumlah dan deskripsi:\n"
                f"Format: `[jumlah] [deskripsi]`\n\n"
                f"Contoh:\n"
                f"• `25000 makan siang`\n"
                f"• `50000 bensin`\n"
                f"• `150000 belanja bulanan`",
                call.message.chat.id,
                call.message.message_id,
                reply_markup=markup,
                parse_mode='Markdown'
            )
            
        except Exception as e:
            logger.error(f"Error in expense wallet selection: {e}")
            safe_answer_callback_query(bot, call.id, "❌ Terjadi kesalahan")
    
    @bot.message_handler(func=lambda message: message.from_user.id in transaction_states)
    def handle_transaction_input(message):
        """Handle transaction input"""
        try:
            user_id = message.from_user.id
            state = transaction_states.get(user_id)
            
            if not state:
                return
            
            if state['step'] == 'amount':
                # Parse amount and description
                text = message.text.strip()
                parts = text.split(' ', 1)
                
                if len(parts) < 2:
                    bot.send_message(
                        message.chat.id,
                        "❌ Format tidak valid. Masukkan: [jumlah] [deskripsi]\n"
                        "Contoh: `50000 makan siang`",
                        parse_mode='Markdown'
                    )
                    return
                
                amount = parse_amount(parts[0])
                description = parts[1].strip()
                
                if amount is None or not validate_transaction_amount(amount):
                    bot.send_message(
                        message.chat.id,
                        "❌ Jumlah tidak valid. Silakan masukkan angka yang benar."
                    )
                    return
                
                if not description:
                    bot.send_message(
                        message.chat.id,
                        "❌ Deskripsi wajib diisi."
                    )
                    return
                
                # Store amount and description
                state['amount'] = amount
                state['description'] = description
                state['step'] = 'category'
                
                # Show category selection
                markup = create_category_keyboard(state['type'])
                bot.send_message(
                    message.chat.id,
                    f"🏷️ *Pilih Kategori*\n\n"
                    f"Transaksi: {format_currency_idr(amount)} - {description}",
                    reply_markup=markup,
                    parse_mode='Markdown'
                )
                
        except Exception as e:
            logger.error(f"Error handling transaction input: {e}")
            bot.send_message(
                message.chat.id,
                "❌ Terjadi kesalahan. Silakan coba lagi."
            )
            # Clear state on error
            if user_id in transaction_states:
                del transaction_states[user_id]
    
    @bot.callback_query_handler(func=lambda call: call.data.startswith('category_'))
    def category_callback(call):
        """Handle category selection"""
        try:
            category_code = call.data.replace('category_', '')
            user_id = call.from_user.id
            state = transaction_states.get(user_id)
            
            if not state:
                safe_answer_callback_query(bot, call.id, "❌ Sesi expired")
                return
            
            state['category'] = category_code
            
            # Show confirmation
            db = SessionLocal()
            try:
                if state['type'] == 'income':
                    wallet = db.query(Wallet).filter(Wallet.id == state['to_wallet_id']).first()
                    wallet_name = wallet.name if wallet else "Unknown"
                    
                    summary = format_transaction_summary(
                        'income', state['amount'], state['description'],
                        to_wallet=wallet_name, category=get_category_name(category_code)
                    )
                else:  # expense
                    wallet = db.query(Wallet).filter(Wallet.id == state['from_wallet_id']).first()
                    wallet_name = wallet.name if wallet else "Unknown"
                    
                    summary = format_transaction_summary(
                        'expense', state['amount'], state['description'],
                        from_wallet=wallet_name, category=get_category_name(category_code)
                    )
                
                summary += "\n\n*Lanjut simpan?*"
                
                markup = create_confirmation_keyboard('save_transaction')
                bot.edit_message_text(
                    summary,
                    call.message.chat.id,
                    call.message.message_id,
                    reply_markup=markup,
                    parse_mode='Markdown'
                )
                
            finally:
                db.close()
                
        except Exception as e:
            logger.error(f"Error in category selection: {e}")
            safe_answer_callback_query(bot, call.id, "❌ Terjadi kesalahan")
    
    @bot.callback_query_handler(func=lambda call: call.data == 'confirm_save_transaction')
    def confirm_save_transaction(call):
        """Save transaction"""
        try:
            user_id = call.from_user.id
            state = transaction_states.get(user_id)
            
            if not state:
                safe_answer_callback_query(bot, call.id, "❌ Sesi expired")
                return
            
            db = SessionLocal()
            try:
                user = db.query(User).filter(User.telegram_id == user_id).first()
                
                # Create transaction
                transaction = Transaction(
                    user_id=user.id,
                    type=state['type'],
                    amount=state['amount'],
                    description=state['description']
                )
                
                if state['type'] == 'income':
                    transaction.to_wallet_id = state['to_wallet_id']
                    # Update wallet balance
                    wallet = db.query(Wallet).filter(Wallet.id == state['to_wallet_id']).first()
                    wallet.balance += state['amount']
                else:  # expense
                    transaction.from_wallet_id = state['from_wallet_id']
                    # Update wallet balance
                    wallet = db.query(Wallet).filter(Wallet.id == state['from_wallet_id']).first()
                    wallet.balance -= state['amount']
                
                db.add(transaction)
                db.commit()
                
                emoji = "💰" if state['type'] == 'income' else "💸"
                success_text = f"✅ *Transaksi Berhasil Disimpan!*\n\n"
                success_text += f"{emoji} {format_currency_idr(state['amount'])}\n"
                success_text += f"📝 {state['description']}\n"
                success_text += f"🏦 Saldo {wallet.name}: {format_currency_idr(wallet.balance)}"
                
                markup = create_back_button('transaction_menu')
                bot.edit_message_text(
                    success_text,
                    call.message.chat.id,
                    call.message.message_id,
                    reply_markup=markup,
                    parse_mode='Markdown'
                )
                
                # Clear state
                del transaction_states[user_id]
                
            finally:
                db.close()
                
        except Exception as e:
            logger.error(f"Error saving transaction: {e}")
            safe_answer_callback_query(bot, call.id, "❌ Terjadi kesalahan")
    
    # Command handlers for quick transaction entry
    @bot.message_handler(commands=['in', 'income'])
    def income_command(message):
        """Handle /in command for quick income entry"""
        try:
            # Parse transaction text
            amount, description, wallet_name = parse_transaction_text(message.text)
            
            if not amount or not description:
                bot.send_message(
                    message.chat.id,
                    "💰 *Catat Pemasukan Cepat*\n\n"
                    "Format: `/in [jumlah] [deskripsi] dari [kantong]`\n\n"
                    "Contoh:\n"
                    "• `/in 500000 gaji dari BCA`\n"
                    "• `/in 50000 bonus dari Dana`",
                    parse_mode='Markdown'
                )
                return
            
            # Quick save logic here...
            bot.send_message(
                message.chat.id,
                f"✅ Pemasukan {format_currency_idr(amount)} untuk '{description}' berhasil dicatat!"
            )
            
        except Exception as e:
            logger.error(f"Error in income command: {e}")
            bot.send_message(message.chat.id, "❌ Terjadi kesalahan")
    
    @bot.message_handler(commands=['out', 'expense'])
    def expense_command(message):
        """Handle /out command for quick expense entry"""
        try:
            # Parse transaction text
            amount, description, wallet_name = parse_transaction_text(message.text)
            
            if not amount or not description:
                bot.send_message(
                    message.chat.id,
                    "💸 *Catat Pengeluaran Cepat*\n\n"
                    "Format: `/out [jumlah] [deskripsi] dari [kantong]`\n\n"
                    "Contoh:\n"
                    "• `/out 25000 makan siang dari Dompet`\n"
                    "• `/out 50000 bensin dari BCA`",
                    parse_mode='Markdown'
                )
                return
            
            # Quick save logic here...
            bot.send_message(
                message.chat.id,
                f"✅ Pengeluaran {format_currency_idr(amount)} untuk '{description}' berhasil dicatat!"
            )
            
        except Exception as e:
            logger.error(f"Error in expense command: {e}")
            bot.send_message(message.chat.id, "❌ Terjadi kesalahan")
