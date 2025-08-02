import telebot
from telebot import types
from sqlalchemy.orm import sessionmaker
from src.models.database import SessionLocal, User, Wallet, Asset
from src.services.asset_service import AssetService
from src.utils.keyboards import create_wallet_selection_keyboard
from src.utils.helpers import format_currency_idr
import logging

logger = logging.getLogger(__name__)

asset_states = {}

def register_asset_handlers(bot):
    @bot.message_handler(commands=['aset', 'asset'])
    def asset_command(message):
        user_id = message.from_user.id
        db = SessionLocal()
        try:
            user = db.query(User).filter(User.telegram_id == user_id).first()
            if not user:
                bot.send_message(message.chat.id, "❌ User tidak ditemukan.")
                return
            service = AssetService(db)
            assets = service.get_user_assets(user.id)
            if not assets:
                bot.send_message(message.chat.id, "📭 Anda belum punya aset. Gunakan /tambahaset untuk menambah aset.")
                return
            text = "💼 *Daftar Aset Anda:*\n\n"
            markup = types.InlineKeyboardMarkup()
            for asset in assets:
                ret = asset.return_value or 0.0
                ret_pct = asset.return_percent or 0.0
                text += f"{asset.name} ({asset.symbol.upper()}) - {asset.quantity} @ {format_currency_idr(asset.buy_price)}\n"
                text += f"Harga terakhir: {format_currency_idr(asset.last_price) if asset.last_price else '-'}\n"
                text += f"Return: {format_currency_idr(ret)} ({ret_pct:.2f}%)\n"
                row = [
                    types.InlineKeyboardButton(f"🔄 Sinkron", callback_data=f"sync_asset_{asset.id}"),
                    types.InlineKeyboardButton(f"✏️ Edit", callback_data=f"edit_asset_{asset.id}"),
                    types.InlineKeyboardButton(f"🗑️ Hapus", callback_data=f"delete_asset_{asset.id}")
                ]
                markup.row(*row)
                text += "\n"
            bot.send_message(message.chat.id, text, reply_markup=markup, parse_mode='Markdown')
        finally:
            db.close()
    @bot.callback_query_handler(func=lambda call: call.data.startswith('delete_asset_'))
    def delete_asset_callback(call):
        user_id = call.from_user.id
        asset_id = int(call.data.split('_')[-1])
        
        # Hapus tombol untuk mencegah double click
        try:
            bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
        except:
            pass
            
        # Show loading message
        bot.answer_callback_query(call.id, "🗑️ Sedang menghapus...", show_alert=False)
        
        db = SessionLocal()
        try:
            # Cari user terlebih dahulu
            user = db.query(User).filter(User.telegram_id == user_id).first()
            if not user:
                bot.answer_callback_query(call.id, "❌ User tidak ditemukan.")
                return
                
            service = AssetService(db)
            ok = service.delete_asset(asset_id, user.id)  # Gunakan user.id bukan user_id
            if ok:
                bot.answer_callback_query(call.id, "✅ Aset berhasil dihapus!", show_alert=True)
                # Refresh list
                asset_command(call.message)
            else:
                bot.answer_callback_query(call.id, "❌ Gagal hapus aset.", show_alert=True)
                # Restore buttons jika gagal
                asset_command(call.message)
        finally:
            db.close()

    @bot.callback_query_handler(func=lambda call: call.data.startswith('edit_asset_'))
    def edit_asset_callback(call):
        user_id = call.from_user.id
        asset_id = int(call.data.split('_')[-1])
        db = SessionLocal()
        try:
            # Cari user terlebih dahulu
            user = db.query(User).filter(User.telegram_id == user_id).first()
            if not user:
                bot.answer_callback_query(call.id, "❌ User tidak ditemukan.", show_alert=True)
                return
                
            asset = db.query(Asset).filter(Asset.id == asset_id, Asset.user_id == user.id, Asset.is_active == True).first()
            if not asset:
                bot.answer_callback_query(call.id, "❌ Aset tidak ditemukan.", show_alert=True)
                return
            asset_states[user_id] = {
                'edit_id': asset_id,
                'step': 'edit_field',
                'edit_asset': asset
            }
            markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
            markup.add('name', 'symbol', 'quantity', 'buy_price', 'type')
            bot.send_message(call.message.chat.id, "Edit field apa? (name, symbol, quantity, buy_price, type)", reply_markup=markup)
        finally:
            db.close()

    @bot.message_handler(func=lambda m: asset_states.get(m.from_user.id, {}).get('step') == 'edit_field')
    def edit_asset_field_input(message):
        user_id = message.from_user.id
        field = message.text.strip().lower()
        if field not in ['name', 'symbol', 'quantity', 'buy_price', 'type']:
            bot.send_message(message.chat.id, "Field hanya: name, symbol, quantity, buy_price, type")
            return
        asset_states[user_id]['edit_field'] = field
        asset_states[user_id]['step'] = 'edit_value'
        bot.send_message(message.chat.id, f"Masukkan nilai baru untuk {field}:")

    @bot.message_handler(func=lambda m: asset_states.get(m.from_user.id, {}).get('step') == 'edit_value')
    def edit_asset_value_input(message):
        user_id = message.from_user.id
        field = asset_states[user_id]['edit_field']
        value = message.text.strip()
        asset_id = asset_states[user_id]['edit_id']
        db = SessionLocal()
        try:
            service = AssetService(db)
            kwargs = {}
            if field == 'name':
                kwargs['name'] = value.strip()
            elif field == 'symbol':
                kwargs['symbol'] = value.strip().lower()
            elif field == 'type':
                tipe = value.strip().lower()
                if tipe not in ['saham', 'kripto']:
                    bot.send_message(message.chat.id, "Tipe aset hanya 'saham' atau 'kripto'.")
                    return
                kwargs['asset_type'] = tipe
            elif field == 'quantity':
                try:
                    qty = float(value)
                    if qty <= 0:
                        raise ValueError
                    kwargs['quantity'] = qty
                except Exception:
                    bot.send_message(message.chat.id, "Jumlah tidak valid.")
                    return
            elif field == 'buy_price':
                try:
                    price = float(value)
                    if price <= 0:
                        raise ValueError
                    kwargs['buy_price'] = price
                except Exception:
                    bot.send_message(message.chat.id, "Harga tidak valid.")
                    return
            updated = service.update_asset(asset_id, user_id, **kwargs)
            if updated:
                bot.send_message(message.chat.id, f"✅ Aset berhasil diupdate!")
            else:
                bot.send_message(message.chat.id, f"❌ Gagal update aset.")
            del asset_states[user_id]
            # Refresh list
            asset_command(message)
        finally:
            db.close()

    @bot.message_handler(commands=['tambahaset'])
    def add_asset_command(message):
        user_id = message.from_user.id
        db = SessionLocal()
        try:
            user = db.query(User).filter(User.telegram_id == user_id).first()
            wallets = db.query(Wallet).filter(Wallet.user_id == user.id, Wallet.is_active == True).all()
            if not wallets:
                bot.send_message(message.chat.id, "❌ Anda harus punya minimal 1 kantong untuk menyimpan aset.")
                return
            asset_states[user_id] = {'step': 'name'}
            bot.send_message(message.chat.id, "🆕 Masukkan nama aset (misal: BBCA, BTC):")
        finally:
            db.close()

    @bot.message_handler(func=lambda m: asset_states.get(m.from_user.id, {}).get('step') == 'name')
    def asset_input_name(message):
        user_id = message.from_user.id
        asset_states[user_id]['name'] = message.text.strip().upper()
        asset_states[user_id]['step'] = 'type'
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        markup.add('saham', 'kripto')
        bot.send_message(message.chat.id, "Pilih tipe aset:", reply_markup=markup)

    @bot.message_handler(func=lambda m: asset_states.get(m.from_user.id, {}).get('step') == 'type')
    def asset_input_type(message):
        user_id = message.from_user.id
        tipe = message.text.strip().lower()
        if tipe not in ['saham', 'kripto']:
            bot.send_message(message.chat.id, "Tipe aset hanya 'saham' atau 'kripto'.")
            return
        asset_states[user_id]['type'] = tipe
        asset_states[user_id]['step'] = 'symbol'
        bot.send_message(message.chat.id, "Masukkan kode/simbol aset (misal: BBCA, btc):")

    @bot.message_handler(func=lambda m: asset_states.get(m.from_user.id, {}).get('step') == 'symbol')
    def asset_input_symbol(message):
        user_id = message.from_user.id
        asset_states[user_id]['symbol'] = message.text.strip().lower()
        asset_states[user_id]['step'] = 'quantity'
        bot.send_message(message.chat.id, "Masukkan jumlah (lot untuk saham, unit untuk kripto):")

    @bot.message_handler(func=lambda m: asset_states.get(m.from_user.id, {}).get('step') == 'quantity')
    def asset_input_quantity(message):
        user_id = message.from_user.id
        
        # Pastikan user state masih valid
        if user_id not in asset_states:
            bot.send_message(message.chat.id, "Sesi telah expired. Silakan mulai lagi dengan /tambahaset")
            return
            
        try:
            # Support koma sebagai separator desimal
            qty_text = message.text.strip().replace(',', '.')
            qty = float(qty_text)
            
            if qty <= 0:
                raise ValueError("Jumlah harus positif")
                
            asset_states[user_id]['quantity'] = qty
            asset_states[user_id]['step'] = 'buy_price'
            bot.send_message(message.chat.id, "Masukkan harga beli per unit (IDR):\nContoh: 8571 atau 8571.50")
            
        except ValueError as e:
            # Jangan hapus state saat error
            bot.send_message(message.chat.id, f"❌ Jumlah tidak valid: {str(e)}\n\nMasukkan jumlah (lot untuk saham, unit untuk kripto):\nContoh: 100 atau 0.001")
        except Exception as e:
            logger.error(f"Error in asset_input_quantity: {e}")
            bot.send_message(message.chat.id, "❌ Terjadi kesalahan. Silakan coba lagi.")

    @bot.message_handler(func=lambda m: asset_states.get(m.from_user.id, {}).get('step') == 'buy_price')
    def asset_input_buy_price(message):
        user_id = message.from_user.id
        
        # Pastikan user state masih valid
        if user_id not in asset_states:
            bot.send_message(message.chat.id, "Sesi telah expired. Silakan mulai lagi dengan /tambahaset")
            return
            
        try:
            # Support koma sebagai separator desimal (8.571,50 atau 8571,50)
            price_text = message.text.strip().replace(',', '.')
            price = float(price_text)
            
            if price <= 0:
                raise ValueError("Harga harus positif")
                
            asset_states[user_id]['buy_price'] = price
            asset_states[user_id]['step'] = 'wallet'
            
            # Ambil daftar wallet user
            db = SessionLocal()
            try:
                user = db.query(User).filter(User.telegram_id == user_id).first()
                if not user:
                    bot.send_message(message.chat.id, "❌ User tidak ditemukan. Silakan mulai ulang dengan /start")
                    asset_states.pop(user_id, None)
                    return
                    
                wallets = db.query(Wallet).filter(Wallet.user_id == user.id, Wallet.is_active == True).all()
                if not wallets:
                    bot.send_message(message.chat.id, "❌ Anda belum punya kantong/wallet. Silakan buat dulu di menu Kantong.")
                    asset_states.pop(user_id, None)
                    return
                    
                markup = create_wallet_selection_keyboard(wallets, 'asset')
                bot.send_message(message.chat.id, "Pilih kantong untuk menyimpan aset:", reply_markup=markup)
                
            finally:
                db.close()
                
        except ValueError as e:
            # Jangan hapus state saat error, biarkan user coba lagi
            bot.send_message(message.chat.id, f"❌ Harga beli tidak valid: {str(e)}\n\nMasukkan harga beli per unit (IDR):\nContoh: 8571 atau 8571.50")
        except Exception as e:
            logger.error(f"Error in asset_input_buy_price: {e}")
            bot.send_message(message.chat.id, "❌ Terjadi kesalahan. Silakan coba lagi atau mulai ulang dengan /tambahaset")

    @bot.callback_query_handler(func=lambda call: call.data.startswith('asset_wallet_'))
    def asset_select_wallet(call):
        """Handler untuk memilih wallet saat menambah aset"""
        user_id = call.from_user.id
        if user_id not in asset_states or asset_states[user_id].get('step') != 'wallet':
            bot.answer_callback_query(call.id, "Sesi expired. Mulai lagi.", show_alert=True)
            return
        
        wallet_id = int(call.data.split('_')[-1])
        asset_states[user_id]['wallet_id'] = wallet_id
        asset_states[user_id]['step'] = 'confirm'
        
        # Tampilkan ringkasan dengan validasi data
        data = asset_states[user_id]
        
        # Validasi field yang diperlukan
        required_fields = ['type', 'symbol', 'quantity', 'buy_price']
        for field in required_fields:
            if field not in data:
                bot.answer_callback_query(call.id, f"Data {field} tidak lengkap. Mulai ulang.", show_alert=True)
                asset_states.pop(user_id, None)
                return
        
        # Gunakan nama dari data atau fallback ke symbol jika tidak ada
        asset_name = data.get('name', data.get('symbol', 'Unknown'))
        
        text = f"""*Konfirmasi Data Aset:*

Tipe: {data['type'].capitalize()}
Symbol: {data['symbol']}  
Nama: {asset_name}
Jumlah: {data['quantity']}
Harga Beli: {format_currency_idr(data['buy_price'])}
Wallet ID: {wallet_id}

Apakah data sudah benar?"""
        
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("✅ Ya, simpan", callback_data="asset_add_confirm"))
        markup.add(types.InlineKeyboardButton("❌ Batal", callback_data="asset_add_cancel"))
        
        bot.send_message(call.message.chat.id, text, reply_markup=markup, parse_mode='Markdown')
        bot.answer_callback_query(call.id)

    @bot.callback_query_handler(func=lambda call: call.data.startswith('sync_asset_'))
    def sync_asset_callback(call):
        user_id = call.from_user.id
        asset_id = int(call.data.split('_')[-1])
        
        # Show loading message dan disable tombol
        bot.answer_callback_query(call.id, "[SYNC] Sedang sinkronisasi...", show_alert=False)
        
        # Hapus keyboard untuk mencegah double click
        try:
            loading_markup = types.InlineKeyboardMarkup()
            loading_markup.add(types.InlineKeyboardButton("[LOADING] Sinkronisasi...", callback_data="loading"))
            bot.edit_message_reply_markup(
                call.message.chat.id, 
                call.message.message_id, 
                reply_markup=loading_markup
            )
        except Exception as e:
            logger.error(f"Error updating markup: {e}")
        
        db = SessionLocal()
        try:
            user = db.query(User).filter(User.telegram_id == user_id).first()
            if not user:
                bot.answer_callback_query(call.id, "[ERROR] User tidak ditemukan.")
                return
                
            asset = db.query(Asset).filter(Asset.id == asset_id, Asset.user_id == user.id, Asset.is_active == True).first()
            if not asset:
                bot.answer_callback_query(call.id, "[ERROR] Aset tidak ditemukan.")
                return
                
            service = AssetService(db)
            updated = service.sync_asset_price(asset)
            if updated:
                ret = asset.return_value or 0.0
                ret_pct = asset.return_percent or 0.0
                text = f"[OK] Harga {asset.name} disinkronisasi!\nHarga terakhir: {format_currency_idr(asset.last_price)}\nReturn: {format_currency_idr(ret)} ({ret_pct:.2f}%)"
                bot.answer_callback_query(call.id, text, show_alert=True)
            else:
                bot.answer_callback_query(call.id, "[ERROR] Gagal sinkron harga. Coba lagi nanti.", show_alert=True)
                
            # Refresh the asset list dengan delay kecil
            import time
            time.sleep(0.5)  # Beri waktu callback query selesai
            asset_command(call.message)
            
        except Exception as e:
            logger.error(f"Error in sync_asset_callback: {e}")
            bot.answer_callback_query(call.id, f"[ERROR] Gagal sinkronisasi: {str(e)}", show_alert=True)
        finally:
            db.close()

    # Tambahkan handler untuk loading state
    @bot.callback_query_handler(func=lambda call: call.data == 'loading')
    def loading_callback(call):
        """Handle loading button clicks"""
        bot.answer_callback_query(call.id, "[INFO] Masih memproses, mohon tunggu...", show_alert=False)
    @bot.callback_query_handler(func=lambda call: call.data == 'asset_list')
    def asset_list_callback(call):
        """Handle asset list callback"""
        try:
            user_id = call.from_user.id
            db = SessionLocal()
            try:
                user = db.query(User).filter(User.telegram_id == user_id).first()
                if not user:
                    bot.answer_callback_query(call.id, "❌ User tidak ditemukan.")
                    return
                
                service = AssetService(db)
                assets = service.get_user_assets(user.id)
                
                if not assets:
                    text = "📭 *Daftar Aset Kosong*\n\nAnda belum memiliki aset apapun.\nGunakan tombol 'Tambah Aset' untuk menambah investasi pertama Anda."
                    markup = types.InlineKeyboardMarkup()
                    markup.add(types.InlineKeyboardButton("➕ Tambah Aset", callback_data="asset_add"))
                    markup.add(types.InlineKeyboardButton("🔙 Menu Utama", callback_data="back_to_main"))
                else:
                    text = "💼 *Daftar Aset Anda:*\n\n"
                    markup = types.InlineKeyboardMarkup()
                    total_value = 0
                    total_return = 0
                    
                    for asset in assets:
                        current_value = asset.get_current_value()
                        ret = asset.return_value or 0.0
                        ret_pct = asset.return_percent or 0.0
                        
                        total_value += current_value
                        total_return += ret
                        
                        text += f"📈 *{asset.name}* ({asset.symbol.upper()})\n"
                        if asset.asset_type == 'saham':
                            text += f"   Jumlah: {asset.quantity} lot ({asset.get_actual_quantity()} lembar)\n"
                        else:
                            text += f"   Jumlah: {asset.quantity}\n"
                        text += f"   Harga Beli: {format_currency_idr(asset.buy_price)}\n"
                        text += f"   Harga Terakhir: {format_currency_idr(asset.last_price) if asset.last_price else '-'}\n"
                        text += f"   Nilai Sekarang: {format_currency_idr(current_value)}\n"
                        text += f"   Return: {format_currency_idr(ret)} ({ret_pct:.2f}%)\n\n"
                        
                        # Buttons for each asset
                        row = [
                            types.InlineKeyboardButton(f"✏️ Edit", callback_data=f"edit_asset_{asset.id}"),
                            types.InlineKeyboardButton(f"🗑️ Hapus", callback_data=f"delete_asset_{asset.id}")
                        ]
                        markup.row(*row)
                    
                    text += f"💰 *Total Nilai: {format_currency_idr(total_value)}*\n"
                    text += f"📊 *Total Return: {format_currency_idr(total_return)}*"
                    
                    # Add navigation buttons
                    markup.add(types.InlineKeyboardButton("🔄 Sinkron Semua", callback_data="asset_sync_all"))
                    markup.add(types.InlineKeyboardButton("🔙 Menu Utama", callback_data="back_to_main"))
                
                bot.edit_message_text(
                    text,
                    call.message.chat.id,
                    call.message.message_id,
                    reply_markup=markup,
                    parse_mode='Markdown'
                )
                bot.answer_callback_query(call.id)
                
            finally:
                db.close()
                
        except Exception as e:
            logger.error(f"Error in asset list callback: {e}")
            bot.answer_callback_query(call.id, "❌ Terjadi kesalahan")

    @bot.callback_query_handler(func=lambda call: call.data == 'asset_add')
    def asset_add_callback(call):
        """Mulai proses tambah aset interaktif"""
        user_id = call.from_user.id
        # Reset state user sebelum memulai
        asset_states[user_id] = {'step': 'type'}
        text = "➕ *Tambah Aset Baru*\n\nPilih jenis aset yang ingin Anda tambahkan:"
        markup = types.InlineKeyboardMarkup()
        markup.add(
            types.InlineKeyboardButton("📈 Saham", callback_data="asset_add_jenis_saham"),
            types.InlineKeyboardButton("₿ Kripto", callback_data="asset_add_jenis_kripto")
        )
        markup.add(types.InlineKeyboardButton("🔙 Kembali", callback_data="asset_list"))
        bot.edit_message_text(
            text,
            call.message.chat.id,
            call.message.message_id,
            reply_markup=markup,
            parse_mode='Markdown'
        )
        bot.answer_callback_query(call.id)

    @bot.callback_query_handler(func=lambda call: call.data in ['asset_add_jenis_saham', 'asset_add_jenis_kripto'])
    def asset_add_jenis_callback(call):
        user_id = call.from_user.id
        tipe = 'saham' if call.data == 'asset_add_jenis_saham' else 'kripto'
        # Pastikan state user sudah ada sebelum update
        if user_id not in asset_states:
            asset_states[user_id] = {}
        asset_states[user_id]['step'] = 'symbol'
        asset_states[user_id]['type'] = tipe
        
        text = f"Masukkan *symbol* {tipe.upper()} (misal: BBRI atau bitcoin):"
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("❌ Batalkan", callback_data="asset_add_cancel"))
        
        bot.send_message(call.message.chat.id, text, reply_markup=markup, parse_mode='Markdown')
        bot.answer_callback_query(call.id)

    @bot.callback_query_handler(func=lambda call: call.data == 'asset_add_confirm')
    def asset_add_confirm_callback(call):
        user_id = call.from_user.id
        data = asset_states.get(user_id)
        if not data or data.get('step') != 'confirm':
            bot.answer_callback_query(call.id, "Data tidak ditemukan atau sesi expired.", show_alert=True)
            return
        
        # Validasi data lengkap
        required_fields = ['type', 'symbol', 'quantity', 'buy_price', 'wallet_id']
        for field in required_fields:
            if field not in data:
                bot.answer_callback_query(call.id, f"Data {field} tidak lengkap.", show_alert=True)
                return
        
        # Gunakan nama dari data atau fallback ke symbol jika tidak ada
        asset_name = data.get('name', data.get('symbol', 'Unknown Asset'))
        
        db = SessionLocal()
        try:
            user = db.query(User).filter(User.telegram_id == user_id).first()
            if not user:
                bot.answer_callback_query(call.id, "User tidak ditemukan.", show_alert=True)
                return
                
            service = AssetService(db)
            asset = service.add_asset(
                user_id=user.id,
                wallet_id=data['wallet_id'],
                name=asset_name,
                asset_type=data['type'],
                symbol=data['symbol'],
                quantity=data['quantity'],
                buy_price=data['buy_price']
            )
            text = f"✅ *Aset berhasil ditambahkan!*\n\n📈 {asset.name} ({asset.symbol.upper()})\n💰 {asset.quantity} @ {format_currency_idr(asset.buy_price)}"
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton("📋 Lihat Daftar Aset", callback_data="asset_list"))
            markup.add(types.InlineKeyboardButton("➕ Tambah Lagi", callback_data="asset_add"))
            bot.send_message(call.message.chat.id, text, reply_markup=markup, parse_mode='Markdown')
        except Exception as e:
            logger.error(f"Error saving asset: {e}")
            bot.send_message(call.message.chat.id, "❌ Gagal menyimpan aset. Coba lagi nanti.")
        finally:
            db.close()
            asset_states.pop(user_id, None)
        bot.answer_callback_query(call.id)

    @bot.callback_query_handler(func=lambda call: call.data == 'asset_add_cancel')
    def asset_add_cancel_callback(call):
        user_id = call.from_user.id
        
        # Clear user state
        asset_states.pop(user_id, None)
        
        # Pesan pembatalan dengan peringatan
        text = """⚠️ *Input Aset Dibatalkan*

Semua data yang telah Anda masukkan akan dihilangkan dan tidak tersimpan.

Untuk menambah aset kembali, silakan pilih tombol "Tambah Aset" atau gunakan command `/tambahaset`."""
        
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("➕ Tambah Aset Lagi", callback_data="asset_add"))
        markup.add(types.InlineKeyboardButton("📋 Daftar Aset", callback_data="asset_list"))
        markup.add(types.InlineKeyboardButton("🔙 Menu Utama", callback_data="back_to_main"))
        
        bot.send_message(call.message.chat.id, text, reply_markup=markup, parse_mode='Markdown')
        bot.answer_callback_query(call.id, "Input dibatalkan", show_alert=False)

    @bot.callback_query_handler(func=lambda call: call.data == 'asset_sync')
    def asset_sync_callback(call):
        """Handle asset sync callback"""
        try:
            user_id = call.from_user.id
            
            # Show loading message dan disable tombol
            bot.answer_callback_query(call.id, "[SYNC] Memulai sinkronisasi semua aset...", show_alert=False)
            
            # Update message dengan loading indicator
            try:
                loading_markup = types.InlineKeyboardMarkup()
                loading_markup.add(types.InlineKeyboardButton("[LOADING] Sedang sinkronisasi...", callback_data="loading"))
                loading_markup.add(types.InlineKeyboardButton("[CANCEL] Batal", callback_data="asset_menu"))
                bot.edit_message_reply_markup(
                    call.message.chat.id, 
                    call.message.message_id, 
                    reply_markup=loading_markup
                )
            except Exception as e:
                logger.error(f"Error updating markup: {e}")
            
            db = SessionLocal()
            try:
                user = db.query(User).filter(User.telegram_id == user_id).first()
                if not user:
                    bot.answer_callback_query(call.id, "[ERROR] User tidak ditemukan.")
                    return
                
                service = AssetService(db)
                assets = service.get_user_assets(user.id)
                
                if not assets:
                    bot.answer_callback_query(call.id, "[INFO] Tidak ada aset untuk disinkronisasi.")
                    return
                
                synced_count = 0
                failed_count = 0
                success_assets = []
                failed_assets = []
                
                # Progress update untuk setiap aset
                for i, asset in enumerate(assets):
                    try:
                        # Update progress
                        progress_text = f"[SYNC] Memproses {i+1}/{len(assets)}: {asset.symbol}"
                        if i > 0:  # Avoid rate limiting callback queries
                            try:
                                bot.edit_message_text(
                                    progress_text,
                                    call.message.chat.id,
                                    call.message.message_id,
                                    reply_markup=loading_markup
                                )
                            except:
                                pass
                        
                        # Sync price
                        if service.sync_asset_price(asset):
                            synced_count += 1
                            success_assets.append(asset.symbol)
                        else:
                            failed_count += 1
                            failed_assets.append(asset.symbol)
                            
                        # Small delay to avoid hitting API limits
                        if i < len(assets) - 1:  # Don't delay on last item
                            import time
                            time.sleep(0.5)
                            
                    except Exception as e:
                        logger.error(f"Error syncing asset {asset.symbol}: {e}")
                        failed_count += 1
                        failed_assets.append(asset.symbol)
                
                # Build result message
                result_text = f"[OK] Sinkronisasi Harga Selesai\n\n"
                result_text += f"Berhasil: {synced_count}/{len(assets)} aset\n"
                if failed_count > 0:
                    result_text += f"Gagal: {failed_count} aset\n"
                
                if success_assets:
                    result_text += f"\nBerhasil: {', '.join(success_assets[:5])}"
                    if len(success_assets) > 5:
                        result_text += f" dan {len(success_assets)-5} lainnya"
                        
                if failed_assets:
                    result_text += f"\nGagal: {', '.join(failed_assets[:3])}"
                    if len(failed_assets) > 3:
                        result_text += f" dan {len(failed_assets)-3} lainnya"
                
                bot.answer_callback_query(call.id, result_text, show_alert=True)
                
                # Refresh the asset list dengan delay
                import time
                time.sleep(0.5)
                asset_list_callback(call)
                
            finally:
                db.close()
                
        except Exception as e:
            logger.error(f"Error in asset sync callback: {e}")
            bot.answer_callback_query(call.id, f"[ERROR] Gagal sinkronisasi: {str(e)}", show_alert=True)

    @bot.callback_query_handler(func=lambda call: call.data == 'asset_portfolio')
    def asset_portfolio_callback(call):
        """Handle asset portfolio callback"""
        try:
            user_id = call.from_user.id
            db = SessionLocal()
            try:
                user = db.query(User).filter(User.telegram_id == user_id).first()
                if not user:
                    bot.answer_callback_query(call.id, "❌ User tidak ditemukan.")
                    return
                
                service = AssetService(db)
                assets = service.get_user_assets(user.id)
                
                if not assets:
                    text = "📭 *Portofolio Kosong*\n\nAnda belum memiliki investasi apapun."
                else:
                    # Calculate portfolio summary
                    total_investment = 0
                    total_current_value = 0
                    total_return = 0
                    saham_count = 0
                    kripto_count = 0
                    
                    for asset in assets:
                        investment = asset.get_total_cost()
                        current_value = asset.get_current_value()
                        
                        total_investment += investment
                        total_current_value += current_value
                        total_return += (current_value - investment)
                        
                        if asset.asset_type == 'saham':
                            saham_count += 1
                        elif asset.asset_type == 'kripto':
                            kripto_count += 1
                    
                    total_return_pct = (total_return / total_investment) * 100 if total_investment > 0 else 0
                    
                    text = f"💼 *Overview Portofolio*\n\n"
                    text += f"📊 **Ringkasan:**\n"
                    text += f"• Total Aset: {len(assets)}\n"
                    text += f"• Saham: {saham_count} | Kripto: {kripto_count}\n\n"
                    text += f"💰 **Finansial:**\n"
                    text += f"• Modal: {format_currency_idr(total_investment)}\n"
                    text += f"• Nilai Sekarang: {format_currency_idr(total_current_value)}\n"
                    text += f"• Return: {format_currency_idr(total_return)}\n"
                    text += f"• Return %: {total_return_pct:.2f}%\n\n"
                    
                    if total_return >= 0:
                        text += "📈 *Portofolio Anda menguntungkan!*"
                    else:
                        text += "📉 *Portofolio Anda merugi. Stay strong!*"
                
                markup = types.InlineKeyboardMarkup()
                markup.add(types.InlineKeyboardButton("📋 Lihat Detail", callback_data="asset_list"))
                markup.add(types.InlineKeyboardButton("🔙 Menu Utama", callback_data="back_to_main"))
                
                bot.edit_message_text(
                    text,
                    call.message.chat.id,
                    call.message.message_id,
                    reply_markup=markup,
                    parse_mode='Markdown'
                )
                bot.answer_callback_query(call.id)
                
            finally:
                db.close()
                
        except Exception as e:
            logger.error(f"Error in asset portfolio callback: {e}")
            bot.answer_callback_query(call.id, "❌ Terjadi kesalahan")

    @bot.callback_query_handler(func=lambda call: call.data == 'asset_stock')
    def asset_stock_callback(call):
        """Handle stock assets callback"""
        try:
            user_id = call.from_user.id
            db = SessionLocal()
            try:
                user = db.query(User).filter(User.telegram_id == user_id).first()
                if not user:
                    bot.answer_callback_query(call.id, "❌ User tidak ditemukan.")
                    return
                
                service = AssetService(db)
                saham_assets = service.get_user_assets_by_type(user.id, 'saham')
                
                if not saham_assets:
                    text = "📈 *Aset Saham*\n\nAnda belum memiliki investasi saham."
                    markup = types.InlineKeyboardMarkup()
                    markup.add(types.InlineKeyboardButton("➕ Tambah Saham", callback_data="asset_add_saham"))
                else:
                    text = "📈 *Portofolio Saham*\n\n"
                    markup = types.InlineKeyboardMarkup()
                    
                    for asset in saham_assets:
                        current_value = asset.get_current_value()
                        ret = asset.return_value or 0.0
                        ret_pct = asset.return_percent or 0.0
                        
                        text += f"📊 *{asset.name}* ({asset.symbol.upper()})\n"
                        text += f"   Jumlah: {asset.quantity} lot ({asset.get_actual_quantity()} lembar)\n"
                        text += f"   Nilai: {format_currency_idr(current_value)}\n"
                        text += f"   Return: {format_currency_idr(ret)} ({ret_pct:.2f}%)\n\n"
                    
                    markup.add(types.InlineKeyboardButton("🔄 Sinkron Saham", callback_data="sync_stock_all"))
                    markup.add(types.InlineKeyboardButton("➕ Tambah Saham", callback_data="asset_add_saham"))
                
                markup.add(types.InlineKeyboardButton("🔙 Kembali", callback_data="asset_menu"))
                
                bot.edit_message_text(
                    text,
                    call.message.chat.id,
                    call.message.message_id,
                    reply_markup=markup,
                    parse_mode='Markdown'
                )
                bot.answer_callback_query(call.id)
                
            finally:
                db.close()
                
        except Exception as e:
            logger.error(f"Error in asset stock callback: {e}")
            bot.answer_callback_query(call.id, "❌ Terjadi kesalahan")

    @bot.callback_query_handler(func=lambda call: call.data == 'asset_crypto')
    def asset_crypto_callback(call):
        """Handle crypto assets callback"""
        try:
            user_id = call.from_user.id
            db = SessionLocal()
            try:
                user = db.query(User).filter(User.telegram_id == user_id).first()
                if not user:
                    bot.answer_callback_query(call.id, "❌ User tidak ditemukan.")
                    return
                
                service = AssetService(db)
                crypto_assets = service.get_user_assets_by_type(user.id, 'kripto')
                
                if not crypto_assets:
                    text = "₿ *Aset Kripto*\n\nAnda belum memiliki investasi kripto."
                    markup = types.InlineKeyboardMarkup()
                    markup.add(types.InlineKeyboardButton("➕ Tambah Kripto", callback_data="asset_add_kripto"))
                else:
                    text = "₿ *Portofolio Kripto*\n\n"
                    markup = types.InlineKeyboardMarkup()
                    
                    for asset in crypto_assets:
                        current_value = asset.get_current_value()
                        ret = asset.return_value or 0.0
                        ret_pct = asset.return_percent or 0.0
                        
                        text += f"💰 *{asset.name}* ({asset.symbol.upper()})\n"
                        text += f"   Jumlah: {asset.quantity}\n"
                        text += f"   Nilai: {format_currency_idr(current_value)}\n"
                        text += f"   Return: {format_currency_idr(ret)} ({ret_pct:.2f}%)\n\n"
                    
                    markup.add(types.InlineKeyboardButton("🔄 Sinkron Kripto", callback_data="sync_crypto_all"))
                    markup.add(types.InlineKeyboardButton("➕ Tambah Kripto", callback_data="asset_add_kripto"))
                
                markup.add(types.InlineKeyboardButton("🔙 Kembali", callback_data="asset_menu"))
                
                bot.edit_message_text(
                    text,
                    call.message.chat.id,
                    call.message.message_id,
                    reply_markup=markup,
                    parse_mode='Markdown'
                )
                bot.answer_callback_query(call.id)
                
            finally:
                db.close()
                
        except Exception as e:
            logger.error(f"Error in asset crypto callback: {e}")
            bot.answer_callback_query(call.id, "❌ Terjadi kesalahan")

    # Add asset type specific handlers
    @bot.callback_query_handler(func=lambda call: call.data == 'asset_add_saham')
    def asset_add_saham_callback(call):
        """Handle add stock asset callback"""
        try:
            text = "📈 *Tambah Saham Baru*\n\nMasukkan detail saham dengan format:\n`/tambahaset saham [symbol] [nama] [jumlah] [harga_beli] [wallet]`\n\nContoh:\n`/tambahaset saham BBRI Bank BRI 100 4500 Investasi`"
            
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton("🔙 Kembali", callback_data="asset_add"))
            
            bot.edit_message_text(
                text,
                call.message.chat.id,
                call.message.message_id,
                reply_markup=markup,
                parse_mode='Markdown'
            )
            bot.answer_callback_query(call.id)
            
        except Exception as e:
            logger.error(f"Error in asset add saham callback: {e}")
            bot.answer_callback_query(call.id, "❌ Terjadi kesalahan")

    @bot.callback_query_handler(func=lambda call: call.data == 'asset_add_kripto')
    def asset_add_kripto_callback(call):
        """Handle add crypto asset callback"""
        try:
            text = "₿ *Tambah Kripto Baru*\n\nMasukkan detail kripto dengan format:\n`/tambahaset kripto [symbol] [nama] [jumlah] [harga_beli] [wallet]`\n\nContoh:\n`/tambahaset kripto bitcoin Bitcoin 0.001 700000000 Investasi`"
            
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton("🔙 Kembali", callback_data="asset_add"))
            
            bot.edit_message_text(
                text,
                call.message.chat.id,
                call.message.message_id,
                reply_markup=markup,
                parse_mode='Markdown'
            )
            bot.answer_callback_query(call.id)
            
        except Exception as e:
            logger.error(f"Error in asset add kripto callback: {e}")
            bot.answer_callback_query(call.id, "❌ Terjadi kesalahan")
