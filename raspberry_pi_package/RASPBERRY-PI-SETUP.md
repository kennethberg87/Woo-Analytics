# WooCommerce Dashboard - Raspberry Pi Setup Guide

This guide provides detailed instructions for setting up and running the WooCommerce Dashboard on your Raspberry Pi using port 3000.

## Prerequisites

- Raspberry Pi (3 or newer recommended) with Raspberry Pi OS (formerly Raspbian)
- Internet connection
- Your WooCommerce API credentials (key and secret)
- Basic familiarity with terminal commands

## Hardware Recommendations

For optimal performance:
- Raspberry Pi 4 with at least 2GB RAM recommended
- Use a high-quality microSD card (Class 10 or better)
- Consider using a cooling case or fan for long-term operation

## Setup Instructions

### Step 1: Prepare Your Raspberry Pi

1. Start with a fresh installation of Raspberry Pi OS (Lite is sufficient if you're not using the desktop)
2. Update your system:

```bash
sudo apt update
sudo apt upgrade -y
```

3. Install required dependencies:

```bash
sudo apt install -y python3-pip python3-venv git libatlas-base-dev
```

### Step 2: Download the Application

1. Create a directory for the application:

```bash
mkdir -p ~/woocommerce-dashboard
cd ~/woocommerce-dashboard
```

2. Option A - Download and extract the zip file:

```bash
wget https://github.com/YOUR-USERNAME/woocommerce-dashboard/archive/main.zip
unzip main.zip
mv woocommerce-dashboard-main/* .
rm -rf woocommerce-dashboard-main main.zip
```

3. Option B - Clone the repository (if using Git):

```bash
git clone https://github.com/YOUR-USERNAME/woocommerce-dashboard.git .
```

### Step 3: Set Up Python Environment

Create a virtual environment and install required packages:

```bash
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip

# Install optimized versions of heavy packages for ARM
pip install numpy --only-binary :all:
pip install pandas --only-binary :all:

# Install all other requirements
pip install streamlit plotly pytz woocommerce google-ads google-analytics-data plotly
```

#### Note on Memory Usage

Raspberry Pi has limited RAM. To optimize performance:

```bash
# Add a swapfile if you don't already have one
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
```

### Step 4: Configure the Application

1. Create a `.env` file with your WooCommerce credentials:

```bash
cat > .env << EOF
WOOCOMMERCE_URL=https://your-store.com
WOOCOMMERCE_KEY=your_consumer_key
WOOCOMMERCE_SECRET=your_consumer_secret

# Optional - only if using Google Analytics integration
GOOGLE_ANALYTICS_PROPERTY_ID=your_property_id

# Optional - only if using Google Ads integration
GOOGLE_ADS_DEVELOPER_TOKEN=your_developer_token
GOOGLE_ADS_CLIENT_ID=your_client_id
GOOGLE_ADS_CLIENT_SECRET=your_client_secret
GOOGLE_ADS_REFRESH_TOKEN=your_refresh_token
GOOGLE_ADS_CUSTOMER_ID=your_customer_id
EOF
```

2. Create a helper script to load environment variables:

```bash
cat > load_env.sh << EOF
#!/bin/bash
set -a
source .env
set +a
EOF

chmod +x load_env.sh
```

3. Configure Streamlit to use port 3000:

```bash
mkdir -p ~/.streamlit
cat > ~/.streamlit/config.toml << EOF
[server]
headless = true
port = 3000
address = "0.0.0.0"
enableCORS = false
enableXsrfProtection = true
EOF
```

### Step 5: Create a Startup Script

Create a run script to make it easier to start the dashboard:

```bash
cat > run_dashboard.sh << EOF
#!/bin/bash
cd ~/woocommerce-dashboard
source venv/bin/activate
source ./load_env.sh
streamlit run woocommerce_dashboard.py
EOF

chmod +x run_dashboard.sh
```

### Step 6: Set Up Automatic Startup (Optional)

Create a systemd service to automatically start the dashboard on boot:

```bash
sudo nano /etc/systemd/system/woocommerce-dashboard.service
```

Add the following content (replace `pi` with your username if different):

```
[Unit]
Description=WooCommerce Dashboard Streamlit App
After=network.target

[Service]
User=pi
WorkingDirectory=/home/pi/woocommerce-dashboard
ExecStart=/bin/bash -c 'source /home/pi/woocommerce-dashboard/venv/bin/activate && source /home/pi/woocommerce-dashboard/load_env.sh && streamlit run /home/pi/woocommerce-dashboard/woocommerce_dashboard.py --server.port 3000'
Restart=always
RestartSec=10
StandardOutput=syslog
StandardError=syslog
SyslogIdentifier=woocommerce-dashboard

[Install]
WantedBy=multi-user.target
```

Enable and start the service:

```bash
sudo systemctl enable woocommerce-dashboard.service
sudo systemctl start woocommerce-dashboard.service
```

### Step 7: Run the Dashboard

If you're not using the automatic startup option, start the dashboard manually:

```bash
./run_dashboard.sh
```

Access the dashboard by opening a browser and navigating to:
- `http://YOUR-PI-IP:3000` (from another device on your network)
- `http://localhost:3000` (from the Raspberry Pi itself if using Desktop version)

## Performance Optimizations for Raspberry Pi

### Reduce Memory Usage

For better performance on resource-limited Raspberry Pi:

1. Optimize the environment configuration in `~/.streamlit/config.toml`:

```toml
[server]
headless = true
port = 3000
address = "0.0.0.0"
enableCORS = false
maxUploadSize = 5
maxMessageSize = 50

[runner]
magicEnabled = false

[browser]
gatherUsageStats = false

[global]
developmentMode = false
```

2. Add memory optimization to your startup:

```bash
# Modify your run_dashboard.sh
export STREAMLIT_SERVER_MAX_UPLOAD_SIZE=5
export PYTHONOPTIMIZE=2
export STREAMLIT_BROWSER_GATHER_USAGE_STATS=false
```

### Network Performance

If you plan to access your dashboard from outside your local network:

1. Set up port forwarding in your router (forward port 3000 to your Raspberry Pi)
2. Consider using a dynamic DNS service if you don't have a static IP
3. For security, consider setting up a reverse proxy with authentication

## Troubleshooting

### Dashboard Crashes or Runs Slowly

1. Check memory usage: `free -h`
2. Monitor system resources during operation: `htop`
3. Consider reducing the date range of data fetched
4. Ensure your Pi has adequate cooling

### Connection Issues

If you can't connect to your dashboard:

1. Check if the service is running: `sudo systemctl status woocommerce-dashboard.service`
2. Verify you can access port 3000: `curl localhost:3000`
3. Check if any firewall is blocking access: `sudo ufw status` (if ufw is installed)
4. Ensure the IP address you're using for your Pi is correct: `hostname -I`

### Log Files

To view logs for troubleshooting:

```bash
sudo journalctl -u woocommerce-dashboard.service -f
```

## Updating the Dashboard

To update the dashboard to a newer version:

1. Stop the service: `sudo systemctl stop woocommerce-dashboard.service`
2. Back up your credentials: `cp .env .env.backup`
3. Update the code (pull from Git or extract new zip)
4. Restore your credentials: `cp .env.backup .env`
5. Restart the service: `sudo systemctl start woocommerce-dashboard.service`

## Raspberry Pi Maintenance

For stable long-term operation:

1. Set up automatic updates: 
   ```bash
   sudo apt install unattended-upgrades
   sudo dpkg-reconfigure unattended-upgrades
   ```

2. Monitor disk space regularly:
   ```bash
   df -h
   ```

3. Consider a backup solution for your configuration
   ```bash
   # Simple backup script
   rsync -avz --exclude='venv' ~/woocommerce-dashboard/ ~/backup/woocommerce-dashboard/
   ```