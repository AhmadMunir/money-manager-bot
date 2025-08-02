#!/usr/bin/env python3
"""
Backup Monitoring & Health Check System
Monitor kesehatan sistem backup dan alert jika ada masalah
"""
import os
import json
import sqlite3
import logging
from datetime import datetime, timedelta
from pathlib import Path
from scripts.backup_system import BackupManager

logger = logging.getLogger(__name__)

class BackupMonitor:
    def __init__(self):
        self.backup_manager = BackupManager()
        self.monitor_config = self.load_monitor_config()
        
    def load_monitor_config(self):
        """Load monitoring configuration"""
        config_path = Path("config/backup_config.json")
        
        if config_path.exists():
            with open(config_path) as f:
                return json.load(f)
        else:
            # Default config
            return {
                "backup_config": {
                    "max_backup_age_days": 1,
                    "min_backups_required": 3,
                    "max_backup_size_mb": 1000,
                    "critical_operations": []
                }
            }
    
    def health_check(self):
        """Comprehensive backup system health check"""
        print("🔍 BACKUP SYSTEM HEALTH CHECK")
        print("=" * 50)
        
        health_report = {
            "timestamp": datetime.now().isoformat(),
            "overall_status": "healthy",
            "checks": {},
            "warnings": [],
            "errors": [],
            "recommendations": []
        }
        
        # Check 1: Backup availability
        print("1. Checking backup availability...")
        backup_check = self.check_backup_availability()
        health_report["checks"]["backup_availability"] = backup_check
        
        if not backup_check["has_recent_backup"]:
            health_report["errors"].append("No recent backup found")
            health_report["overall_status"] = "critical"
        
        # Check 2: Database integrity
        print("2. Checking database integrity...")
        db_check = self.check_database_integrity()
        health_report["checks"]["database_integrity"] = db_check
        
        if not db_check["all_databases_healthy"]:
            health_report["errors"].append("Database integrity issues detected")
            health_report["overall_status"] = "critical"
        
        # Check 3: Storage space
        print("3. Checking storage space...")
        storage_check = self.check_storage_space()
        health_report["checks"]["storage_space"] = storage_check
        
        if storage_check["disk_usage_percent"] > 90:
            health_report["warnings"].append("Low disk space")
            if health_report["overall_status"] == "healthy":
                health_report["overall_status"] = "warning"
        
        # Check 4: Backup file integrity
        print("4. Checking backup file integrity...")
        integrity_check = self.check_backup_file_integrity()
        health_report["checks"]["backup_integrity"] = integrity_check
        
        if integrity_check["corrupted_backups"]:
            health_report["warnings"].append(f"Found {len(integrity_check['corrupted_backups'])} corrupted backups")
            if health_report["overall_status"] == "healthy":
                health_report["overall_status"] = "warning"
        
        # Generate recommendations
        health_report["recommendations"] = self.generate_recommendations(health_report)
        
        # Save health report
        report_file = Path("backups") / f"health_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(health_report, f, indent=2)
        
        # Display summary
        self.display_health_summary(health_report)
        
        return health_report
    
    def check_backup_availability(self):
        """Check if recent backups are available"""
        backups = self.backup_manager.list_backups()
        
        if not backups:
            return {
                "has_backups": False,
                "has_recent_backup": False,
                "latest_backup_age_days": None,
                "total_backups": 0
            }
        
        latest_backup = backups[0]  # Most recent
        age_days = latest_backup["age_days"]
        max_age = self.monitor_config["backup_config"].get("max_backup_age_days", 1)
        
        return {
            "has_backups": True,
            "has_recent_backup": age_days <= max_age,
            "latest_backup_age_days": age_days,
            "total_backups": len(backups),
            "latest_backup": latest_backup["file"]
        }
    
    def check_database_integrity(self):
        """Check integrity of all databases"""
        databases = ["finance_bot.db", "monman.db"]
        results = {}
        all_healthy = True
        
        for db_name in databases:
            if Path(db_name).exists():
                is_healthy = self.backup_manager.validate_database(db_name)
                results[db_name] = {
                    "exists": True,
                    "healthy": is_healthy,
                    "size_mb": Path(db_name).stat().st_size / (1024*1024)
                }
                if not is_healthy:
                    all_healthy = False
            else:
                results[db_name] = {
                    "exists": False,
                    "healthy": False,
                    "size_mb": 0
                }
                all_healthy = False
        
        return {
            "all_databases_healthy": all_healthy,
            "databases": results
        }
    
    def check_storage_space(self):
        """Check available storage space"""
        try:
            # Get disk usage for current directory
            statvfs = os.statvfs('.')
            total_space = statvfs.f_frsize * statvfs.f_blocks
            available_space = statvfs.f_frsize * statvfs.f_available
            used_space = total_space - available_space
            usage_percent = (used_space / total_space) * 100
            
            return {
                "total_space_gb": total_space / (1024**3),
                "available_space_gb": available_space / (1024**3),
                "used_space_gb": used_space / (1024**3),
                "disk_usage_percent": usage_percent
            }
        except:
            # Fallback for Windows
            import shutil
            total, used, free = shutil.disk_usage('.')
            usage_percent = (used / total) * 100
            
            return {
                "total_space_gb": total / (1024**3),
                "available_space_gb": free / (1024**3),
                "used_space_gb": used / (1024**3),
                "disk_usage_percent": usage_percent
            }
    
    def check_backup_file_integrity(self):
        """Check integrity of backup files"""
        backups = self.backup_manager.list_backups()
        corrupted_backups = []
        healthy_backups = []
        
        for backup in backups:
            backup_path = Path("backups") / backup["file"]
            
            try:
                # Basic checks
                if backup_path.stat().st_size < 1024:  # Too small
                    corrupted_backups.append({
                        "file": backup["file"],
                        "issue": "File too small"
                    })
                elif backup["file"].endswith('.zip'):
                    # Try to read zip file
                    import zipfile
                    with zipfile.ZipFile(backup_path, 'r') as zf:
                        # Test zip integrity
                        bad_file = zf.testzip()
                        if bad_file:
                            corrupted_backups.append({
                                "file": backup["file"],
                                "issue": f"Corrupted archive: {bad_file}"
                            })
                        else:
                            healthy_backups.append(backup["file"])
                else:
                    healthy_backups.append(backup["file"])
                    
            except Exception as e:
                corrupted_backups.append({
                    "file": backup["file"],
                    "issue": str(e)
                })
        
        return {
            "total_backups": len(backups),
            "healthy_backups": healthy_backups,
            "corrupted_backups": corrupted_backups,
            "integrity_score": len(healthy_backups) / len(backups) if backups else 0
        }
    
    def generate_recommendations(self, health_report):
        """Generate recommendations based on health check"""
        recommendations = []
        
        # Backup recommendations
        if not health_report["checks"]["backup_availability"]["has_recent_backup"]:
            recommendations.append({
                "priority": "high",
                "category": "backup",
                "message": "Create immediate backup - no recent backup found",
                "action": "Run: python scripts/backup_system.py"
            })
        
        backup_count = health_report["checks"]["backup_availability"]["total_backups"]
        min_required = self.monitor_config["backup_config"].get("min_backups_required", 3)
        
        if backup_count < min_required:
            recommendations.append({
                "priority": "medium",
                "category": "backup",
                "message": f"Increase backup frequency - only {backup_count} backups available",
                "action": "Schedule more frequent backups"
            })
        
        # Database recommendations
        if not health_report["checks"]["database_integrity"]["all_databases_healthy"]:
            recommendations.append({
                "priority": "critical",
                "category": "database",
                "message": "Database corruption detected - immediate attention required",
                "action": "Run database repair or restore from backup"
            })
        
        # Storage recommendations
        usage_percent = health_report["checks"]["storage_space"]["disk_usage_percent"]
        if usage_percent > 90:
            recommendations.append({
                "priority": "high",
                "category": "storage",
                "message": f"Disk space critical ({usage_percent:.1f}% used)",
                "action": "Clean up old backups or expand storage"
            })
        elif usage_percent > 80:
            recommendations.append({
                "priority": "medium",
                "category": "storage",
                "message": f"Disk space warning ({usage_percent:.1f}% used)",
                "action": "Monitor disk usage and plan cleanup"
            })
        
        # Backup integrity recommendations
        corrupted_count = len(health_report["checks"]["backup_integrity"]["corrupted_backups"])
        if corrupted_count > 0:
            recommendations.append({
                "priority": "medium",
                "category": "backup",
                "message": f"Remove {corrupted_count} corrupted backup files",
                "action": "Clean up corrupted backups and verify backup process"
            })
        
        return recommendations
    
    def display_health_summary(self, health_report):
        """Display health check summary"""
        status = health_report["overall_status"]
        
        # Status indicator
        if status == "healthy":
            print("\n✅ OVERALL STATUS: HEALTHY")
        elif status == "warning":
            print("\n⚠️ OVERALL STATUS: WARNING")
        elif status == "critical":
            print("\n❌ OVERALL STATUS: CRITICAL")
        
        print("-" * 30)
        
        # Key metrics
        backup_check = health_report["checks"]["backup_availability"]
        if backup_check["has_backups"]:
            print(f"📂 Total Backups: {backup_check['total_backups']}")
            print(f"📅 Latest Backup: {backup_check['latest_backup_age_days']:.1f} days ago")
        else:
            print("📂 No backups found!")
        
        # Database status
        db_check = health_report["checks"]["database_integrity"]
        healthy_dbs = sum(1 for db in db_check["databases"].values() if db["healthy"])
        total_dbs = len(db_check["databases"])
        print(f"💾 Database Health: {healthy_dbs}/{total_dbs} healthy")
        
        # Storage status
        storage = health_report["checks"]["storage_space"]
        print(f"💿 Disk Usage: {storage['disk_usage_percent']:.1f}%")
        
        # Errors and warnings
        if health_report["errors"]:
            print("\n❌ ERRORS:")
            for error in health_report["errors"]:
                print(f"  - {error}")
        
        if health_report["warnings"]:
            print("\n⚠️ WARNINGS:")
            for warning in health_report["warnings"]:
                print(f"  - {warning}")
        
        # Top recommendations
        if health_report["recommendations"]:
            print("\n💡 TOP RECOMMENDATIONS:")
            high_priority = [r for r in health_report["recommendations"] if r["priority"] in ["critical", "high"]]
            for rec in high_priority[:3]:  # Show top 3
                print(f"  - [{rec['priority'].upper()}] {rec['message']}")
    
    def automated_monitoring(self):
        """Run automated monitoring and alerting"""
        print("🤖 Running automated backup monitoring...")
        
        health_report = self.health_check()
        
        # Check if alerts should be sent
        alerts_needed = []
        
        if health_report["overall_status"] == "critical":
            alerts_needed.append("CRITICAL: Backup system needs immediate attention")
        
        if not health_report["checks"]["backup_availability"]["has_recent_backup"]:
            alerts_needed.append("WARNING: No recent backup found")
        
        # Log alerts
        if alerts_needed:
            logger.critical("BACKUP SYSTEM ALERTS:")
            for alert in alerts_needed:
                logger.critical(f"  - {alert}")
        else:
            logger.info("Backup system monitoring: All checks passed")
        
        return health_report

def main():
    """Main monitoring interface"""
    monitor = BackupMonitor()
    
    print("🔍 Backup Monitoring System")
    print("=" * 40)
    
    while True:
        print("\nPilih monitoring action:")
        print("1. Run health check")
        print("2. Automated monitoring")
        print("3. View backup status")
        print("4. Check database integrity")
        print("5. Exit")
        
        choice = input("\nPilihan (1-5): ").strip()
        
        if choice == "1":
            monitor.health_check()
            
        elif choice == "2":
            monitor.automated_monitoring()
            
        elif choice == "3":
            backups = monitor.backup_manager.list_backups()
            if backups:
                print("\n📋 Backup Status:")
                for backup in backups[:5]:  # Show recent 5
                    print(f"  - {backup['file']} ({backup['age_days']:.1f} days old)")
            else:
                print("📭 No backups found")
                
        elif choice == "4":
            db_check = monitor.check_database_integrity()
            print("\n💾 Database Integrity:")
            for db_name, status in db_check["databases"].items():
                health_icon = "✅" if status["healthy"] else "❌"
                print(f"  - {db_name}: {health_icon} {'Healthy' if status['healthy'] else 'Issues detected'}")
                
        elif choice == "5":
            print("👋 Goodbye!")
            break
            
        else:
            print("❌ Pilihan tidak valid")

if __name__ == "__main__":
    main()
