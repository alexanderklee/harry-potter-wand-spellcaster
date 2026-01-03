#!/bin/bash
# Wand Spellcaster - Setup Script
# ================================
# Run this script on a fresh Raspberry Pi OS installation
# Usage: bash setup.sh

set -e  # Exit on error

echo "╔════════════════════════════════════════════╗"
echo "║       WAND SPELLCASTER SETUP SCRIPT        ║"
echo "╚════════════════════════════════════════════╝"
echo ""

# Check if running on Raspberry Pi
if [ ! -f /proc/device-tree/model ]; then
    echo "⚠️  Warning: This doesn't appear to be a Raspberry Pi"
    echo "   Some features may not work correctly."
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
else
    PI_MODEL=$(cat /proc/device-tree/model)
    echo "✓ Detected: $PI_MODEL"
fi
echo ""

# Step 1: System Update
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Step 1/5: Updating system packages..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
sudo apt update
sudo apt upgrade -y
echo "✓ System updated"
echo ""

# Step 2: Install System Dependencies
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Step 2/5: Installing system dependencies..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
sudo apt install -y \
    python3-pip \
    python3-venv \
    python3-opencv \
    python3-numpy \
    python3-pygame \
    python3-pil \
    libatlas-base-dev \
    i2c-tools \
    git

# Install PiCamera2 if available
if apt-cache show python3-picamera2 &> /dev/null; then
    sudo apt install -y python3-picamera2
    echo "✓ PiCamera2 installed"
else
    echo "⚠️  PiCamera2 not available (will use OpenCV fallback)"
fi

echo "✓ System dependencies installed"
echo ""

# Step 3: Enable Interfaces
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Step 3/5: Enabling hardware interfaces..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Enable I2C
if ! grep -q "^dtparam=i2c_arm=on" /boot/config.txt 2>/dev/null && \
   ! grep -q "^dtparam=i2c_arm=on" /boot/firmware/config.txt 2>/dev/null; then
    echo "Enabling I2C..."
    sudo raspi-config nonint do_i2c 0
fi
echo "✓ I2C enabled"

# Enable Camera (legacy method for older Pi OS)
if grep -q "start_x=0" /boot/config.txt 2>/dev/null; then
    echo "Enabling camera..."
    sudo raspi-config nonint do_camera 0
fi
echo "✓ Camera interface enabled"

echo ""

# Step 4: Create Virtual Environment and Install Python Packages
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Step 4/5: Setting up Python environment..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Create virtual environment
if [ ! -d "venv" ]; then
    python3 -m venv venv --system-site-packages
    echo "✓ Virtual environment created"
fi

# Activate and install packages
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
echo "✓ Python packages installed"
echo ""

# Step 5: Create directories and test
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Step 5/5: Final setup..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Create models directory
mkdir -p models

# Copy default config if not exists
if [ ! -f "config/settings.yaml" ]; then
    if [ -f "config/settings.yaml.example" ]; then
        cp config/settings.yaml.example config/settings.yaml
        echo "✓ Created config/settings.yaml from example"
    else
        echo "⚠️  No example config found"
    fi
fi

# Test camera
echo "Testing camera..."
if command -v libcamera-hello &> /dev/null; then
    timeout 3 libcamera-hello --nopreview &> /dev/null && echo "✓ Camera working" || echo "⚠️  Camera test failed (may need reboot)"
elif command -v raspistill &> /dev/null; then
    timeout 3 raspistill -o /tmp/test.jpg &> /dev/null && echo "✓ Camera working" && rm -f /tmp/test.jpg || echo "⚠️  Camera test failed (may need reboot)"
else
    echo "⚠️  No camera utility found"
fi

# Test I2C (for OLED)
echo "Testing I2C..."
if i2cdetect -y 1 2>/dev/null | grep -q "3c"; then
    echo "✓ OLED display detected at 0x3C"
else
    echo "ℹ️  No I2C device at 0x3C (OLED not connected or different address)"
fi

echo ""
echo "╔════════════════════════════════════════════╗"
echo "║           SETUP COMPLETE! 🪄               ║"
echo "╚════════════════════════════════════════════╝"
echo ""
echo "Next steps:"
echo "  1. Reboot your Pi:     sudo reboot"
echo "  2. Activate venv:      source venv/bin/activate"
echo "  3. Run calibration:    python3 src/main.py --calibrate"
echo "  4. Start detecting:    python3 src/main.py"
echo ""
echo "For debug mode with visual feedback:"
echo "  python3 src/main.py --debug"
echo ""
echo "Need help? See README.md and docs/HARDWARE_GUIDE.md"
echo ""
