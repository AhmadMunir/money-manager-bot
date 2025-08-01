import re
from datetime import datetime, timedelta
from typing import Tuple, Optional
import pytz
from babel.numbers import format_currency
import logging

logger = logging.getLogger(__name__)

def safe_answer_callback_query(bot, callback_query_id, text=None, show_alert=False):
    """Safely answer callback query, ignoring timeout errors"""
    try:
        bot.answer_callback_query(callback_query_id, text, show_alert)
    except Exception as e:
        logger.debug(f"Callback query timeout/error (ignored): {e}")
        pass

def format_currency_idr(amount: float) -> str:
    """Format currency in Indonesian Rupiah"""
    try:
        return f"Rp {amount:,.0f}".replace(',', '.')
    except:
        return f"Rp {amount}"

def parse_amount(text: str) -> Optional[float]:
    """Parse amount from text, handling various formats"""
    # Remove currency symbols and common words
    text = re.sub(r'[Rp\$€£¥]', '', text)
    text = re.sub(r'\b(ribu|rb|k|juta|jt|m|miliar|b)\b', lambda m: {
        'ribu': '000', 'rb': '000', 'k': '000',
        'juta': '000000', 'jt': '000000', 'm': '000000',
        'miliar': '000000000', 'b': '000000000'
    }.get(m.group(0).lower(), ''), text, flags=re.IGNORECASE)
    
    # Extract number
    match = re.search(r'[\d,.]+', text.replace('.', '').replace(',', '.'))
    if match:
        try:
            return float(match.group().replace(',', '.'))
        except ValueError:
            return None
    return None

def parse_transaction_text(text: str) -> Tuple[Optional[float], str, str]:
    """
    Parse transaction text like '/in 50000 gaji dari BCA'
    Returns: (amount, description, wallet_name)
    """
    # Remove command
    text = re.sub(r'^/(in|out|income|expense)\s*', '', text, flags=re.IGNORECASE).strip()
    
    # Try to extract amount (first number found)
    amount_match = re.search(r'([\d,.k]+(?:\s*(?:ribu|rb|juta|jt|miliar|b))?)', text, re.IGNORECASE)
    amount = None
    description = ""
    wallet_name = ""
    
    if amount_match:
        amount_str = amount_match.group(1)
        amount = parse_amount(amount_str)
        
        # Remove amount from text
        remaining_text = text.replace(amount_match.group(0), '', 1).strip()
        
        # Look for wallet indicators
        wallet_indicators = r'\b(?:dari|to|ke|untuk|pakai|via|lewat|with|from)\s+([^\s]+(?:\s+[^\s]+)*?)(?:\s|$)'
        wallet_match = re.search(wallet_indicators, remaining_text, re.IGNORECASE)
        
        if wallet_match:
            wallet_name = wallet_match.group(1).strip()
            # Remove wallet part from description
            description = re.sub(wallet_indicators, '', remaining_text, flags=re.IGNORECASE).strip()
        else:
            description = remaining_text
    
    return amount, description, wallet_name

def parse_transfer_text(text: str) -> Tuple[Optional[float], str, str]:
    """
    Parse transfer text like '/transfer 100000 BCA Dompet'
    Returns: (amount, from_wallet, to_wallet)
    """
    # Remove command
    text = re.sub(r'^/transfer\s*', '', text, flags=re.IGNORECASE).strip()
    
    # Extract amount
    amount_match = re.search(r'([\d,.k]+(?:\s*(?:ribu|rb|juta|jt|miliar|b))?)', text, re.IGNORECASE)
    amount = None
    from_wallet = ""
    to_wallet = ""
    
    if amount_match:
        amount_str = amount_match.group(1)
        amount = parse_amount(amount_str)
        
        # Remove amount from text
        remaining_text = text.replace(amount_match.group(0), '', 1).strip()
        
        # Split remaining text to get wallets
        parts = remaining_text.split()
        if len(parts) >= 2:
            from_wallet = parts[0]
            to_wallet = ' '.join(parts[1:])
        elif len(parts) == 1:
            from_wallet = parts[0]
    
    return amount, from_wallet, to_wallet

def get_date_range(period: str, custom_date: Optional[datetime] = None) -> Tuple[datetime, datetime]:
    """Get date range for reports"""
    now = datetime.now()
    
    if period == 'today':
        start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        end = now.replace(hour=23, minute=59, second=59, microsecond=999999)
    elif period == 'yesterday':
        yesterday = now - timedelta(days=1)
        start = yesterday.replace(hour=0, minute=0, second=0, microsecond=0)
        end = yesterday.replace(hour=23, minute=59, second=59, microsecond=999999)
    elif period == 'week':
        # Current week (Monday to Sunday)
        days_since_monday = now.weekday()
        start = (now - timedelta(days=days_since_monday)).replace(hour=0, minute=0, second=0, microsecond=0)
        end = (start + timedelta(days=6)).replace(hour=23, minute=59, second=59, microsecond=999999)
    elif period == 'last_week':
        # Last week
        days_since_monday = now.weekday()
        this_week_start = (now - timedelta(days=days_since_monday)).replace(hour=0, minute=0, second=0, microsecond=0)
        start = this_week_start - timedelta(days=7)
        end = (start + timedelta(days=6)).replace(hour=23, minute=59, second=59, microsecond=999999)
    elif period == 'month':
        # Current month
        start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        if now.month == 12:
            end = now.replace(year=now.year+1, month=1, day=1, hour=0, minute=0, second=0, microsecond=0) - timedelta(microseconds=1)
        else:
            end = now.replace(month=now.month+1, day=1, hour=0, minute=0, second=0, microsecond=0) - timedelta(microseconds=1)
    elif period == 'last_month':
        # Last month
        if now.month == 1:
            start = now.replace(year=now.year-1, month=12, day=1, hour=0, minute=0, second=0, microsecond=0)
            end = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0) - timedelta(microseconds=1)
        else:
            start = now.replace(month=now.month-1, day=1, hour=0, minute=0, second=0, microsecond=0)
            end = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0) - timedelta(microseconds=1)
    else:
        # Custom date or fallback to today
        if custom_date:
            start = custom_date.replace(hour=0, minute=0, second=0, microsecond=0)
            end = custom_date.replace(hour=23, minute=59, second=59, microsecond=999999)
        else:
            start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            end = now.replace(hour=23, minute=59, second=59, microsecond=999999)
    
    return start, end

def format_date(date: datetime, format_type: str = 'short') -> str:
    """Format date for display"""
    if format_type == 'short':
        return date.strftime('%d/%m/%Y')
    elif format_type == 'long':
        return date.strftime('%d %B %Y')
    elif format_type == 'datetime':
        return date.strftime('%d/%m/%Y %H:%M')
    else:
        return date.strftime('%d/%m/%Y')

def calculate_percentage_change(current: float, previous: float) -> Tuple[float, str]:
    """Calculate percentage change and return with trend indicator"""
    if previous == 0:
        if current > 0:
            return float('inf'), "📈"
        elif current < 0:
            return float('-inf'), "📉"
        else:
            return 0.0, "➡️"
    
    percentage = ((current - previous) / abs(previous)) * 100
    
    if percentage > 0:
        trend = "📈"
    elif percentage < 0:
        trend = "📉"
    else:
        trend = "➡️"
    
    return percentage, trend

def validate_wallet_name(name: str) -> bool:
    """Validate wallet name"""
    if not name or len(name.strip()) == 0:
        return False
    if len(name.strip()) > 50:
        return False
    return True

def validate_transaction_amount(amount: float) -> bool:
    """Validate transaction amount"""
    if amount <= 0:
        return False
    if amount > 999999999999:  # Max 999 billion
        return False
    return True

def format_transaction_summary(transaction_type: str, amount: float, description: str, 
                             from_wallet: str = None, to_wallet: str = None, 
                             category: str = None) -> str:
    """Format transaction summary for confirmation"""
    summary = f"📋 *Ringkasan Transaksi*\n\n"
    
    if transaction_type == 'income':
        summary += f"💰 *Jenis:* Pemasukan\n"
        summary += f"💵 *Jumlah:* {format_currency_idr(amount)}\n"
        summary += f"📝 *Deskripsi:* {description}\n"
        if to_wallet:
            summary += f"🏦 *Ke Kantong:* {to_wallet}\n"
    elif transaction_type == 'expense':
        summary += f"💸 *Jenis:* Pengeluaran\n"
        summary += f"💵 *Jumlah:* {format_currency_idr(amount)}\n"
        summary += f"📝 *Deskripsi:* {description}\n"
        if from_wallet:
            summary += f"🏦 *Dari Kantong:* {from_wallet}\n"
    elif transaction_type == 'transfer':
        summary += f"🔄 *Jenis:* Transfer\n"
        summary += f"💵 *Jumlah:* {format_currency_idr(amount)}\n"
        if from_wallet:
            summary += f"📤 *Dari:* {from_wallet}\n"
        if to_wallet:
            summary += f"📥 *Ke:* {to_wallet}\n"
    
    if category:
        summary += f"🏷️ *Kategori:* {category}\n"
    
    summary += f"📅 *Tanggal:* {format_date(datetime.now(), 'datetime')}\n"
    
    return summary

def get_wallet_type_name(wallet_type: str) -> str:
    """Get human-readable wallet type name"""
    type_names = {
        'cash': 'Kas/Tunai',
        'bank': 'Bank',
        'e-wallet': 'E-Wallet',
        'card': 'Kartu',
        'investment': 'Investasi',
        'asset': 'Aset',
        'debt': 'Hutang',
        'receivable': 'Piutang',
        'other': 'Lainnya'
    }
    return type_names.get(wallet_type, 'Tidak Dikenal')

def get_category_name(category_code: str) -> str:
    """Get human-readable category name"""
    categories = {
        # Income categories
        'salary': 'Gaji',
        'business': 'Bisnis',
        'gift': 'Hadiah',
        'investment_income': 'Hasil Investasi',
        'rental': 'Sewa',
        'other_income': 'Pemasukan Lainnya',
        
        # Expense categories
        'food': 'Makanan',
        'housing': 'Rumah Tangga',
        'transport': 'Transportasi',
        'shopping': 'Belanja',
        'health': 'Kesehatan',
        'education': 'Pendidikan',
        'entertainment': 'Hiburan',
        'other_expense': 'Pengeluaran Lainnya'
    }
    return categories.get(category_code, 'Tidak Dikenal')

def truncate_text(text: str, max_length: int = 30) -> str:
    """Truncate text if too long"""
    if len(text) <= max_length:
        return text
    return text[:max_length-3] + "..."
