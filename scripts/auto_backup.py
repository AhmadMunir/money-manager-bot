#!/usr/bin/env python3
"""
Auto Backup Integration untuk Finance Bot
Otomatis backup saat ada perubahan penting
"""
import os
import sys
import logging
from datetime import datetime
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from scripts.backup_system import BackupManager

logger = logging.getLogger(__name__)

class AutoBackupIntegration:
    def __init__(self):
        self.backup_manager = BackupManager()
        
    def backup_before_asset_operation(self, operation_type, user_id):
        """Backup sebelum operasi aset penting"""
        if operation_type in ['bulk_delete', 'schema_change', 'data_migration']:
            reason = f"Before {operation_type} by user {user_id}"
            success, backup_name = self.backup_manager.create_full_backup("auto_asset", reason)
            
            if success:
                logger.info(f"✅ Auto backup sebelum {operation_type}: {backup_name}")
                return backup_name
            else:
                logger.error(f"❌ Auto backup gagal sebelum {operation_type}")
                return None
        return None
    
    def backup_before_bot_restart(self):
        """Backup sebelum restart bot"""
        reason = "Before bot restart/update"
        success, backup_name = self.backup_manager.create_full_backup("auto_restart", reason)
        
        if success:
            logger.info(f"✅ Auto backup sebelum restart: {backup_name}")
            return backup_name
        else:
            logger.error("❌ Auto backup gagal sebelum restart")
            return None
    
    def scheduled_backup(self):
        """Backup terjadwal (harian)"""
        reason = "Scheduled daily backup"
        success, backup_name = self.backup_manager.create_full_backup("scheduled", reason)
        
        if success:
            logger.info(f"✅ Scheduled backup berhasil: {backup_name}")
            return backup_name
        else:
            logger.error("❌ Scheduled backup gagal")
            return None

# Integration hooks untuk bot handlers
def create_backup_decorator(backup_type="auto"):
    """Decorator untuk auto backup sebelum operasi tertentu"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            # Create backup before operation
            auto_backup = AutoBackupIntegration()
            
            if backup_type == "asset_operation":
                backup_name = auto_backup.backup_before_asset_operation("bulk_operation", "system")
            elif backup_type == "bot_restart":
                backup_name = auto_backup.backup_before_bot_restart()
            else:
                backup_name = auto_backup.backup_manager.create_full_backup(backup_type, f"Before {func.__name__}")
            
            if backup_name:
                logger.info(f"🛡️ Backup dibuat sebelum {func.__name__}: {backup_name}")
            
            # Execute original function
            try:
                result = func(*args, **kwargs)
                return result
            except Exception as e:
                logger.error(f"❌ Error in {func.__name__}: {e}")
                if backup_name:
                    logger.info(f"💡 Backup tersedia untuk recovery: {backup_name}")
                raise
                
        return wrapper
    return decorator
