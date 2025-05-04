#!/bin/bash
# WooCommerce Dashboard - Package Creator
# This script creates a distributable package for the Raspberry Pi

# Display header
echo "-------------------------------------"
echo "  WooCommerce Dashboard Package Creator  "
echo "  For Raspberry Pi Distribution           "
echo "-------------------------------------"

# Set package name with timestamp
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
PACKAGE_NAME="woocommerce-dashboard-raspi-$TIMESTAMP"
CURRENT_DIR=$(pwd)

# Ensure script is run from the correct directory
if [[ ! -f "woocommerce_dashboard.py" ]]; then
    echo "ERROR: This script must be run from the raspberry_pi_package directory."
    echo "Change to the correct directory and try again."
    exit 1
fi

# Make scripts executable
echo "Making scripts executable..."
chmod +x run_on_pi.sh
chmod +x setup_raspberry_pi.sh
chmod +x scripts/load_env.sh

# Create temporary directory for package
echo "Creating package structure..."
TEMP_DIR="/tmp/$PACKAGE_NAME"
mkdir -p "$TEMP_DIR"

# Copy files to package directory
echo "Copying files to package..."
cp -r woocommerce_dashboard.py utils scripts .streamlit requirements.txt .env.example README.md RASPBERRY-PI-SETUP.md RASPBERRY-PI-FILES.md run_on_pi.sh setup_raspberry_pi.sh "$TEMP_DIR/"

# Create ZIP archive
echo "Creating ZIP archive..."
cd /tmp
zip -r "$PACKAGE_NAME.zip" "$PACKAGE_NAME"
mv "$PACKAGE_NAME.zip" "$CURRENT_DIR/"

# Create TAR.GZ archive
echo "Creating TAR.GZ archive..."
tar -czf "$PACKAGE_NAME.tar.gz" "$PACKAGE_NAME"
mv "$PACKAGE_NAME.tar.gz" "$CURRENT_DIR/"

# Cleanup
echo "Cleaning up temporary files..."
rm -rf "$TEMP_DIR"

# Success message
echo ""
echo "Package creation complete!"
echo ""
echo "Created files:"
echo "- $CURRENT_DIR/$PACKAGE_NAME.zip"
echo "- $CURRENT_DIR/$PACKAGE_NAME.tar.gz"
echo ""
echo "These files contain everything needed to run"
echo "the WooCommerce Dashboard on a Raspberry Pi."
echo ""
echo "Instructions for users:"
echo "1. Download either the ZIP or TAR.GZ file"
echo "2. Extract the archive on the Raspberry Pi"
echo "3. Run setup_raspberry_pi.sh to install"
echo "4. Configure credentials in .env file"
echo "5. Start dashboard with run_on_pi.sh"