# WooCommerce Dashboard Installation Guide
## Self-hosted Ubuntu Server Installation

This guide provides step-by-step instructions for installing and running the WooCommerce Dashboard on a self-hosted Ubuntu server.

### Prerequisites

- Ubuntu 20.04 LTS or newer
- Root or sudo access
- Internet connectivity
- Your WooCommerce API credentials (key and secret)
- Domain name (optional, for HTTPS configuration)

### 1. System Updates and Prerequisites

Connect to your Ubuntu server via SSH and update the system:

```bash
sudo apt update
sudo apt upgrade -y
sudo apt install -y python3-pip python3-dev python3-venv build-essential libssl-dev libffi-dev git nginx
```

### 2. Creating a User Account (Optional but Recommended for Security)

```bash
sudo adduser woo-dashboard
sudo usermod -aG sudo woo-dashboard
sudo su - woo-dashboard
```

### 3. Clone the Repository

```bash
git clone https://github.com/YOUR-USERNAME/woocommerce-dashboard.git
cd woocommerce-dashboard
```

Alternatively, you can manually upload the files using SFTP or create them directly.

### 4. Setting Up the Python Environment

```bash
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

If you don't have a requirements.txt file, create one with the following content:

```
google-ads>=16.0.0
google-analytics-data>=0.16.0
google-api-python-client>=2.84.0
google-auth-httplib2>=0.1.0
google-auth-oauthlib>=1.0.0
numpy>=1.24.3
openai>=0.27.7
openpyxl>=3.1.2
pandas>=2.0.1
plotly>=5.14.1
pytz>=2023.3
reportlab>=4.0.0
streamlit>=1.22.0
trafilatura>=1.5.0
twilio>=8.1.0
WooCommerce>=3.0.0
```

### 5. Create Configuration Directory

```bash
mkdir -p ~/.streamlit
```

Create a configuration file:

```bash
nano ~/.streamlit/config.toml
```

Add the following content:

```toml
[server]
headless = true
address = "0.0.0.0"
port = 8501
enableCORS = false
enableXsrfProtection = true
```

### 6. Set Up Environment Variables 

Create an environment variables file:

```bash
nano .env
```

Add your WooCommerce and other API credentials:

```
# WooCommerce API credentials
WOOCOMMERCE_URL=https://your-store.com
WOOCOMMERCE_KEY=your_consumer_key
WOOCOMMERCE_SECRET=your_consumer_secret

# Google Analytics credentials (if using)
GOOGLE_ANALYTICS_PROPERTY_ID=your_property_id

# Google Ads credentials (if using)
GOOGLE_ADS_DEVELOPER_TOKEN=your_developer_token
GOOGLE_ADS_CLIENT_ID=your_client_id
GOOGLE_ADS_CLIENT_SECRET=your_client_secret
GOOGLE_ADS_REFRESH_TOKEN=your_refresh_token
GOOGLE_ADS_CUSTOMER_ID=your_customer_id

# Other credentials if needed
```

Create a script to load these environment variables:

```bash
nano load_env.sh
```

Add the following content:

```bash
#!/bin/bash
set -a
source .env
set +a
```

Make the script executable:

```bash
chmod +x load_env.sh
```

### 7. Set Up Systemd Service (for automatic startup)

Create a systemd service file:

```bash
sudo nano /etc/systemd/system/woocommerce-dashboard.service
```

Add the following content (adjust paths according to your setup):

```
[Unit]
Description=WooCommerce Dashboard Streamlit App
After=network.target

[Service]
User=woo-dashboard
WorkingDirectory=/home/woo-dashboard/woocommerce-dashboard
ExecStart=/bin/bash -c 'source /home/woo-dashboard/woocommerce-dashboard/venv/bin/activate && source /home/woo-dashboard/woocommerce-dashboard/load_env.sh && python -m streamlit run woocommerce_dashboard.py'
Restart=always
RestartSec=10
StandardOutput=syslog
StandardError=syslog
SyslogIdentifier=woocommerce-dashboard

[Install]
WantedBy=multi-user.target
```

### 8. Configure Nginx as a Reverse Proxy

Create an Nginx configuration file:

```bash
sudo nano /etc/nginx/sites-available/woocommerce-dashboard
```

Add the following content (adjust domain name as needed):

```nginx
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;  # Replace with your domain or server IP

    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_read_timeout 86400;
    }
}
```

Create a symbolic link and test the configuration:

```bash
sudo ln -s /etc/nginx/sites-available/woocommerce-dashboard /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 9. Enable and Start the Service

```bash
sudo systemctl enable woocommerce-dashboard.service
sudo systemctl start woocommerce-dashboard.service
```

### 10. Check Status and Logs

```bash
sudo systemctl status woocommerce-dashboard.service
sudo journalctl -u woocommerce-dashboard.service
```

### 11. Set Up SSL with Let's Encrypt (Optional but Recommended)

```bash
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com -d www.your-domain.com
```

### 12. Firewall Configuration (Optional)

If you're using UFW firewall:

```bash
sudo ufw allow 'Nginx Full'
sudo ufw status
```

### Troubleshooting

#### Common Issues:

1. **Application Doesn't Start**
   - Check logs: `sudo journalctl -u woocommerce-dashboard.service`
   - Verify environment variables are loaded correctly
   - Ensure Python dependencies are installed correctly

2. **Can't Access Dashboard**
   - Check if Streamlit is running: `ps aux | grep streamlit`
   - Verify Nginx configuration and restart if needed
   - Check firewall settings

3. **API Connection Issues**
   - Verify your API credentials in the .env file
   - Check network connectivity to WooCommerce site
   - Look for errors in application logs

#### Updating the Application:

To update the application code:

```bash
cd /home/woo-dashboard/woocommerce-dashboard
git pull  # If using Git
source venv/bin/activate
pip install -r requirements.txt  # If dependencies changed
sudo systemctl restart woocommerce-dashboard.service
```

### Security Recommendations

1. **Secure Access**: Consider setting up basic authentication in Nginx
2. **Regular Updates**: Keep Ubuntu, Python, and all packages updated
3. **Firewall**: Configure UFW to only allow necessary ports
4. **Backup**: Regularly backup your configuration and credentials
5. **Monitoring**: Set up monitoring to alert you of any downtime

### System Requirements

The WooCommerce Dashboard has been optimized for performance, but requirements depend on your store size and traffic:

- **Minimum**: 1 CPU core, 2GB RAM, 10GB storage
- **Recommended**: 2 CPU cores, 4GB RAM, 20GB storage
- **Large stores**: 4+ CPU cores, 8GB+ RAM, 40GB+ storage

### Performance Optimization

For larger WooCommerce stores, consider:

1. Increasing server resources (CPU/RAM)
2. Setting up a caching mechanism for API responses
3. Scheduling background data refreshes during off-peak hours
4. Monitoring memory usage and adjusting as needed

### Regular Maintenance

1. Check logs regularly: `sudo journalctl -u woocommerce-dashboard.service`
2. Update system packages: `sudo apt update && sudo apt upgrade`
3. Update Python packages: `pip install --upgrade -r requirements.txt`
4. Renew SSL certificates (Let's Encrypt auto-renews, but verify)
5. Monitor disk space: `df -h`