# WooCommerce Dashboard - Quick Start Guide

This guide provides the essential steps to quickly deploy the WooCommerce Dashboard on your Ubuntu server.

## Prerequisites

- Ubuntu 20.04 LTS or newer
- Root or sudo access
- WooCommerce API credentials

## Quick Installation (Using Automated Script)

1. **Connect to your server** via SSH:
   ```bash
   ssh user@your-server-ip
   ```

2. **Download the deployment script**:
   ```bash
   wget https://raw.githubusercontent.com/YOUR-USERNAME/woocommerce-dashboard/main/deploy.sh
   chmod +x deploy.sh
   ```

3. **Run the script** with sudo:
   ```bash
   sudo ./deploy.sh
   ```

4. **Follow the prompts** to configure your installation.

5. **Copy application files** to the installation directory (specified during setup).

6. **Edit the `.env` file** with your WooCommerce API credentials.

7. **Start the service**:
   ```bash
   sudo systemctl enable woocommerce-dashboard.service
   sudo systemctl start woocommerce-dashboard.service
   ```

8. **Access your dashboard** at:
   - `http://your-server-ip` or
   - `https://your-domain.com` (if configured with a domain)

## Manual Installation Steps

If you prefer a manual installation, follow these steps:

1. **Update system**:
   ```bash
   sudo apt update
   sudo apt upgrade -y
   sudo apt install -y python3-pip python3-dev python3-venv build-essential libssl-dev libffi-dev git nginx
   ```

2. **Create a dedicated user** (optional):
   ```bash
   sudo adduser woo-dashboard
   sudo usermod -aG sudo woo-dashboard
   ```

3. **Clone or copy files**:
   ```bash
   # If using Git:
   git clone https://github.com/YOUR-USERNAME/woocommerce-dashboard.git
   
   # Or manually create directory:
   mkdir -p /home/woo-dashboard/woocommerce-dashboard
   # then copy files via SFTP or scp
   ```

4. **Set up Python environment**:
   ```bash
   cd /home/woo-dashboard/woocommerce-dashboard
   python3 -m venv venv
   source venv/bin/activate
   pip install --upgrade pip
   pip install -r requirements.txt  # Create this file based on INSTALLATION.md
   ```

5. **Configure Streamlit**:
   ```bash
   mkdir -p ~/.streamlit
   echo "[server]
   headless = true
   address = \"0.0.0.0\"
   port = 8501
   enableCORS = false" > ~/.streamlit/config.toml
   ```

6. **Set up environment variables** with your API credentials:
   ```bash
   echo "WOOCOMMERCE_URL=https://your-store.com
   WOOCOMMERCE_KEY=your_key
   WOOCOMMERCE_SECRET=your_secret" > .env
   ```

7. **Create systemd service**:
   ```bash
   sudo nano /etc/systemd/system/woocommerce-dashboard.service
   # Add content based on INSTALLATION.md
   sudo systemctl enable woocommerce-dashboard.service
   sudo systemctl start woocommerce-dashboard.service
   ```

8. **Configure Nginx**:
   ```bash
   sudo nano /etc/nginx/sites-available/woocommerce-dashboard
   # Add content based on INSTALLATION.md
   sudo ln -s /etc/nginx/sites-available/woocommerce-dashboard /etc/nginx/sites-enabled/
   sudo nginx -t
   sudo systemctl restart nginx
   ```

## Verifying Installation

Check if the service is running:
```bash
sudo systemctl status woocommerce-dashboard.service
```

View logs if there are issues:
```bash
sudo journalctl -u woocommerce-dashboard.service
```

## Supported Features

- Daily, weekly, and monthly sales metrics
- Product performance analysis
- Stock quantity monitoring
- Customer insights
- Payment method analytics
- Customer acquisition cost analysis
- Export functionality

## Troubleshooting

- **Dashboard not loading**: Check service status and logs
- **API connection issues**: Verify credentials in .env file
- **Permission problems**: Check ownership of files and directories
- **Nginx issues**: Check configuration and restart if needed

For more detailed instructions, refer to the full [INSTALLATION.md](INSTALLATION.md) guide.