# Downloadable Files for Raspberry Pi Setup

This document explains the downloadable files needed to set up the WooCommerce Dashboard on your Raspberry Pi.

## Files Included in the Download

The download package contains the following files:

### Setup Scripts
- `scripts/setup_raspberry_pi.sh` - Main setup script that automates the installation process
- `scripts/load_env.sh` - Helper script to load environment variables
- `scripts/run_dashboard.sh` - Script to start the dashboard on port 3000
- `scripts/.env.example` - Template for environment variables configuration

### Documentation
- `RASPBERRY-PI-SETUP.md` - Comprehensive setup and configuration guide
- `RASPBERRY-PI-FILES.md` (this file) - Explanation of the downloadable files

## How to Use the Files

1. **Download the Package**
   - Save the ZIP file to your Raspberry Pi
   - Extract it: `unzip woocommerce-dashboard-raspberry-pi.zip`

2. **Run the Setup Script**
   ```bash
   cd woocommerce-dashboard-raspberry-pi
   chmod +x scripts/setup_raspberry_pi.sh
   ./scripts/setup_raspberry_pi.sh
   ```

3. **Configure Environment Variables**
   - Copy the example environment file: `cp scripts/.env.example .env`
   - Edit with your credentials: `nano .env`

4. **Download the Application Files**
   - After running the setup script, follow the instructions in `DOWNLOAD_INSTRUCTIONS.md`
   - Make sure to download the main app file (`woocommerce_dashboard.py`) and utilities directory (`utils/`)

5. **Run the Dashboard**
   ```bash
   ./scripts/run_dashboard.sh
   ```

## File Structure After Setup

After completing the setup, your directory structure should look like this:

```
~/woocommerce-dashboard/
├── .env                       # Your environment configuration
├── .streamlit/                # Streamlit configuration directory
│   └── config.toml            # Streamlit configuration for port 3000
├── venv/                      # Python virtual environment
├── load_env.sh                # Environment variables loader script
├── run_dashboard.sh           # Dashboard startup script
├── woocommerce_dashboard.py   # Main application file
├── utils/                     # Utility modules
│   ├── data_processor.py      # Data processing utilities
│   ├── export_handler.py      # Export functionality
│   ├── google_ads_client.py   # Google Ads integration
│   ├── google_analytics_client.py # Google Analytics integration
│   ├── notification_handler.py # Notification system
│   ├── translations.py        # Language translations
│   └── woocommerce_client.py  # WooCommerce API client
└── woocommerce-dashboard.service # Systemd service file
```

## Automatic Startup (Optional)

To set up automatic startup when your Raspberry Pi boots:

```bash
sudo cp ~/woocommerce-dashboard/woocommerce-dashboard.service /etc/systemd/system/
sudo systemctl enable woocommerce-dashboard.service
sudo systemctl start woocommerce-dashboard.service
```

## Troubleshooting

If you encounter issues with the setup:

1. Check the logs: `sudo journalctl -u woocommerce-dashboard.service -f`
2. Verify environment variables: `source .env && echo $WOOCOMMERCE_URL`
3. Test network connectivity: `curl -I https://your-woocommerce-store.com`
4. Check Python environment: `source venv/bin/activate && python -c "import streamlit; print(streamlit.__version__)"`

For more detailed troubleshooting, refer to the `RASPBERRY-PI-SETUP.md` file.