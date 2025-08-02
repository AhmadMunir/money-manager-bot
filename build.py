#!/usr/bin/env python3
"""
Build script for MonMan Bot executables
Creates Windows .exe files and packages for distribution
"""

import os
import sys
import shutil
import subprocess
import json
from pathlib import Path

class BuildSystem:
    def __init__(self):
        self.root_dir = Path(__file__).parent
        self.build_dir = self.root_dir / "build"
        self.dist_dir = self.root_dir / "dist"
        self.spec_dir = self.root_dir / "specs"
        
        # Build configuration
        self.config = {
            "app_name": "MonMan Bot",
            "version": "2.0.0",
            "author": "AhmadMunir",
            "description": "Telegram Finance Bot Manager",
            "icon": "assets/icon.ico",
            "console": False
        }
    
    def setup_build_env(self):
        """Setup build environment"""
        print("🔧 Setting up build environment...")
        
        # Create directories
        self.build_dir.mkdir(exist_ok=True)
        self.dist_dir.mkdir(exist_ok=True)
        self.spec_dir.mkdir(exist_ok=True)
        
        # Create assets directory if not exists
        assets_dir = self.root_dir / "assets"
        assets_dir.mkdir(exist_ok=True)
        
        # Create default icon if not exists
        icon_path = assets_dir / "icon.ico"
        if not icon_path.exists():
            print("ℹ️  Creating default icon...")
            self.create_default_icon(icon_path)
        
        print("✅ Build environment ready")
    
    def create_default_icon(self, icon_path):
        """Create a default icon file"""
        try:
            from PIL import Image, ImageDraw, ImageFont
            
            # Create a simple icon
            size = (64, 64)
            img = Image.new('RGBA', size, (0, 100, 200, 255))
            draw = ImageDraw.Draw(img)
            
            # Draw "MB" text
            try:
                font = ImageFont.truetype("arial.ttf", 24)
            except:
                font = ImageFont.load_default()
            
            text = "MB"
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            
            x = (size[0] - text_width) // 2
            y = (size[1] - text_height) // 2
            draw.text((x, y), text, fill=(255, 255, 255, 255), font=font)
            
            # Save as ICO
            img.save(icon_path, format='ICO', sizes=[(64, 64), (32, 32), (16, 16)])
            print(f"✅ Default icon created at {icon_path}")
            
        except ImportError:
            print("⚠️  Pillow not available, creating placeholder icon")
            # Create a minimal ICO file
            with open(icon_path, 'wb') as f:
                # Minimal ICO header
                f.write(b'\x00\x00\x01\x00\x01\x00\x10\x10\x00\x00\x01\x00\x08\x00\x68\x05\x00\x00\x16\x00\x00\x00')
                f.write(b'\x00' * 1384)  # Placeholder data
    
    def create_gui_spec(self):
        """Create PyInstaller spec for GUI launcher"""
        spec_content = f'''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['gui_launcher.py'],
    pathex=['{self.root_dir.as_posix()}'],
    binaries=[],
    datas=[
        ('config', 'config'),
        ('logs', 'logs'),
        ('assets', 'assets'),
        ('requirements*.txt', '.'),
    ],
    hiddenimports=[
        'tkinter',
        'tkinter.ttk',
        'tkinter.scrolledtext',
        'tkinter.messagebox',
        'tkinter.filedialog',
        'queue',
        'threading',
        'subprocess',
        'json',
        'logging',
        'datetime',
        'os',
        'sys',
        'time'
    ],
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='MonManBot-GUI',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console={str(self.config.get("console", False)).lower()},
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='{self.config.get("icon", "assets/icon.ico")}',
    version_file='version_info.txt'
)
'''
        
        spec_path = self.spec_dir / "gui_launcher.spec"
        with open(spec_path, 'w') as f:
            f.write(spec_content)
        
        print(f"✅ GUI spec created: {spec_path}")
        return spec_path
    
    def create_cli_spec(self):
        """Create PyInstaller spec for CLI launcher"""
        spec_content = f'''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['cli_launcher.py'],
    pathex=['{self.root_dir.as_posix()}'],
    binaries=[],
    datas=[
        ('config', 'config'),
        ('logs', 'logs'),
        ('requirements*.txt', '.'),
    ],
    hiddenimports=[
        'argparse',
        'subprocess',
        'threading',
        'signal',
        'json',
        'logging',
        'datetime',
        'pathlib',
        'os',
        'sys',
        'time'
    ],
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='MonManBot-CLI',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='{self.config.get("icon", "assets/icon.ico")}',
    version_file='version_info.txt'
)
'''
        
        spec_path = self.spec_dir / "cli_launcher.spec"
        with open(spec_path, 'w') as f:
            f.write(spec_content)
        
        print(f"✅ CLI spec created: {spec_path}")
        return spec_path
    
    def create_bot_spec(self):
        """Create PyInstaller spec for main bot"""
        spec_content = f'''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=['{self.root_dir.as_posix()}'],
    binaries=[],
    datas=[
        ('src', 'src'),
        ('config', 'config'),
        ('logs', 'logs'),
        ('migrations', 'migrations'),
        ('scripts', 'scripts'),
        ('requirements.txt', '.'),
        ('.env', '.'),
    ],
    hiddenimports=[
        'telebot',
        'sqlalchemy',
        'sqlite3',
        'dotenv',
        'logging',
        'datetime',
        'os',
        'sys',
        'atexit',
        'signal'
    ],
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='MonManBot',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='{self.config.get("icon", "assets/icon.ico")}',
    version_file='version_info.txt'
)
'''
        
        spec_path = self.spec_dir / "main_bot.spec"
        with open(spec_path, 'w') as f:
            f.write(spec_content)
        
        print(f"✅ Bot spec created: {spec_path}")
        return spec_path
    
    def create_version_info(self):
        """Create version info file for Windows executables"""
        version_info = f'''# UTF-8
#
# For more details about fixed file info 'ffi' see:
# http://msdn.microsoft.com/en-us/library/ms646997.aspx
VSVersionInfo(
  ffi=FixedFileInfo(
    filevers=(2,0,0,0),
    prodvers=(2,0,0,0),
    mask=0x3f,
    flags=0x0,
    OS=0x40004,
    fileType=0x1,
    subtype=0x0,
    date=(0, 0)
    ),
  kids=[
    StringFileInfo(
      [
      StringTable(
        u'040904B0',
        [StringStruct(u'CompanyName', u'{self.config["author"]}'),
        StringStruct(u'FileDescription', u'{self.config["description"]}'),
        StringStruct(u'FileVersion', u'{self.config["version"]}'),
        StringStruct(u'InternalName', u'{self.config["app_name"]}'),
        StringStruct(u'LegalCopyright', u'© 2025 {self.config["author"]}'),
        StringStruct(u'OriginalFilename', u'MonManBot.exe'),
        StringStruct(u'ProductName', u'{self.config["app_name"]}'),
        StringStruct(u'ProductVersion', u'{self.config["version"]}')])
      ]),
    VarFileInfo([VarStruct(u'Translation', [1033, 1200])])
  ]
)
'''
        
        version_path = self.root_dir / "version_info.txt"
        with open(version_path, 'w', encoding='utf-8') as f:
            f.write(version_info)
        
        print(f"✅ Version info created: {version_path}")
        return version_path
    
    def install_build_deps(self):
        """Install build dependencies"""
        print("📦 Installing build dependencies...")
        
        try:
            subprocess.run([
                sys.executable, "-m", "pip", "install", "-r", "requirements_build.txt"
            ], check=True, cwd=self.root_dir)
            print("✅ Build dependencies installed")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install build dependencies: {e}")
            return False
        
        return True
    
    def build_executable(self, spec_path, name):
        """Build executable using PyInstaller"""
        print(f"🔨 Building {name}...")
        
        try:
            cmd = [
                sys.executable, "-m", "PyInstaller",
                "--clean",
                "--noconfirm",
                str(spec_path)
            ]
            
            result = subprocess.run(cmd, cwd=self.root_dir, capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"✅ {name} built successfully")
                return True
            else:
                print(f"❌ Failed to build {name}")
                print("STDOUT:", result.stdout)
                print("STDERR:", result.stderr)
                return False
                
        except Exception as e:
            print(f"❌ Error building {name}: {e}")
            return False
    
    def create_installer_script(self):
        """Create NSIS installer script"""
        installer_script = f'''
; MonMan Bot Installer Script
; Generated by build system

!define APP_NAME "MonMan Bot"
!define APP_VERSION "{self.config["version"]}"
!define APP_PUBLISHER "{self.config["author"]}"
!define APP_URL "https://github.com/AhmadMunir/money-manager-bot"
!define APP_EXECUTABLE "MonManBot-GUI.exe"

!include "MUI2.nsh"

Name "${{APP_NAME}}"
OutFile "MonManBot-Setup-${{APP_VERSION}}.exe"
InstallDir "$PROGRAMFILES\\${{APP_NAME}}"
InstallDirRegKey HKCU "Software\\${{APP_NAME}}" ""
RequestExecutionLevel admin

!define MUI_ABORTWARNING
!define MUI_ICON "assets\\icon.ico"
!define MUI_UNICON "assets\\icon.ico"

!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_LICENSE "LICENSE"
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

!insertmacro MUI_UNPAGE_WELCOME
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES
!insertmacro MUI_UNPAGE_FINISH

!insertmacro MUI_LANGUAGE "English"

Section "Main Application" SecMain
    SetOutPath "$INSTDIR"
    
    ; Install main files
    File "dist\\MonManBot-GUI.exe"
    File "dist\\MonManBot-CLI.exe"
    File "dist\\MonManBot.exe"
    
    ; Install additional files
    File /r "config"
    File /r "logs"
    File /r "assets"
    File "requirements*.txt"
    File "README.md"
    
    ; Create shortcuts
    CreateDirectory "$SMPROGRAMS\\${{APP_NAME}}"
    CreateShortCut "$SMPROGRAMS\\${{APP_NAME}}\\${{APP_NAME}}.lnk" "$INSTDIR\\${{APP_EXECUTABLE}}"
    CreateShortCut "$SMPROGRAMS\\${{APP_NAME}}\\${{APP_NAME}} CLI.lnk" "$INSTDIR\\MonManBot-CLI.exe"
    CreateShortCut "$DESKTOP\\${{APP_NAME}}.lnk" "$INSTDIR\\${{APP_EXECUTABLE}}"
    
    ; Registry entries
    WriteRegStr HKCU "Software\\${{APP_NAME}}" "" $INSTDIR
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${{APP_NAME}}" "DisplayName" "${{APP_NAME}}"
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${{APP_NAME}}" "UninstallString" "$INSTDIR\\Uninstall.exe"
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${{APP_NAME}}" "DisplayVersion" "${{APP_VERSION}}"
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${{APP_NAME}}" "Publisher" "${{APP_PUBLISHER}}"
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${{APP_NAME}}" "URLInfoAbout" "${{APP_URL}}"
    
    WriteUninstaller "$INSTDIR\\Uninstall.exe"
SectionEnd

Section "Uninstall"
    Delete "$INSTDIR\\*.exe"
    RMDir /r "$INSTDIR\\config"
    RMDir /r "$INSTDIR\\logs"  
    RMDir /r "$INSTDIR\\assets"
    Delete "$INSTDIR\\*.txt"
    Delete "$INSTDIR\\*.md"
    Delete "$INSTDIR\\Uninstall.exe"
    RMDir "$INSTDIR"
    
    Delete "$SMPROGRAMS\\${{APP_NAME}}\\*.lnk"
    RMDir "$SMPROGRAMS\\${{APP_NAME}}"
    Delete "$DESKTOP\\${{APP_NAME}}.lnk"
    
    DeleteRegKey HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${{APP_NAME}}"
    DeleteRegKey HKCU "Software\\${{APP_NAME}}"
SectionEnd
'''
        
        installer_path = self.root_dir / "installer.nsi"
        with open(installer_path, 'w') as f:
            f.write(installer_script)
        
        print(f"✅ Installer script created: {installer_path}")
        return installer_path
    
    def create_portable_package(self):
        """Create portable package"""
        print("📦 Creating portable package...")
        
        portable_dir = self.dist_dir / "MonManBot-Portable"
        
        # Clean and create portable directory
        if portable_dir.exists():
            shutil.rmtree(portable_dir)
        portable_dir.mkdir(parents=True)
        
        # Copy executables
        for exe_name in ["MonManBot-GUI.exe", "MonManBot-CLI.exe", "MonManBot.exe"]:
            exe_path = self.dist_dir / exe_name
            if exe_path.exists():
                shutil.copy2(exe_path, portable_dir)
        
        # Copy essential files
        essential_files = [
            "README.md",
            "requirements.txt",
            "requirements_launcher.txt",
            ".env.example"
        ]
        
        for file_name in essential_files:
            file_path = self.root_dir / file_name
            if file_path.exists():
                shutil.copy2(file_path, portable_dir)
        
        # Copy directories
        essential_dirs = ["config", "logs", "assets"]
        for dir_name in essential_dirs:
            dir_path = self.root_dir / dir_name
            if dir_path.exists():
                shutil.copytree(dir_path, portable_dir / dir_name)
        
        # Create run scripts
        run_gui_bat = portable_dir / "Run-GUI.bat"
        with open(run_gui_bat, 'w') as f:
            f.write('@echo off\n')
            f.write('echo Starting MonMan Bot GUI...\n')
            f.write('MonManBot-GUI.exe\n')
            f.write('pause\n')
        
        run_cli_bat = portable_dir / "Run-CLI.bat"
        with open(run_cli_bat, 'w') as f:
            f.write('@echo off\n')
            f.write('echo MonMan Bot CLI Interface\n')
            f.write('MonManBot-CLI.exe menu\n')
            f.write('pause\n')
        
        # Create ZIP package
        import zipfile
        zip_path = self.dist_dir / f"MonManBot-Portable-{self.config['version']}.zip"
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(portable_dir):
                for file in files:
                    file_path = Path(root) / file
                    arc_name = file_path.relative_to(portable_dir)
                    zipf.write(file_path, arc_name)
        
        print(f"✅ Portable package created: {zip_path}")
        return zip_path
    
    def cleanup_build(self):
        """Clean up build artifacts"""
        print("🧹 Cleaning up build artifacts...")
        
        # Remove build directory
        if self.build_dir.exists():
            shutil.rmtree(self.build_dir)
        
        # Remove spec files
        for spec_file in self.spec_dir.glob("*.spec"):
            spec_file.unlink()
        
        # Remove version info
        version_file = self.root_dir / "version_info.txt"
        if version_file.exists():
            version_file.unlink()
        
        print("✅ Cleanup completed")
    
    def build_all(self):
        """Build all executables"""
        print("🚀 Starting MonMan Bot build process...")
        
        # Setup
        self.setup_build_env()
        
        # Install dependencies
        if not self.install_build_deps():
            return False
        
        # Create version info
        self.create_version_info()
        
        # Create specs
        gui_spec = self.create_gui_spec()
        cli_spec = self.create_cli_spec()
        bot_spec = self.create_bot_spec()
        
        # Build executables
        success = True
        success &= self.build_executable(gui_spec, "GUI Launcher")
        success &= self.build_executable(cli_spec, "CLI Launcher")
        success &= self.build_executable(bot_spec, "Main Bot")
        
        if success:
            # Create packages
            self.create_portable_package()
            self.create_installer_script()
            
            print("🎉 Build completed successfully!")
            print(f"📁 Output directory: {self.dist_dir}")
            print("\n📦 Generated files:")
            
            for item in self.dist_dir.iterdir():
                if item.is_file():
                    size = item.stat().st_size / (1024 * 1024)  # MB
                    print(f"  - {item.name} ({size:.1f} MB)")
        else:
            print("❌ Build failed!")
        
        # Cleanup
        self.cleanup_build()
        
        return success

def main():
    """Main build function"""
    builder = BuildSystem()
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "setup":
            builder.setup_build_env()
        elif command == "deps":
            builder.install_build_deps()
        elif command == "gui":
            builder.setup_build_env()
            builder.create_version_info()
            gui_spec = builder.create_gui_spec()
            builder.build_executable(gui_spec, "GUI Launcher")
        elif command == "cli":
            builder.setup_build_env()
            builder.create_version_info()
            cli_spec = builder.create_cli_spec()
            builder.build_executable(cli_spec, "CLI Launcher")
        elif command == "bot":
            builder.setup_build_env()
            builder.create_version_info()
            bot_spec = builder.create_bot_spec()
            builder.build_executable(bot_spec, "Main Bot")
        elif command == "package":
            builder.create_portable_package()
        elif command == "clean":
            builder.cleanup_build()
        else:
            print("Usage: python build.py [setup|deps|gui|cli|bot|package|clean]")
            print("       python build.py        # Build all")
    else:
        # Build everything
        builder.build_all()

if __name__ == "__main__":
    main()
