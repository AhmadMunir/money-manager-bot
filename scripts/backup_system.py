#!/usr/bin/env python3
"""
Sistema Backup Otomatis untuk Finance Bot
Melindungi data saat ada perubahan mayor pada database atau kode
"""
import os
import sqlite3
import shutil
import json
import zipfile
from datetime import datetime, timedelta
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BackupManager:
    def __init__(self, base_dir="."):
        self.base_dir = Path(base_dir)
        self.backup_dir = self.base_dir / "backups"
        self.backup_dir.mkdir(exist_ok=True)
        
        # Konfigurasi backup
        self.max_backups = 10  # Maksimal backup yang disimpan
        self.databases = ["finance_bot.db", "monman.db"]
        self.critical_files = [
            "main.py",
            "src/",
            "requirements.txt",
            ".env.example",
            "README.md"
        ]
        
    def create_backup_name(self, backup_type="auto"):
        """Buat nama backup dengan timestamp"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"backup_{backup_type}_{timestamp}"
    
    def backup_database(self, db_name, backup_name):
        """Backup database dengan data validation"""
        if not os.path.exists(db_name):
            logger.warning(f"Database {db_name} tidak ditemukan")
            return False
            
        try:
            # Validasi database integrity
            if not self.validate_database(db_name):
                logger.error(f"Database {db_name} corrupt, backup dibatalkan")
                return False
                
            # Backup database
            backup_path = self.backup_dir / backup_name / f"{db_name}.backup"
            backup_path.parent.mkdir(exist_ok=True)
            
            shutil.copy2(db_name, backup_path)
            
            # Backup metadata
            metadata = self.get_database_metadata(db_name)
            metadata_path = self.backup_dir / backup_name / f"{db_name}.metadata.json"
            
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f, indent=2, default=str)
                
            logger.info(f"✅ Database {db_name} berhasil dibackup ke {backup_path}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error backup database {db_name}: {e}")
            return False
    
    def validate_database(self, db_name):
        """Validasi integritas database"""
        try:
            conn = sqlite3.connect(db_name)
            cursor = conn.cursor()
            
            # Check integrity
            cursor.execute("PRAGMA integrity_check")
            result = cursor.fetchone()[0]
            
            if result != "ok":
                logger.error(f"Database {db_name} integrity check failed: {result}")
                return False
                
            # Check if critical tables exist
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            
            required_tables = ['users', 'wallets', 'transactions', 'assets']
            missing_tables = [table for table in required_tables if table not in tables]
            
            if missing_tables:
                logger.warning(f"Missing tables in {db_name}: {missing_tables}")
                
            conn.close()
            return True
            
        except Exception as e:
            logger.error(f"Error validating database {db_name}: {e}")
            return False
    
    def get_database_metadata(self, db_name):
        """Ambil metadata database untuk backup"""
        try:
            conn = sqlite3.connect(db_name)
            cursor = conn.cursor()
            
            metadata = {
                "backup_time": datetime.now().isoformat(),
                "database_name": db_name,
                "file_size": os.path.getsize(db_name),
                "tables": {},
                "record_counts": {}
            }
            
            # Get table info
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            
            for table in tables:
                # Table structure
                cursor.execute(f"PRAGMA table_info({table})")
                columns = cursor.fetchall()
                metadata["tables"][table] = [
                    {"name": col[1], "type": col[2], "not_null": col[3], "primary_key": col[5]} 
                    for col in columns
                ]
                
                # Record count
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                metadata["record_counts"][table] = count
            
            conn.close()
            return metadata
            
        except Exception as e:
            logger.error(f"Error getting metadata for {db_name}: {e}")
            return {"error": str(e)}
    
    def backup_code_files(self, backup_name):
        """Backup file kode penting"""
        try:
            backup_path = self.backup_dir / backup_name / "code"
            backup_path.mkdir(parents=True, exist_ok=True)
            
            for item in self.critical_files:
                source_path = self.base_dir / item
                
                if source_path.is_file():
                    # Backup single file
                    dest_path = backup_path / item
                    dest_path.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(source_path, dest_path)
                    logger.info(f"✅ File {item} dibackup")
                    
                elif source_path.is_dir():
                    # Backup directory
                    dest_path = backup_path / item
                    shutil.copytree(source_path, dest_path, dirs_exist_ok=True)
                    logger.info(f"✅ Directory {item} dibackup")
                    
                else:
                    logger.warning(f"⚠️ {item} tidak ditemukan")
                    
            return True
            
        except Exception as e:
            logger.error(f"❌ Error backup code files: {e}")
            return False
    
    def create_full_backup(self, backup_type="manual", reason="User initiated"):
        """Buat backup lengkap (database + code)"""
        backup_name = self.create_backup_name(backup_type)
        backup_path = self.backup_dir / backup_name
        
        logger.info(f"🔄 Memulai backup lengkap: {backup_name}")
        logger.info(f"📝 Alasan: {reason}")
        
        success = True
        backup_info = {
            "backup_name": backup_name,
            "backup_type": backup_type,
            "reason": reason,
            "timestamp": datetime.now().isoformat(),
            "databases": {},
            "code_backup": False,
            "success": False
        }
        
        # Backup databases
        for db_name in self.databases:
            db_success = self.backup_database(db_name, backup_name)
            backup_info["databases"][db_name] = db_success
            if not db_success:
                success = False
                
        # Backup code files
        code_success = self.backup_code_files(backup_name)
        backup_info["code_backup"] = code_success
        if not code_success:
            success = False
            
        # Save backup info
        backup_info["success"] = success
        info_path = backup_path / "backup_info.json"
        with open(info_path, 'w') as f:
            json.dump(backup_info, f, indent=2, default=str)
            
        if success:
            # Create compressed archive
            self.create_backup_archive(backup_name)
            logger.info(f"✅ Backup lengkap selesai: {backup_name}")
        else:
            logger.error(f"❌ Backup gagal: {backup_name}")
            
        # Cleanup old backups
        self.cleanup_old_backups()
        
        return success, backup_name
    
    def create_backup_archive(self, backup_name):
        """Buat archive terkompresi dari backup"""
        try:
            backup_path = self.backup_dir / backup_name
            archive_path = self.backup_dir / f"{backup_name}.zip"
            
            with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(backup_path):
                    for file in files:
                        file_path = Path(root) / file
                        arc_path = file_path.relative_to(backup_path)
                        zipf.write(file_path, arc_path)
            
            # Remove uncompressed backup after successful compression
            shutil.rmtree(backup_path)
            logger.info(f"✅ Backup archive dibuat: {archive_path}")
            
        except Exception as e:
            logger.error(f"❌ Error creating backup archive: {e}")
    
    def cleanup_old_backups(self):
        """Hapus backup lama, simpan hanya yang terbaru"""
        try:
            # Get all backup files
            backup_files = list(self.backup_dir.glob("backup_*.zip"))
            backup_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
            
            # Remove old backups
            if len(backup_files) > self.max_backups:
                for old_backup in backup_files[self.max_backups:]:
                    old_backup.unlink()
                    logger.info(f"🗑️ Backup lama dihapus: {old_backup.name}")
                    
        except Exception as e:
            logger.error(f"❌ Error cleanup old backups: {e}")
    
    def list_backups(self):
        """List semua backup yang tersedia"""
        backups = []
        
        for backup_file in self.backup_dir.glob("backup_*.zip"):
            try:
                # Extract info from filename
                name_parts = backup_file.stem.split('_')
                if len(name_parts) >= 3:
                    backup_type = name_parts[1]
                    timestamp_str = '_'.join(name_parts[2:])
                    timestamp = datetime.strptime(timestamp_str, "%Y%m%d_%H%M%S")
                    
                    backups.append({
                        "file": backup_file.name,
                        "type": backup_type,
                        "timestamp": timestamp,
                        "size": backup_file.stat().st_size,
                        "age_days": (datetime.now() - timestamp).days
                    })
                    
            except Exception as e:
                logger.warning(f"Error parsing backup file {backup_file}: {e}")
                
        backups.sort(key=lambda x: x["timestamp"], reverse=True)
        return backups
    
    def restore_backup(self, backup_name, target_dir="."):
        """Restore backup ke directory tertentu"""
        try:
            backup_file = self.backup_dir / f"{backup_name}.zip"
            
            if not backup_file.exists():
                logger.error(f"Backup file tidak ditemukan: {backup_file}")
                return False
                
            target_path = Path(target_dir)
            restore_path = target_path / f"restored_{backup_name}"
            restore_path.mkdir(exist_ok=True)
            
            # Extract backup
            with zipfile.ZipFile(backup_file, 'r') as zipf:
                zipf.extractall(restore_path)
                
            logger.info(f"✅ Backup berhasil di-restore ke: {restore_path}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error restoring backup: {e}")
            return False
    
    def pre_migration_backup(self, migration_name):
        """Backup khusus sebelum migrasi database"""
        reason = f"Pre-migration backup for: {migration_name}"
        return self.create_full_backup("pre_migration", reason)
    
    def pre_deployment_backup(self, version):
        """Backup khusus sebelum deployment"""
        reason = f"Pre-deployment backup for version: {version}"
        return self.create_full_backup("pre_deployment", reason)

def main():
    """Main function untuk testing backup system"""
    backup_manager = BackupManager()
    
    print("🔧 Finance Bot Backup System")
    print("=" * 40)
    
    while True:
        print("\nPilih aksi:")
        print("1. Buat backup lengkap")
        print("2. Backup pre-migration")
        print("3. Backup pre-deployment")
        print("4. List backup yang ada")
        print("5. Restore backup")
        print("6. Exit")
        
        choice = input("\nPilihan (1-6): ").strip()
        
        if choice == "1":
            reason = input("Alasan backup (opsional): ").strip() or "Manual backup"
            success, backup_name = backup_manager.create_full_backup("manual", reason)
            if success:
                print(f"✅ Backup berhasil: {backup_name}")
            else:
                print("❌ Backup gagal")
                
        elif choice == "2":
            migration_name = input("Nama migrasi: ").strip()
            if migration_name:
                success, backup_name = backup_manager.pre_migration_backup(migration_name)
                if success:
                    print(f"✅ Pre-migration backup berhasil: {backup_name}")
                else:
                    print("❌ Pre-migration backup gagal")
                    
        elif choice == "3":
            version = input("Versi deployment: ").strip()
            if version:
                success, backup_name = backup_manager.pre_deployment_backup(version)
                if success:
                    print(f"✅ Pre-deployment backup berhasil: {backup_name}")
                else:
                    print("❌ Pre-deployment backup gagal")
                    
        elif choice == "4":
            backups = backup_manager.list_backups()
            if backups:
                print("\n📋 Backup yang tersedia:")
                print("-" * 60)
                for i, backup in enumerate(backups, 1):
                    size_mb = backup["size"] / (1024*1024)
                    print(f"{i}. {backup['file']}")
                    print(f"   Type: {backup['type']}")
                    print(f"   Date: {backup['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}")
                    print(f"   Size: {size_mb:.1f} MB")
                    print(f"   Age: {backup['age_days']} days")
                    print()
            else:
                print("📭 Tidak ada backup tersedia")
                
        elif choice == "5":
            backups = backup_manager.list_backups()
            if backups:
                print("\n📋 Backup yang tersedia:")
                for i, backup in enumerate(backups, 1):
                    print(f"{i}. {backup['file']}")
                    
                try:
                    idx = int(input("\nPilih backup untuk restore (nomor): ")) - 1
                    if 0 <= idx < len(backups):
                        backup_name = backups[idx]["file"].replace(".zip", "")
                        target = input("Target directory (default: current): ").strip() or "."
                        
                        if backup_manager.restore_backup(backup_name, target):
                            print("✅ Restore berhasil")
                        else:
                            print("❌ Restore gagal")
                    else:
                        print("❌ Pilihan tidak valid")
                except ValueError:
                    print("❌ Input tidak valid")
            else:
                print("📭 Tidak ada backup untuk di-restore")
                
        elif choice == "6":
            print("👋 Goodbye!")
            break
            
        else:
            print("❌ Pilihan tidak valid")

if __name__ == "__main__":
    main()
