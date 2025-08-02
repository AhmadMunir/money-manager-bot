#!/usr/bin/env python3
"""
MonMan Bot - Windows GUI Launcher
GUI interface untuk start/stop bot dengan monitoring log
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import subprocess
import threading
import os
import sys
import json
import logging
from datetime import datetime
import queue
import time

class BotGUILauncher:
    def __init__(self, root):
        self.root = root
        self.root.title("MonMan Bot Launcher")
        self.root.geometry("800x600")
        self.root.resizable(True, True)
        
        # Bot process
        self.bot_process = None
        self.is_running = False
        self.log_queue = queue.Queue()
        
        # Config
        self.config_file = "config/launcher_config.json"
        self.load_config()
        
        self.setup_gui()
        self.setup_logging()
        
        # Start log monitoring thread
        self.log_thread = threading.Thread(target=self.monitor_logs, daemon=True)
        self.log_thread.start()
        
        # Check bot status on startup
        self.check_bot_status()
    
    def load_config(self):
        """Load launcher configuration"""
        default_config = {
            "log_level": "INFO",
            "auto_scroll": True,
            "max_log_lines": 1000,
            "bot_script": "main.py",
            "log_file": "logs/bot.log"
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
            print(f"Error loading config: {e}")
    
    def save_config(self):
        """Save launcher configuration"""
        try:
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            print(f"Error saving config: {e}")
    
    def setup_gui(self):
        """Setup GUI components"""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="MonMan Finance Bot Launcher", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # Control Panel
        control_frame = ttk.LabelFrame(main_frame, text="Bot Control", padding="10")
        control_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        control_frame.columnconfigure(2, weight=1)
        
        # Status
        ttk.Label(control_frame, text="Status:").grid(row=0, column=0, sticky=tk.W)
        self.status_label = ttk.Label(control_frame, text="Stopped", foreground="red")
        self.status_label.grid(row=0, column=1, sticky=tk.W, padx=(5, 20))
        
        # Buttons
        self.start_btn = ttk.Button(control_frame, text="▶ Start Bot", 
                                   command=self.start_bot, style="Accent.TButton")
        self.start_btn.grid(row=0, column=2, padx=5)
        
        self.stop_btn = ttk.Button(control_frame, text="⏹ Stop Bot", 
                                  command=self.stop_bot, state="disabled")
        self.stop_btn.grid(row=0, column=3, padx=5)
        
        self.restart_btn = ttk.Button(control_frame, text="🔄 Restart", 
                                     command=self.restart_bot, state="disabled")
        self.restart_btn.grid(row=0, column=4, padx=5)
        
        # Log Level Selection
        ttk.Label(control_frame, text="Log Level:").grid(row=1, column=0, sticky=tk.W, pady=(10, 0))
        self.log_level_var = tk.StringVar(value=self.config.get("log_level", "INFO"))
        log_level_combo = ttk.Combobox(control_frame, textvariable=self.log_level_var,
                                      values=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
                                      state="readonly", width=10)
        log_level_combo.grid(row=1, column=1, sticky=tk.W, padx=(5, 20), pady=(10, 0))
        log_level_combo.bind("<<ComboboxSelected>>", self.on_log_level_change)
        
        # Auto-scroll checkbox
        self.auto_scroll_var = tk.BooleanVar(value=self.config.get("auto_scroll", True))
        auto_scroll_cb = ttk.Checkbutton(control_frame, text="Auto Scroll", 
                                        variable=self.auto_scroll_var,
                                        command=self.on_auto_scroll_change)
        auto_scroll_cb.grid(row=1, column=2, sticky=tk.W, pady=(10, 0))
        
        # Clear logs button
        clear_btn = ttk.Button(control_frame, text="🗑 Clear Logs", command=self.clear_logs)
        clear_btn.grid(row=1, column=3, padx=5, pady=(10, 0))
        
        # Save logs button
        save_btn = ttk.Button(control_frame, text="💾 Save Logs", command=self.save_logs)
        save_btn.grid(row=1, column=4, padx=5, pady=(10, 0))
        
        # Log Display
        log_frame = ttk.LabelFrame(main_frame, text="Bot Logs", padding="5")
        log_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S))
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        
        # Log text area with scrollbar
        self.log_text = scrolledtext.ScrolledText(log_frame, wrap=tk.WORD, 
                                                 font=("Consolas", 10))
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure text tags for different log levels
        self.log_text.tag_config("INFO", foreground="black")
        self.log_text.tag_config("DEBUG", foreground="gray")
        self.log_text.tag_config("WARNING", foreground="orange")
        self.log_text.tag_config("ERROR", foreground="red")
        self.log_text.tag_config("CRITICAL", foreground="red", background="yellow")
        
        # Status bar
        status_frame = ttk.Frame(main_frame)
        status_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 0))
        status_frame.columnconfigure(1, weight=1)
        
        self.status_bar = ttk.Label(status_frame, text="Ready", relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E))
        
        # Process log queue periodically
        self.root.after(100, self.process_log_queue)
    
    def setup_logging(self):
        """Setup logging configuration"""
        logging.basicConfig(
            level=getattr(logging, self.config.get("log_level", "INFO")),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(),
                logging.FileHandler('logs/launcher.log')
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def check_bot_status(self):
        """Check if bot is already running"""
        try:
            # Check for running python processes with main.py
            result = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq python.exe'], 
                                  capture_output=True, text=True)
            if 'python.exe' in result.stdout:
                # More specific check needed here
                pass
        except Exception as e:
            self.logger.debug(f"Error checking bot status: {e}")
    
    def start_bot(self):
        """Start the bot process"""
        if self.is_running:
            messagebox.showwarning("Warning", "Bot is already running!")
            return
        
        try:
            self.log_message("INFO", "Starting MonMan Bot...")
            self.status_bar.config(text="Starting bot...")
            
            # Start bot process
            self.bot_process = subprocess.Popen(
                [sys.executable, self.config.get("bot_script", "main.py")],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1
            )
            
            self.is_running = True
            self.update_ui_state()
            
            # Start output monitoring thread
            self.output_thread = threading.Thread(
                target=self.monitor_bot_output, 
                daemon=True
            )
            self.output_thread.start()
            
            self.log_message("INFO", "Bot started successfully!")
            self.status_bar.config(text="Bot is running")
            
        except Exception as e:
            self.log_message("ERROR", f"Failed to start bot: {e}")
            messagebox.showerror("Error", f"Failed to start bot: {e}")
            self.status_bar.config(text="Failed to start")
    
    def stop_bot(self):
        """Stop the bot process"""
        if not self.is_running or not self.bot_process:
            messagebox.showwarning("Warning", "Bot is not running!")
            return
        
        try:
            self.log_message("INFO", "Stopping MonMan Bot...")
            self.status_bar.config(text="Stopping bot...")
            
            # Terminate bot process
            self.bot_process.terminate()
            
            # Wait for process to end
            try:
                self.bot_process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                self.log_message("WARNING", "Bot didn't stop gracefully, forcing...")
                self.bot_process.kill()
                self.bot_process.wait()
            
            self.is_running = False
            self.bot_process = None
            self.update_ui_state()
            
            self.log_message("INFO", "Bot stopped successfully!")
            self.status_bar.config(text="Bot stopped")
            
        except Exception as e:
            self.log_message("ERROR", f"Error stopping bot: {e}")
            messagebox.showerror("Error", f"Error stopping bot: {e}")
    
    def restart_bot(self):
        """Restart the bot"""
        self.log_message("INFO", "Restarting MonMan Bot...")
        self.stop_bot()
        time.sleep(2)  # Wait a bit
        self.start_bot()
    
    def monitor_bot_output(self):
        """Monitor bot output in separate thread"""
        if not self.bot_process:
            return
        
        for line in iter(self.bot_process.stdout.readline, ''):
            if line:
                # Parse log level from line if possible
                log_level = "INFO"
                if " - ERROR - " in line:
                    log_level = "ERROR"
                elif " - WARNING - " in line:
                    log_level = "WARNING"
                elif " - DEBUG - " in line:
                    log_level = "DEBUG"
                elif " - CRITICAL - " in line:
                    log_level = "CRITICAL"
                
                self.log_queue.put(("BOT", log_level, line.strip()))
        
        # Process ended
        if self.is_running:
            self.log_queue.put(("SYSTEM", "WARNING", "Bot process ended unexpectedly"))
            self.is_running = False
            self.bot_process = None
            self.root.after(0, self.update_ui_state)
    
    def monitor_logs(self):
        """Monitor log files for changes"""
        log_file = self.config.get("log_file", "logs/bot.log")
        if not os.path.exists(log_file):
            return
        
        try:
            with open(log_file, 'r') as f:
                f.seek(0, 2)  # Go to end of file
                while True:
                    line = f.readline()
                    if line:
                        log_level = "INFO"
                        if " - ERROR - " in line:
                            log_level = "ERROR"
                        elif " - WARNING - " in line:
                            log_level = "WARNING"
                        elif " - DEBUG - " in line:
                            log_level = "DEBUG"
                        
                        self.log_queue.put(("FILE", log_level, line.strip()))
                    else:
                        time.sleep(0.1)
        except Exception as e:
            self.log_queue.put(("SYSTEM", "ERROR", f"Error monitoring logs: {e}"))
    
    def process_log_queue(self):
        """Process log messages from queue"""
        try:
            while True:
                source, level, message = self.log_queue.get_nowait()
                self.display_log_message(source, level, message)
        except queue.Empty:
            pass
        finally:
            self.root.after(100, self.process_log_queue)
    
    def log_message(self, level, message):
        """Add log message to display"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.log_queue.put(("LAUNCHER", level, f"[{timestamp}] {message}"))
    
    def display_log_message(self, source, level, message):
        """Display log message in text widget"""
        # Check log level filter
        current_level = self.log_level_var.get()
        level_priority = {"DEBUG": 0, "INFO": 1, "WARNING": 2, "ERROR": 3, "CRITICAL": 4}
        
        if level_priority.get(level, 1) < level_priority.get(current_level, 1):
            return
        
        # Add timestamp if not present
        if not message.startswith('['):
            timestamp = datetime.now().strftime("%H:%M:%S")
            message = f"[{timestamp}] {message}"
        
        # Add source prefix
        prefix = f"[{source}] " if source != "BOT" else ""
        full_message = f"{prefix}{message}\n"
        
        # Insert message
        self.log_text.insert(tk.END, full_message, level)
        
        # Limit number of lines
        max_lines = self.config.get("max_log_lines", 1000)
        lines = int(self.log_text.index('end-1c').split('.')[0])
        if lines > max_lines:
            self.log_text.delete('1.0', f'{lines - max_lines}.0')
        
        # Auto-scroll if enabled
        if self.auto_scroll_var.get():
            self.log_text.see(tk.END)
    
    def update_ui_state(self):
        """Update UI based on bot running state"""
        if self.is_running:
            self.status_label.config(text="Running", foreground="green")
            self.start_btn.config(state="disabled")
            self.stop_btn.config(state="normal")
            self.restart_btn.config(state="normal")
        else:
            self.status_label.config(text="Stopped", foreground="red")
            self.start_btn.config(state="normal")
            self.stop_btn.config(state="disabled")
            self.restart_btn.config(state="disabled")
    
    def on_log_level_change(self, event=None):
        """Handle log level change"""
        self.config["log_level"] = self.log_level_var.get()
        self.save_config()
        self.log_message("INFO", f"Log level changed to: {self.log_level_var.get()}")
    
    def on_auto_scroll_change(self):
        """Handle auto-scroll change"""
        self.config["auto_scroll"] = self.auto_scroll_var.get()
        self.save_config()
    
    def clear_logs(self):
        """Clear log display"""
        self.log_text.delete('1.0', tk.END)
        self.log_message("INFO", "Log display cleared")
    
    def save_logs(self):
        """Save logs to file"""
        try:
            filename = filedialog.asksaveasfilename(
                defaultextension=".log",
                filetypes=[("Log files", "*.log"), ("Text files", "*.txt"), ("All files", "*.*")],
                title="Save Logs"
            )
            
            if filename:
                with open(filename, 'w') as f:
                    f.write(self.log_text.get('1.0', tk.END))
                self.log_message("INFO", f"Logs saved to: {filename}")
                messagebox.showinfo("Success", f"Logs saved to:\n{filename}")
                
        except Exception as e:
            self.log_message("ERROR", f"Error saving logs: {e}")
            messagebox.showerror("Error", f"Error saving logs: {e}")
    
    def on_closing(self):
        """Handle window closing"""
        if self.is_running:
            if messagebox.askquestion("Confirm", "Bot is still running. Stop it before closing?") == 'yes':
                self.stop_bot()
                time.sleep(1)
        
        self.save_config()
        self.root.quit()

def main():
    """Main function"""
    # Ensure logs directory exists
    os.makedirs("logs", exist_ok=True)
    os.makedirs("config", exist_ok=True)
    
    root = tk.Tk()
    app = BotGUILauncher(root)
    
    # Handle window closing
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    
    # Set window icon if available
    try:
        root.iconbitmap("assets/icon.ico")
    except:
        pass
    
    root.mainloop()

if __name__ == "__main__":
    main()
