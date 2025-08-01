import telebot
from telebot import types
from sqlalchemy.orm import sessionmaker
from sqlalchemy import func, and_, or_
from datetime import datetime, timedelta
from src.models.database import SessionLocal, User, Wallet, Transaction
from src.utils.keyboards import create_report_menu, create_analysis_menu, create_back_button
from src.utils.helpers import (
    format_currency_idr, get_date_range, format_date,
    calculate_percentage_change, get_category_name,
    safe_answer_callback_query
)
import logging

logger = logging.getLogger(__name__)

def register_report_handlers(bot):
    """Register report handlers"""
    
    @bot.callback_query_handler(func=lambda call: call.data == 'report_menu')
    def report_menu_callback(call):
        """Handle report menu callback"""
        try:
            markup = create_report_menu()
            bot.edit_message_text(
                "📊 *Laporan Keuangan*\n\nPilih periode laporan:",
                call.message.chat.id,
                call.message.message_id,
                reply_markup=markup,
                parse_mode='Markdown'
            )
        except Exception as e:
            logger.error(f"Error in report menu: {e}")
            safe_answer_callback_query(bot, call.id, "❌ Terjadi kesalahan")
    
    @bot.callback_query_handler(func=lambda call: call.data == 'report_daily')
    def daily_report_callback(call):
        """Generate daily report"""
        try:
            user_id = call.from_user.id
            report_text = generate_daily_report(user_id)
            
            markup = create_back_button('report_menu')
            bot.edit_message_text(
                report_text,
                call.message.chat.id,
                call.message.message_id,
                reply_markup=markup,
                parse_mode='Markdown'
            )
            
        except Exception as e:
            logger.error(f"Error in daily report: {e}")
            safe_answer_callback_query(bot, call.id, "❌ Terjadi kesalahan")
    
    @bot.callback_query_handler(func=lambda call: call.data == 'report_weekly')
    def weekly_report_callback(call):
        """Generate weekly report"""
        try:
            user_id = call.from_user.id
            report_text = generate_weekly_report(user_id)
            
            markup = create_back_button('report_menu')
            bot.edit_message_text(
                report_text,
                call.message.chat.id,
                call.message.message_id,
                reply_markup=markup,
                parse_mode='Markdown'
            )
            
        except Exception as e:
            logger.error(f"Error in weekly report: {e}")
            safe_answer_callback_query(bot, call.id, "❌ Terjadi kesalahan")
    
    @bot.callback_query_handler(func=lambda call: call.data == 'report_monthly')
    def monthly_report_callback(call):
        """Generate monthly report"""
        try:
            user_id = call.from_user.id
            report_text = generate_monthly_report(user_id)
            
            markup = create_back_button('report_menu')
            bot.edit_message_text(
                report_text,
                call.message.chat.id,
                call.message.message_id,
                reply_markup=markup,
                parse_mode='Markdown'
            )
            
        except Exception as e:
            logger.error(f"Error in monthly report: {e}")
            safe_answer_callback_query(bot, call.id, "❌ Terjadi kesalahan")
    
    @bot.callback_query_handler(func=lambda call: call.data == 'analysis_menu')
    def analysis_menu_callback(call):
        """Handle analysis menu callback"""
        try:
            markup = create_analysis_menu()
            bot.edit_message_text(
                "📈 *Analisis Keuangan*\n\nPilih jenis analisis:",
                call.message.chat.id,
                call.message.message_id,
                reply_markup=markup,
                parse_mode='Markdown'
            )
        except Exception as e:
            logger.error(f"Error in analysis menu: {e}")
            safe_answer_callback_query(bot, call.id, "❌ Terjadi kesalahan")
    
    @bot.callback_query_handler(func=lambda call: call.data == 'analysis_wow')
    def wow_analysis_callback(call):
        """Generate Week over Week analysis"""
        try:
            user_id = call.from_user.id
            report_text = generate_wow_analysis(user_id)
            
            markup = create_back_button('analysis_menu')
            bot.edit_message_text(
                report_text,
                call.message.chat.id,
                call.message.message_id,
                reply_markup=markup,
                parse_mode='Markdown'
            )
            
        except Exception as e:
            logger.error(f"Error in WoW analysis: {e}")
            safe_answer_callback_query(bot, call.id, "❌ Terjadi kesalahan")
    
    @bot.callback_query_handler(func=lambda call: call.data == 'analysis_mom')
    def mom_analysis_callback(call):
        """Generate Month over Month analysis"""
        try:
            user_id = call.from_user.id
            report_text = generate_mom_analysis(user_id)
            
            markup = create_back_button('analysis_menu')
            bot.edit_message_text(
                report_text,
                call.message.chat.id,
                call.message.message_id,
                reply_markup=markup,
                parse_mode='Markdown'
            )
            
        except Exception as e:
            logger.error(f"Error in MoM analysis: {e}")
            safe_answer_callback_query(bot, call.id, "❌ Terjadi kesalahan")
    
    @bot.message_handler(commands=['report'])
    def report_command(message):
        """Handle /report command"""
        try:
            markup = create_report_menu()
            bot.send_message(
                message.chat.id,
                "📊 *Laporan Keuangan*\n\nPilih periode laporan:",
                reply_markup=markup,
                parse_mode='Markdown'
            )
        except Exception as e:
            logger.error(f"Error in report command: {e}")
            bot.send_message(message.chat.id, "❌ Terjadi kesalahan")

def generate_daily_report(user_id: int) -> str:
    """Generate daily financial report"""
    try:
        db = SessionLocal()
        
        user = db.query(User).filter(User.telegram_id == user_id).first()
        if not user:
            return "❌ User tidak ditemukan"
        
        # Get today's date range
        start_date, end_date = get_date_range('today')
        
        # Get today's transactions
        transactions = db.query(Transaction).filter(
            Transaction.user_id == user.id,
            Transaction.transaction_date.between(start_date, end_date)
        ).all()
        
        # Calculate totals
        total_income = sum(t.amount for t in transactions if t.type == 'income')
        total_expense = sum(t.amount for t in transactions if t.type == 'expense')
        net_flow = total_income - total_expense
        
        # Get wallet balances
        wallets = db.query(Wallet).filter(
            Wallet.user_id == user.id,
            Wallet.is_active == True
        ).all()
        total_balance = sum(w.balance for w in wallets)
        
        report = f"📅 *Laporan Harian*\n"
        report += f"🗓️ {format_date(datetime.now(), 'long')}\n\n"
        
        report += f"💰 *Pemasukan:* {format_currency_idr(total_income)}\n"
        report += f"💸 *Pengeluaran:* {format_currency_idr(total_expense)}\n"
        report += f"📊 *Net Flow:* {format_currency_idr(net_flow)}\n"
        report += f"💯 *Total Saldo:* {format_currency_idr(total_balance)}\n\n"
        
        if transactions:
            report += f"📝 *Transaksi Hari Ini ({len(transactions)}):*\n"
            for t in transactions[-5:]:  # Show last 5 transactions
                emoji = "💰" if t.type == 'income' else "💸"
                report += f"{emoji} {format_currency_idr(t.amount)} - {t.description}\n"
            
            if len(transactions) > 5:
                report += f"... dan {len(transactions) - 5} transaksi lainnya\n"
        else:
            report += "📝 *Tidak ada transaksi hari ini*\n"
        
        db.close()
        return report
        
    except Exception as e:
        logger.error(f"Error generating daily report: {e}")
        return "❌ Terjadi kesalahan saat membuat laporan"

def generate_weekly_report(user_id: int) -> str:
    """Generate weekly financial report"""
    try:
        db = SessionLocal()
        
        user = db.query(User).filter(User.telegram_id == user_id).first()
        if not user:
            return "❌ User tidak ditemukan"
        
        # Get this week's date range
        start_date, end_date = get_date_range('week')
        
        # Get this week's transactions
        transactions = db.query(Transaction).filter(
            Transaction.user_id == user.id,
            Transaction.transaction_date.between(start_date, end_date)
        ).all()
        
        # Calculate totals
        total_income = sum(t.amount for t in transactions if t.type == 'income')
        total_expense = sum(t.amount for t in transactions if t.type == 'expense')
        net_flow = total_income - total_expense
        
        # Get daily breakdown
        daily_expenses = {}
        for t in transactions:
            if t.type == 'expense':
                day = t.transaction_date.strftime('%A')
                daily_expenses[day] = daily_expenses.get(day, 0) + t.amount
        
        report = f"📆 *Laporan Mingguan*\n"
        report += f"🗓️ {format_date(start_date)} - {format_date(end_date)}\n\n"
        
        report += f"💰 *Total Pemasukan:* {format_currency_idr(total_income)}\n"
        report += f"💸 *Total Pengeluaran:* {format_currency_idr(total_expense)}\n"
        report += f"📊 *Net Flow:* {format_currency_idr(net_flow)}\n"
        report += f"📝 *Jumlah Transaksi:* {len(transactions)}\n\n"
        
        if daily_expenses:
            report += f"📊 *Pengeluaran per Hari:*\n"
            for day, amount in sorted(daily_expenses.items()):
                report += f"• {day}: {format_currency_idr(amount)}\n"
        
        # Average daily expense
        avg_daily = total_expense / 7 if total_expense > 0 else 0
        report += f"\n📈 *Rata-rata Pengeluaran Harian:* {format_currency_idr(avg_daily)}"
        
        db.close()
        return report
        
    except Exception as e:
        logger.error(f"Error generating weekly report: {e}")
        return "❌ Terjadi kesalahan saat membuat laporan"

def generate_monthly_report(user_id: int) -> str:
    """Generate monthly financial report"""
    try:
        db = SessionLocal()
        
        user = db.query(User).filter(User.telegram_id == user_id).first()
        if not user:
            return "❌ User tidak ditemukan"
        
        # Get this month's date range
        start_date, end_date = get_date_range('month')
        
        # Get this month's transactions
        transactions = db.query(Transaction).filter(
            Transaction.user_id == user.id,
            Transaction.transaction_date.between(start_date, end_date)
        ).all()
        
        # Calculate totals
        total_income = sum(t.amount for t in transactions if t.type == 'income')
        total_expense = sum(t.amount for t in transactions if t.type == 'expense')
        net_flow = total_income - total_expense
        
        # Get category breakdown for expenses
        category_expenses = {}
        for t in transactions:
            if t.type == 'expense' and t.category_id:
                # This would need category lookup - simplified for now
                category_expenses['Lainnya'] = category_expenses.get('Lainnya', 0) + t.amount
        
        report = f"🗓️ *Laporan Bulanan*\n"
        report += f"📅 {format_date(start_date, 'long')} - {format_date(end_date, 'long')}\n\n"
        
        report += f"💰 *Total Pemasukan:* {format_currency_idr(total_income)}\n"
        report += f"💸 *Total Pengeluaran:* {format_currency_idr(total_expense)}\n"
        report += f"📊 *Net Flow:* {format_currency_idr(net_flow)}\n"
        report += f"📝 *Jumlah Transaksi:* {len(transactions)}\n\n"
        
        # Savings rate
        if total_income > 0:
            savings_rate = (net_flow / total_income) * 100
            report += f"💳 *Tingkat Tabungan:* {savings_rate:.1f}%\n\n"
        
        # Average daily expense
        days_in_month = (end_date - start_date).days + 1
        avg_daily = total_expense / days_in_month if total_expense > 0 else 0
        report += f"📈 *Rata-rata Pengeluaran Harian:* {format_currency_idr(avg_daily)}\n"
        
        # Spending projection
        days_passed = (datetime.now() - start_date).days + 1
        if days_passed > 0 and total_expense > 0:
            projected_monthly = (total_expense / days_passed) * days_in_month
            report += f"🔮 *Proyeksi Pengeluaran Bulanan:* {format_currency_idr(projected_monthly)}"
        
        db.close()
        return report
        
    except Exception as e:
        logger.error(f"Error generating monthly report: {e}")
        return "❌ Terjadi kesalahan saat membuat laporan"

def generate_wow_analysis(user_id: int) -> str:
    """Generate Week over Week analysis"""
    try:
        db = SessionLocal()
        
        user = db.query(User).filter(User.telegram_id == user_id).first()
        if not user:
            return "❌ User tidak ditemukan"
        
        # Get this week and last week data
        this_week_start, this_week_end = get_date_range('week')
        last_week_start, last_week_end = get_date_range('last_week')
        
        # This week transactions
        this_week_transactions = db.query(Transaction).filter(
            Transaction.user_id == user.id,
            Transaction.transaction_date.between(this_week_start, this_week_end)
        ).all()
        
        # Last week transactions
        last_week_transactions = db.query(Transaction).filter(
            Transaction.user_id == user.id,
            Transaction.transaction_date.between(last_week_start, last_week_end)
        ).all()
        
        # Calculate totals
        this_week_income = sum(t.amount for t in this_week_transactions if t.type == 'income')
        this_week_expense = sum(t.amount for t in this_week_transactions if t.type == 'expense')
        
        last_week_income = sum(t.amount for t in last_week_transactions if t.type == 'income')
        last_week_expense = sum(t.amount for t in last_week_transactions if t.type == 'expense')
        
        # Calculate percentage changes
        income_change, income_trend = calculate_percentage_change(this_week_income, last_week_income)
        expense_change, expense_trend = calculate_percentage_change(this_week_expense, last_week_expense)
        
        report = f"📈 *Analisis Week over Week*\n\n"
        
        report += f"💰 *Pemasukan:*\n"
        report += f"• Minggu ini: {format_currency_idr(this_week_income)}\n"
        report += f"• Minggu lalu: {format_currency_idr(last_week_income)}\n"
        if income_change != float('inf') and income_change != float('-inf'):
            report += f"• Perubahan: {income_trend} {abs(income_change):.1f}%\n\n"
        else:
            report += f"• Perubahan: {income_trend} Baru ada data\n\n"
        
        report += f"💸 *Pengeluaran:*\n"
        report += f"• Minggu ini: {format_currency_idr(this_week_expense)}\n"
        report += f"• Minggu lalu: {format_currency_idr(last_week_expense)}\n"
        if expense_change != float('inf') and expense_change != float('-inf'):
            report += f"• Perubahan: {expense_trend} {abs(expense_change):.1f}%\n\n"
        else:
            report += f"• Perubahan: {expense_trend} Baru ada data\n\n"
        
        # Insights
        report += f"💡 *Insight:*\n"
        if expense_change > 10:
            report += f"⚠️ Pengeluaran naik signifikan ({expense_change:.1f}%)\n"
        elif expense_change < -10:
            report += f"✅ Pengeluaran turun signifikan ({abs(expense_change):.1f}%)\n"
        else:
            report += f"➡️ Pengeluaran relatif stabil\n"
        
        db.close()
        return report
        
    except Exception as e:
        logger.error(f"Error generating WoW analysis: {e}")
        return "❌ Terjadi kesalahan saat membuat analisis"

def generate_mom_analysis(user_id: int) -> str:
    """Generate Month over Month analysis"""
    try:
        db = SessionLocal()
        
        user = db.query(User).filter(User.telegram_id == user_id).first()
        if not user:
            return "❌ User tidak ditemukan"
        
        # Get this month and last month data
        this_month_start, this_month_end = get_date_range('month')
        last_month_start, last_month_end = get_date_range('last_month')
        
        # This month transactions
        this_month_transactions = db.query(Transaction).filter(
            Transaction.user_id == user.id,
            Transaction.transaction_date.between(this_month_start, this_month_end)
        ).all()
        
        # Last month transactions
        last_month_transactions = db.query(Transaction).filter(
            Transaction.user_id == user.id,
            Transaction.transaction_date.between(last_month_start, last_month_end)
        ).all()
        
        # Calculate totals
        this_month_income = sum(t.amount for t in this_month_transactions if t.type == 'income')
        this_month_expense = sum(t.amount for t in this_month_transactions if t.type == 'expense')
        
        last_month_income = sum(t.amount for t in last_month_transactions if t.type == 'income')
        last_month_expense = sum(t.amount for t in last_month_transactions if t.type == 'expense')
        
        # Calculate percentage changes
        income_change, income_trend = calculate_percentage_change(this_month_income, last_month_income)
        expense_change, expense_trend = calculate_percentage_change(this_month_expense, last_month_expense)
        
        report = f"📊 *Analisis Month over Month*\n\n"
        
        report += f"💰 *Pemasukan:*\n"
        report += f"• Bulan ini: {format_currency_idr(this_month_income)}\n"
        report += f"• Bulan lalu: {format_currency_idr(last_month_income)}\n"
        if income_change != float('inf') and income_change != float('-inf'):
            report += f"• Perubahan: {income_trend} {abs(income_change):.1f}%\n\n"
        else:
            report += f"• Perubahan: {income_trend} Baru ada data\n\n"
        
        report += f"💸 *Pengeluaran:*\n"
        report += f"• Bulan ini: {format_currency_idr(this_month_expense)}\n"
        report += f"• Bulan lalu: {format_currency_idr(last_month_expense)}\n"
        if expense_change != float('inf') and expense_change != float('-inf'):
            report += f"• Perubahan: {expense_trend} {abs(expense_change):.1f}%\n\n"
        else:
            report += f"• Perubahan: {expense_trend} Baru ada data\n\n"
        
        # Net flow comparison
        this_month_net = this_month_income - this_month_expense
        last_month_net = last_month_income - last_month_expense
        net_change, net_trend = calculate_percentage_change(this_month_net, last_month_net)
        
        report += f"📊 *Net Flow:*\n"
        report += f"• Bulan ini: {format_currency_idr(this_month_net)}\n"
        report += f"• Bulan lalu: {format_currency_idr(last_month_net)}\n"
        if net_change != float('inf') and net_change != float('-inf'):
            report += f"• Perubahan: {net_trend} {abs(net_change):.1f}%\n\n"
        else:
            report += f"• Perubahan: {net_trend} Baru ada data\n\n"
        
        # Insights
        report += f"💡 *Insight:*\n"
        if expense_change > 15:
            report += f"⚠️ Pengeluaran naik signifikan bulan ini\n"
        elif expense_change < -15:
            report += f"✅ Pengeluaran turun signifikan bulan ini\n"
        
        if this_month_net > last_month_net:
            report += f"📈 Net flow membaik dari bulan lalu\n"
        elif this_month_net < last_month_net:
            report += f"📉 Net flow menurun dari bulan lalu\n"
        
        db.close()
        return report
        
    except Exception as e:
        logger.error(f"Error generating MoM analysis: {e}")
        return "❌ Terjadi kesalahan saat membuat analisis"
