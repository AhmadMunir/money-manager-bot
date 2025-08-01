import schedule
import time
import threading
from datetime import datetime
import os
from dotenv import load_dotenv
from src.models.database import SessionLocal, User
from src.handlers.report_handler import generate_daily_report
import logging

load_dotenv()
logger = logging.getLogger(__name__)

class SchedulerService:
    def __init__(self):
        self.running = False
        self.thread = None
        self.setup_schedules()
    
    def setup_schedules(self):
        """Setup scheduled tasks"""
        # Daily report time from environment variable
        daily_time = os.getenv('DAILY_REPORT_TIME', '08:00')
        
        # Schedule daily reports
        if os.getenv('AUTO_REPORT_ENABLED', 'False').lower() == 'true':
            schedule.every().day.at(daily_time).do(self.send_daily_reports)
            logger.info(f"Daily reports scheduled at {daily_time}")
        
        # Weekly reports (every Monday)
        weekly_day = os.getenv('WEEKLY_REPORT_DAY', 'monday')
        schedule.every().monday.at(daily_time).do(self.send_weekly_reports)
        
        # Monthly reports (1st day of month)
        # Note: schedule library doesn't support monthly directly
        # This would need a more sophisticated approach
    
    def send_daily_reports(self):
        """Send daily reports to all active users"""
        try:
            logger.info("Starting daily report generation")
            db = SessionLocal()
            
            try:
                # Get all active users
                users = db.query(User).filter(User.is_active == True).all()
                
                for user in users:
                    try:
                        report = generate_daily_report(user.telegram_id)
                        # Here you would send the report via Telegram
                        # This requires access to the bot instance
                        logger.info(f"Daily report generated for user {user.telegram_id}")
                    except Exception as e:
                        logger.error(f"Error generating daily report for user {user.telegram_id}: {e}")
                
                logger.info(f"Daily reports sent to {len(users)} users")
                
            finally:
                db.close()
                
        except Exception as e:
            logger.error(f"Error in daily report job: {e}")
    
    def send_weekly_reports(self):
        """Send weekly reports to all active users"""
        try:
            logger.info("Starting weekly report generation")
            # Similar to daily reports but for weekly
            pass
        except Exception as e:
            logger.error(f"Error in weekly report job: {e}")
    
    def run_scheduler(self):
        """Run the scheduler in a loop"""
        while self.running:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
    
    def start(self):
        """Start the scheduler in a separate thread"""
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self.run_scheduler, daemon=True)
            self.thread.start()
            logger.info("Scheduler started")
    
    def stop(self):
        """Stop the scheduler"""
        if self.running:
            self.running = False
            if self.thread:
                self.thread.join(timeout=5)
            logger.info("Scheduler stopped")
    
    def get_next_run_times(self):
        """Get next scheduled run times"""
        jobs = schedule.jobs
        next_runs = []
        
        for job in jobs:
            next_runs.append({
                'job': str(job.job_func),
                'next_run': job.next_run
            })
        
        return next_runs
