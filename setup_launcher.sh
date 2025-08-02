#!/bin/bash
# MonMan Bot - Setup Script for Linux/macOS
# This script sets up the launcher and creates system integration

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LAUNCHER_SCRIPT="$SCRIPT_DIR/monman"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_info "Setting up MonMan Bot Launcher..."

# Make launcher executable
if [ -f "$LAUNCHER_SCRIPT" ]; then
    chmod +x "$LAUNCHER_SCRIPT"
    print_success "Made launcher script executable"
else
    print_error "Launcher script not found: $LAUNCHER_SCRIPT"
    exit 1
fi

# Install Python dependencies
print_info "Installing launcher dependencies..."
if command -v pip3 &> /dev/null; then
    pip3 install -r requirements_launcher.txt
    print_success "Dependencies installed"
else
    print_warning "pip3 not found, please install dependencies manually:"
    echo "pip3 install -r requirements_launcher.txt"
fi

# Create directories
mkdir -p logs config
print_success "Created required directories"

# Offer to create system-wide link
echo ""
read -p "Create system-wide launcher link? [y/N]: " create_link
if [[ $create_link =~ ^[Yy]$ ]]; then
    SYSTEM_BIN="/usr/local/bin/monman-bot"
    
    if [ -w "/usr/local/bin" ] || sudo -n true 2>/dev/null; then
        # Create symlink
        if [ -w "/usr/local/bin" ]; then
            ln -sf "$LAUNCHER_SCRIPT" "$SYSTEM_BIN"
        else
            sudo ln -sf "$LAUNCHER_SCRIPT" "$SYSTEM_BIN"
        fi
        print_success "System-wide launcher created: $SYSTEM_BIN"
        print_info "You can now run 'monman-bot' from anywhere"
    else
        print_warning "Cannot create system-wide link (no sudo access)"
        print_info "You can create it manually: sudo ln -sf '$LAUNCHER_SCRIPT' '$SYSTEM_BIN'"
    fi
fi

# Create desktop entry for GUI systems
if [ -n "$DISPLAY" ] || [ -n "$WAYLAND_DISPLAY" ]; then
    read -p "Create desktop entry? [y/N]: " create_desktop
    if [[ $create_desktop =~ ^[Yy]$ ]]; then
        DESKTOP_FILE="$HOME/.local/share/applications/monman-bot.desktop"
        mkdir -p "$(dirname "$DESKTOP_FILE")"
        
        cat > "$DESKTOP_FILE" << EOF
[Desktop Entry]
Name=MonMan Bot Launcher
Comment=Finance Bot Management Interface
Exec=python3 "$SCRIPT_DIR/gui_launcher.py"
Icon=utilities-system-monitor
Terminal=false
Type=Application
Categories=Office;Finance;
StartupNotify=true
EOF
        print_success "Desktop entry created: $DESKTOP_FILE"
    fi
fi

# Create systemd service (optional)
read -p "Create systemd service for auto-start? [y/N]: " create_service
if [[ $create_service =~ ^[Yy]$ ]]; then
    SERVICE_FILE="$HOME/.config/systemd/user/monman-bot.service"
    mkdir -p "$(dirname "$SERVICE_FILE")"
    
    cat > "$SERVICE_FILE" << EOF
[Unit]
Description=MonMan Finance Bot
After=network.target

[Service]
Type=simple
ExecStart=python3 $SCRIPT_DIR/main.py
WorkingDirectory=$SCRIPT_DIR
Restart=always
RestartSec=10
Environment=PYTHONPATH=$SCRIPT_DIR

[Install]
WantedBy=default.target
EOF
    
    # Enable and start service
    systemctl --user daemon-reload
    systemctl --user enable monman-bot.service
    
    print_success "Systemd service created and enabled"
    print_info "Service commands:"
    echo "  Start:   systemctl --user start monman-bot"
    echo "  Stop:    systemctl --user stop monman-bot"
    echo "  Status:  systemctl --user status monman-bot"
    echo "  Logs:    journalctl --user -u monman-bot -f"
fi

echo ""
print_success "Setup completed!"
print_info "Usage examples:"
echo "  ./monman              # Interactive menu"
echo "  ./monman start        # Start bot"
echo "  ./monman status       # Check status"
echo "  ./monman logs -f      # Follow logs"
echo "  python3 gui_launcher.py  # GUI interface"
echo ""
