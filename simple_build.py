#!/usr/bin/env python3
"""
Simple build script for MonMan Bot GUI executable
"""

import os
import sys
import subprocess
from pathlib import Path

def build_gui():
    """Build GUI executable with PyInstaller"""
    print("🔨 Building MonMan Bot GUI...")
    
    # Ensure directories exist
    os.makedirs("assets", exist_ok=True)
    os.makedirs("config", exist_ok=True)
    os.makedirs("logs", exist_ok=True)
    
    # Create icon if not exists
    icon_path = Path("assets/icon.ico")
    if not icon_path.exists():
        print("Creating placeholder icon...")
        with open(icon_path, "wb") as f:
            # Minimal ICO header
            f.write(b'\x00\x00\x01\x00\x01\x00\x10\x10\x00\x00\x01\x00\x08\x00\x68\x05\x00\x00\x16\x00\x00\x00')
            f.write(b'\x00' * 1384)
    
    # PyInstaller command
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",
        "--windowed",
        "--name=MonManBot-GUI",
        f"--icon={icon_path}",
        "--add-data=config;config",
        "--add-data=logs;logs", 
        "--add-data=assets;assets",
        "--clean",
        "--noconfirm",
        "gui_launcher.py"
    ]
    
    print(f"Running: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, check=True)
        print("✅ GUI executable built successfully!")
        print("📁 Check dist/MonManBot-GUI.exe")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Build failed: {e}")
        return False

def build_cli():
    """Build CLI executable with PyInstaller"""
    print("🔨 Building MonMan Bot CLI...")
    
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",
        "--console",
        "--name=MonManBot-CLI",
        "--add-data=config;config",
        "--add-data=logs;logs",
        "--clean",
        "--noconfirm",
        "cli_launcher.py"
    ]
    
    try:
        result = subprocess.run(cmd, check=True)
        print("✅ CLI executable built successfully!")
        print("📁 Check dist/MonManBot-CLI.exe")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Build failed: {e}")
        return False

def main():
    """Main build function"""
    if len(sys.argv) > 1 and sys.argv[1] == "cli":
        build_cli()
    elif len(sys.argv) > 1 and sys.argv[1] == "gui":
        build_gui()
    else:
        print("Building both GUI and CLI...")
        build_gui()
        build_cli()

if __name__ == "__main__":
    main()
