# WooCommerce Dashboard - Download Instructions

This directory contains the Raspberry Pi setup packages for the WooCommerce Dashboard.

## Available Download Formats

1. **ZIP Format** (Recommended for Windows users)
   - File: `woocommerce-dashboard-raspi-*.zip`
   - Extract with: `unzip woocommerce-dashboard-raspi-*.zip`

2. **TAR.GZ Format** (Recommended for Linux/Raspberry Pi users)
   - File: `woocommerce-dashboard-raspi-*.tar.gz`
   - Extract with: `tar -xzf woocommerce-dashboard-raspi-*.tar.gz`

## Quick Setup on Raspberry Pi

1. Download either file format to your Raspberry Pi
2. Extract the package:
   ```bash
   # For ZIP files
   unzip woocommerce-dashboard-raspi-*.zip
   
   # For TAR.GZ files
   tar -xzf woocommerce-dashboard-raspi-*.tar.gz
   ```

3. Navigate to the extracted directory:
   ```bash
   cd woocommerce-dashboard-raspi-*
   ```

4. Make the setup script executable:
   ```bash
   chmod +x setup_raspberry_pi.sh
   ```

5. Run the setup script:
   ```bash
   ./setup_raspberry_pi.sh
   ```

6. Follow the on-screen instructions to complete the setup

For detailed setup instructions, see the `RASPBERRY-PI-SETUP.md` file included in the package.

## Package Contents

The Raspberry Pi package includes:
- Main dashboard application (`woocommerce_dashboard.py`)
- Utility modules for data processing and API connections
- Streamlit configuration for port 3000
- Setup and run scripts
- Complete documentation

## Support

If you encounter issues with the download or setup process, please refer to the troubleshooting section in the `RASPBERRY-PI-SETUP.md` file.