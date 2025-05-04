# WooCommerce Dashboard - Raspberry Pi Setup Guide

This guide provides detailed instructions for setting up the WooCommerce Dashboard on your Raspberry Pi.

## Hardware Requirements

For optimal performance, we recommend:
- Raspberry Pi 4 with at least 2GB RAM (4GB recommended)
- 16GB+ microSD card (Class 10 or better)
- Power supply with at least 2.5A output
- Ethernet connection (recommended) or stable Wi-Fi
- Display connected to HDMI for setup (optional)

## Operating System Setup

1. Install Raspberry Pi OS (formerly Raspbian):
   - Download the Raspberry Pi Imager from https://www.raspberrypi.org/software/
   - Select Raspberry Pi OS (64-bit) for best performance
   - Write the OS to your microSD card

2. Initial setup:
   - Boot your Raspberry Pi and follow the initial setup wizard
   - Configure your Wi-Fi or connect via Ethernet
   - Enable SSH for remote access (optional but recommended)
   - Update your system:
     ```bash
     sudo apt update
     sudo apt upgrade -y
     ```

## Dashboard Installation

### Automatic Installation (Recommended)

1. Extract the WooCommerce Dashboard package:
   ```bash
   mkdir -p ~/woocommerce-dashboard
   cd ~/woocommerce-dashboard
   # Extract the files you downloaded
   ```

2. Run the automated setup script:
   ```bash
   chmod +x setup_raspberry_pi.sh
   ./setup_raspberry_pi.sh
   ```

3. Configure your WooCommerce credentials:
   ```bash
   cp .env.example .env
   nano .env
   ```
   
   Edit the `.env` file with your WooCommerce URL, key, and secret.

4. Start the dashboard:
   ```bash
   ./run_on_pi.sh
   ```

### Manual Installation (Alternative)

If you prefer to set things up manually:

1. Create installation directory:
   ```bash
   mkdir -p ~/woocommerce-dashboard
   cd ~/woocommerce-dashboard
   ```

2. Install system dependencies:
   ```bash
   sudo apt-get update
   sudo apt-get install -y python3-venv python3-pip python3-dev libatlas-base-dev
   ```

3. Create and activate a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

4. Install Python dependencies:
   ```bash
   pip install --upgrade pip setuptools wheel
   pip install numpy pandas
   pip install streamlit woocommerce plotly reportlab openpyxl google-analytics-data google-api-python-client google-auth-httplib2 google-auth-oauthlib twilio
   ```

5. Configure Streamlit:
   ```bash
   mkdir -p ~/.streamlit
   nano ~/.streamlit/config.toml
   ```
   
   Add this configuration:
   ```toml
   [server]
   headless = true
   port = 3000
   address = "0.0.0.0"
   ```

6. Create environment variable file:
   ```bash
   nano .env
   ```
   
   Add your credentials:
   ```
   WOOCOMMERCE_URL=https://your-store.com
   WOOCOMMERCE_KEY=your_key
   WOOCOMMERCE_SECRET=your_secret
   ```

7. Create a script to load environment variables:
   ```bash
   nano load_env.sh
   ```
   
   Add:
   ```bash
   #!/bin/bash
   set -a
   source .env
   set +a
   ```
   
   Make it executable:
   ```bash
   chmod +x load_env.sh
   ```

8. Start the dashboard:
   ```bash
   source load_env.sh
   streamlit run woocommerce_dashboard.py --server.port 3000
   ```

## Automatic Startup (Optional)

To make the dashboard start automatically when your Raspberry Pi boots:

1. Create a systemd service file:
   ```bash
   sudo nano /etc/systemd/system/woocommerce-dashboard.service
   ```

2. Add the following content (adjust paths as needed):
   ```
   [Unit]
   Description=WooCommerce Dashboard
   After=network.target

   [Service]
   User=pi
   WorkingDirectory=/home/pi/woocommerce-dashboard
   Environment=PATH=/home/pi/woocommerce-dashboard/venv/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
   ExecStart=/home/pi/woocommerce-dashboard/venv/bin/streamlit run woocommerce_dashboard.py --server.port 3000
   Restart=on-failure
   RestartSec=5s

   [Install]
   WantedBy=multi-user.target
   ```

3. Enable and start the service:
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable woocommerce-dashboard.service
   sudo systemctl start woocommerce-dashboard.service
   ```

4. Check the status:
   ```bash
   sudo systemctl status woocommerce-dashboard.service
   ```

## Performance Optimization

To improve performance on the Raspberry Pi:

1. Add a swap file if you have less than 4GB RAM:
   ```bash
   sudo dphys-swapfile swapoff
   sudo nano /etc/dphys-swapfile
   ```
   
   Set `CONF_SWAPSIZE=2048` and then:
   
   ```bash
   sudo dphys-swapfile setup
   sudo dphys-swapfile swapon
   ```

2. Disable unnecessary services:
   ```bash
   sudo systemctl disable bluetooth.service
   sudo systemctl disable avahi-daemon.service
   ```

3. Overclock if needed (for Raspberry Pi 4 only):
   ```bash
   sudo nano /boot/config.txt
   ```
   
   Add:
   ```
   over_voltage=2
   arm_freq=1750
   ```

## Troubleshooting

### Dashboard Won't Start

1. Check Python environment:
   ```bash
   source venv/bin/activate
   python -c "import streamlit; print(streamlit.__version__)"
   ```

2. Verify environment variables:
   ```bash
   source .env && echo $WOOCOMMERCE_URL
   ```

3. Check for port conflicts:
   ```bash
   sudo netstat -tulpn | grep 3000
   ```

### Slow Performance

1. Monitor system resources:
   ```bash
   top
   ```

2. Check temperature (throttling can occur at high temps):
   ```bash
   vcgencmd measure_temp
   ```

3. Check disk space:
   ```bash
   df -h
   ```

### Connection Issues

1. Test network connectivity:
   ```bash
   ping -c 3 your-woocommerce-store.com
   curl -I https://your-woocommerce-store.com
   ```

2. Check WooCommerce API access:
   ```bash
   source .env
   curl -v https://$WOOCOMMERCE_URL/wp-json/wc/v3/orders?consumer_key=$WOOCOMMERCE_KEY&consumer_secret=$WOOCOMMERCE_SECRET&per_page=1
   ```

## Support and Feedback

For questions or issues with the dashboard setup, please:
1. Check the troubleshooting section above
2. Refer to the main documentation
3. Contact support for additional assistance