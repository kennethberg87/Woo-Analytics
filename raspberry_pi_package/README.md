# WooCommerce Dashboard for Raspberry Pi

A high-performance Streamlit dashboard for WooCommerce sales analytics, providing comprehensive Norwegian business insights with advanced revenue tracking and real-time performance monitoring.

## What's Included in This Package

This package contains everything you need to run the WooCommerce Dashboard on your Raspberry Pi without needing to use Git:

### Core Files
- `woocommerce_dashboard.py` - Main dashboard application
- `utils/` - Directory containing all utility modules
- `requirements.txt` - List of Python packages required

### Raspberry Pi Specific Files
- `run_on_pi.sh` - Script to start the dashboard on port 3000
- `setup_raspberry_pi.sh` - Setup script that automates the installation process
- `.streamlit/config.toml` - Streamlit configuration for port 3000
- `.env.example` - Template for environment variables

### Documentation
- `README.md` (this file) - Overview and quick start guide
- `RASPBERRY-PI-SETUP.md` - Detailed setup instructions
- `RASPBERRY-PI-FILES.md` - Explanation of the included files

## Quick Start

1. Extract this package on your Raspberry Pi
2. Make the setup script executable:
   ```
   chmod +x setup_raspberry_pi.sh
   ```
3. Run the setup script:
   ```
   ./setup_raspberry_pi.sh
   ```
4. Configure your credentials:
   ```
   cp .env.example .env
   nano .env
   ```
5. Start the dashboard:
   ```
   ./run_on_pi.sh
   ```
6. Access your dashboard at:
   ```
   http://<your-raspberry-pi-ip>:3000
   ```

## Features

- Real-time WooCommerce sales data visualization
- Advanced revenue tracking and profit calculations
- Customer insights and retention analysis
- Product performance monitoring
- Multilingual support (Norwegian/English)
- Google Analytics and Google Ads integration (optional)
- Optimized for Raspberry Pi performance

## System Requirements

- Raspberry Pi 3 or newer (4+ recommended)
- Raspberry Pi OS (formerly Raspbian) Bullseye or newer
- At least 2GB RAM
- Internet connection for WooCommerce API access

For detailed setup instructions, see the `RASPBERRY-PI-SETUP.md` file.