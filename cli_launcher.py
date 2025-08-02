#!/usr/bin/env python3
"""
MonMan Bot - Linux CLI Launcher
Command-line interface untuk start/stop bot dengan monitoring log
"""

import os
import sys
import time
import json
import signal
import subprocess
import threading
import argparse
import logging
from datetime import datetime
from pathlib import Path

class Colors:
    """ANSI color codes for terminal output"""
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'

class BotCLILauncher:
    def __init__(self):
        self.bot_process = None
        self.is_running = False
        self.config_file = "config/launcher_config.json"
        self.pid_file = "/tmp/monman_bot.pid"
        
        # Setup
        self.load_config()
        self.setup_logging()
        self.setup_signal_handlers()
    
    def load_config(self):
        """Load launcher configuration"""
        default_config = {
            "log_level": "INFO",
            "bot_script": "main.py",
            "log_file": "logs/bot.log",
            "max_log_lines": 100,
            "auto_restart": False,
            "restart_delay": 5
        }
        
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    self.config = json.load(f)
            else:
                self.config = default_config
                self.save_config()
        except Exception as e:
            self.config = default_config
            self.print_error(f"Error loading config: {e}")
    
    def save_config(self):
        """Save launcher configuration"""
        try:
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            self.print_error(f"Error saving config: {e}")
    
    def setup_logging(self):
        """Setup logging configuration"""
        log_level = getattr(logging, self.config.get("log_level", "INFO"))
        
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(),
                logging.FileHandler('logs/launcher.log')
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown"""
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
    
    def signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        self.print_info(f"\nReceived signal {signum}, shutting down...")
        self.stop_bot()
        sys.exit(0)
    
    def print_header(self):
        """Print application header"""
        print(f"\n{Colors.CYAN}{Colors.BOLD}╔═══════════════════════════════════════╗{Colors.END}")
        print(f"{Colors.CYAN}{Colors.BOLD}║        MonMan Finance Bot CLI         ║{Colors.END}")
        print(f"{Colors.CYAN}{Colors.BOLD}║           Control Interface           ║{Colors.END}")
        print(f"{Colors.CYAN}{Colors.BOLD}╚═══════════════════════════════════════╝{Colors.END}\n")
    
    def print_info(self, message):
        """Print info message"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"{Colors.BLUE}[{timestamp}] INFO:{Colors.END} {message}")
    
    def print_success(self, message):
        """Print success message"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"{Colors.GREEN}[{timestamp}] SUCCESS:{Colors.END} {message}")
    
    def print_warning(self, message):
        """Print warning message"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"{Colors.YELLOW}[{timestamp}] WARNING:{Colors.END} {message}")
    
    def print_error(self, message):
        """Print error message"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"{Colors.RED}[{timestamp}] ERROR:{Colors.END} {message}")
    
    def check_bot_status(self):
        """Check if bot is running"""
        try:
            if os.path.exists(self.pid_file):
                with open(self.pid_file, 'r') as f:
                    pid = int(f.read().strip())
                
                # Check if process exists
                try:
                    os.kill(pid, 0)
                    return True, pid
                except OSError:
                    # Process doesn't exist, remove stale PID file
                    os.remove(self.pid_file)
                    return False, None
            return False, None
        except Exception as e:
            self.print_error(f"Error checking bot status: {e}")
            return False, None
    
    def start_bot(self, daemon=False):
        """Start the bot"""
        is_running, pid = self.check_bot_status()
        if is_running:
            self.print_warning(f"Bot is already running (PID: {pid})")
            return False
        
        try:
            self.print_info("Starting MonMan Bot...")
            
            bot_script = self.config.get("bot_script", "main.py")
            if not os.path.exists(bot_script):
                self.print_error(f"Bot script not found: {bot_script}")
                return False
            
            if daemon:
                # Start as daemon
                self.bot_process = subprocess.Popen(
                    [sys.executable, bot_script],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    preexec_fn=os.setsid
                )
            else:
                # Start with output
                self.bot_process = subprocess.Popen(
                    [sys.executable, bot_script],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    universal_newlines=True,
                    bufsize=1
                )
            
            # Save PID
            with open(self.pid_file, 'w') as f:
                f.write(str(self.bot_process.pid))
            
            self.is_running = True
            self.print_success(f"Bot started successfully (PID: {self.bot_process.pid})")
            
            if not daemon:
                # Monitor output
                self.monitor_output()
            
            return True
            
        except Exception as e:
            self.print_error(f"Failed to start bot: {e}")
            return False
    
    def stop_bot(self):
        """Stop the bot"""
        is_running, pid = self.check_bot_status()
        if not is_running:
            self.print_warning("Bot is not running")
            return False
        
        try:
            self.print_info(f"Stopping bot (PID: {pid})...")
            
            # Send SIGTERM
            os.kill(pid, signal.SIGTERM)
            
            # Wait for graceful shutdown
            for i in range(10):
                try:
                    os.kill(pid, 0)
                    time.sleep(1)
                except OSError:
                    break
            else:
                # Force kill if still running
                self.print_warning("Bot didn't stop gracefully, forcing...")
                os.kill(pid, signal.SIGKILL)
            
            # Remove PID file
            if os.path.exists(self.pid_file):
                os.remove(self.pid_file)
            
            self.is_running = False
            self.bot_process = None
            self.print_success("Bot stopped successfully")
            return True
            
        except Exception as e:
            self.print_error(f"Error stopping bot: {e}")
            return False
    
    def restart_bot(self, daemon=False):
        """Restart the bot"""
        self.print_info("Restarting bot...")
        
        if self.stop_bot():
            time.sleep(2)
            return self.start_bot(daemon)
        return False
    
    def show_status(self):
        """Show bot status"""
        is_running, pid = self.check_bot_status()
        
        print(f"\n{Colors.BOLD}Bot Status:{Colors.END}")
        print("─" * 40)
        
        if is_running:
            print(f"Status: {Colors.GREEN}RUNNING{Colors.END}")
            print(f"PID: {pid}")
            
            # Show memory and CPU usage if available
            try:
                import psutil
                process = psutil.Process(pid)
                cpu_percent = process.cpu_percent()
                memory_info = process.memory_info()
                print(f"CPU: {cpu_percent}%")
                print(f"Memory: {memory_info.rss / 1024 / 1024:.1f} MB")
            except ImportError:
                pass
            except Exception as e:
                self.print_warning(f"Could not get process info: {e}")
        else:
            print(f"Status: {Colors.RED}STOPPED{Colors.END}")
        
        print(f"Log Level: {self.config.get('log_level', 'INFO')}")
        print(f"Log File: {self.config.get('log_file', 'logs/bot.log')}")
        print()
    
    def show_logs(self, lines=None, follow=False):
        """Show bot logs"""
        log_file = self.config.get("log_file", "logs/bot.log")
        
        if not os.path.exists(log_file):
            self.print_warning(f"Log file not found: {log_file}")
            return
        
        lines = lines or self.config.get("max_log_lines", 100)
        
        try:
            if follow:
                self.print_info(f"Following logs from {log_file} (Ctrl+C to stop)")
                self.tail_logs(log_file)
            else:
                self.print_info(f"Showing last {lines} lines from {log_file}")
                subprocess.run(['tail', '-n', str(lines), log_file])
        except Exception as e:
            self.print_error(f"Error showing logs: {e}")
    
    def tail_logs(self, log_file):
        """Follow log file (like tail -f)"""
        try:
            process = subprocess.Popen(['tail', '-f', log_file], 
                                     stdout=subprocess.PIPE, 
                                     universal_newlines=True)
            
            for line in iter(process.stdout.readline, ''):
                # Color code log levels
                line = line.strip()
                if ' - ERROR - ' in line:
                    print(f"{Colors.RED}{line}{Colors.END}")
                elif ' - WARNING - ' in line:
                    print(f"{Colors.YELLOW}{line}{Colors.END}")
                elif ' - INFO - ' in line:
                    print(f"{Colors.BLUE}{line}{Colors.END}")
                elif ' - DEBUG - ' in line:
                    print(f"{Colors.MAGENTA}{line}{Colors.END}")
                else:
                    print(line)
        except KeyboardInterrupt:
            process.terminate()
            self.print_info("Log following stopped")
    
    def monitor_output(self):
        """Monitor bot output in real-time"""
        if not self.bot_process:
            return
        
        self.print_info("Monitoring bot output (Ctrl+C to stop)")
        print("─" * 50)
        
        try:
            for line in iter(self.bot_process.stdout.readline, ''):
                if line:
                    line = line.strip()
                    # Color code based on content
                    if 'ERROR' in line:
                        print(f"{Colors.RED}{line}{Colors.END}")
                    elif 'WARNING' in line:
                        print(f"{Colors.YELLOW}{line}{Colors.END}")
                    elif 'INFO' in line:
                        print(f"{Colors.BLUE}{line}{Colors.END}")
                    else:
                        print(line)
        except KeyboardInterrupt:
            self.print_info("Output monitoring stopped")
        finally:
            if self.bot_process and self.bot_process.poll() is None:
                self.print_warning("Bot process ended unexpectedly")
                self.is_running = False
    
    def configure(self):
        """Interactive configuration"""
        print(f"\n{Colors.BOLD}Configuration:{Colors.END}")
        print("─" * 40)
        
        # Log level
        current_level = self.config.get("log_level", "INFO")
        print(f"Current log level: {current_level}")
        new_level = input("New log level [DEBUG/INFO/WARNING/ERROR/CRITICAL] (Enter to keep current): ").upper()
        if new_level in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]:
            self.config["log_level"] = new_level
        
        # Bot script
        current_script = self.config.get("bot_script", "main.py")
        print(f"Current bot script: {current_script}")
        new_script = input("New bot script path (Enter to keep current): ")
        if new_script.strip():
            self.config["bot_script"] = new_script.strip()
        
        # Auto restart
        current_auto = self.config.get("auto_restart", False)
        print(f"Auto restart: {current_auto}")
        auto_input = input("Enable auto restart? [y/N]: ").lower()
        self.config["auto_restart"] = auto_input in ['y', 'yes']
        
        # Save configuration
        self.save_config()
        self.print_success("Configuration saved!")
    
    def interactive_menu(self):
        """Interactive menu"""
        while True:
            self.print_header()
            self.show_status()
            
            print(f"{Colors.BOLD}Available Commands:{Colors.END}")
            print("1. Start Bot")
            print("2. Stop Bot") 
            print("3. Restart Bot")
            print("4. Start Bot (Daemon)")
            print("5. Show Logs")
            print("6. Follow Logs")
            print("7. Configure")
            print("8. Exit")
            print()
            
            try:
                choice = input(f"{Colors.CYAN}Select option [1-8]:{Colors.END} ").strip()
                
                if choice == '1':
                    self.start_bot(daemon=False)
                elif choice == '2':
                    self.stop_bot()
                elif choice == '3':
                    self.restart_bot(daemon=False)
                elif choice == '4':
                    self.start_bot(daemon=True)
                elif choice == '5':
                    lines = input("Number of lines to show (default 100): ").strip()
                    lines = int(lines) if lines.isdigit() else 100
                    self.show_logs(lines=lines)
                elif choice == '6':
                    self.show_logs(follow=True)
                elif choice == '7':
                    self.configure()
                elif choice == '8':
                    break
                else:
                    self.print_error("Invalid option")
                
                if choice not in ['6', '8']:
                    input(f"\n{Colors.CYAN}Press Enter to continue...{Colors.END}")
                    
            except KeyboardInterrupt:
                print(f"\n{Colors.YELLOW}Operation cancelled{Colors.END}")
                time.sleep(1)
            except Exception as e:
                self.print_error(f"Error: {e}")
                time.sleep(2)

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="MonMan Bot CLI Launcher")
    parser.add_argument('command', nargs='?', choices=['start', 'stop', 'restart', 'status', 'logs', 'config', 'menu'],
                       help='Command to execute')
    parser.add_argument('-d', '--daemon', action='store_true', help='Run bot as daemon')
    parser.add_argument('-f', '--follow', action='store_true', help='Follow logs (with logs command)')
    parser.add_argument('-n', '--lines', type=int, default=100, help='Number of log lines to show')
    parser.add_argument('--log-level', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
                       help='Set log level')
    
    args = parser.parse_args()
    
    # Ensure required directories exist
    os.makedirs("logs", exist_ok=True)
    os.makedirs("config", exist_ok=True)
    
    launcher = BotCLILauncher()
    
    # Override log level if specified
    if args.log_level:
        launcher.config["log_level"] = args.log_level
        launcher.save_config()
        launcher.setup_logging()
    
    if not args.command:
        # No command specified, show interactive menu
        launcher.interactive_menu()
    elif args.command == 'start':
        launcher.start_bot(daemon=args.daemon)
    elif args.command == 'stop':
        launcher.stop_bot()
    elif args.command == 'restart':
        launcher.restart_bot(daemon=args.daemon)
    elif args.command == 'status':
        launcher.show_status()
    elif args.command == 'logs':
        launcher.show_logs(lines=args.lines, follow=args.follow)
    elif args.command == 'config':
        launcher.configure()
    elif args.command == 'menu':
        launcher.interactive_menu()

if __name__ == "__main__":
    main()
