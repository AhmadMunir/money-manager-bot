#!/bin/bash
# Quick Build Script for Linux/macOS
# Builds MonMan Bot executables using PyInstaller

set -e

echo ""
echo "================================"
echo "   MonMan Bot Build System"
echo "================================"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is not installed or not in PATH"
    echo "Please install Python 3.8+ using your package manager"
    exit 1
fi

# Check if build.py exists
if [ ! -f "build.py" ]; then
    print_error "build.py not found"
    echo "Please run this script from the project root directory"
    exit 1
fi

# Show options
echo "Select build option:"
echo "1. Build All (GUI + CLI + Bot + Package)"
echo "2. Build GUI Launcher only"
echo "3. Build CLI Launcher only"
echo "4. Build Main Bot only"
echo "5. Create Portable Package only"
echo "6. Install Build Dependencies only"
echo "7. Clean Build Files"
echo ""

read -p "Enter your choice [1-7]: " choice

case $choice in
    1)
        print_info "Building all executables..."
        python3 build.py
        ;;
    2)
        print_info "Building GUI Launcher..."
        python3 build.py gui
        ;;
    3)
        print_info "Building CLI Launcher..."
        python3 build.py cli
        ;;
    4)
        print_info "Building Main Bot..."
        python3 build.py bot
        ;;
    5)
        print_info "Creating Portable Package..."
        python3 build.py package
        ;;
    6)
        print_info "Installing Build Dependencies..."
        python3 build.py deps
        ;;
    7)
        print_info "Cleaning Build Files..."
        python3 build.py clean
        ;;
    *)
        print_error "Invalid choice"
        exit 1
        ;;
esac

echo ""
echo -e "${GREEN}Build process completed!${NC}"
echo "Check the 'dist' folder for output files."
echo ""
