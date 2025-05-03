#!/bin/bash
# WooCommerce Dashboard Deployment Script
# This script automates the installation of the WooCommerce Dashboard on Ubuntu Server

# Exit on any error
set -e

# Text formatting
BOLD='\033[1m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BOLD}WooCommerce Dashboard - Deployment Script${NC}"
echo "---------------------------------------"
echo -e "${YELLOW}This script will install the WooCommerce Dashboard on your Ubuntu server.${NC}"
echo

# Check for root or sudo
if [ "$EUID" -ne 0 ]; then
  echo -e "${RED}Please run as root or with sudo${NC}"
  exit 1
fi

# Get installation details
read -p "Enter domain name (or leave blank for IP only setup): " DOMAIN_NAME
read -p "Enter port for Streamlit (default: 8501): " STREAMLIT_PORT
STREAMLIT_PORT=${STREAMLIT_PORT:-8501}

# User account setup
echo -e "\n${BOLD}Setting up user account${NC}"
read -p "Create dedicated user for the application? (y/n, default: y): " CREATE_USER
CREATE_USER=${CREATE_USER:-y}

if [[ "$CREATE_USER" =~ ^[Yy]$ ]]; then
  read -p "Enter username (default: woo-dashboard): " USERNAME
  USERNAME=${USERNAME:-woo-dashboard}
  if id "$USERNAME" &>/dev/null; then
    echo -e "${YELLOW}User $USERNAME already exists${NC}"
  else
    echo "Creating user $USERNAME..."
    adduser --gecos "" $USERNAME
    usermod -aG sudo $USERNAME
    echo -e "${GREEN}User $USERNAME created successfully${NC}"
  fi
  APP_DIR="/home/$USERNAME/woocommerce-dashboard"
  mkdir -p "$APP_DIR"
  chown -R $USERNAME:$USERNAME "$APP_DIR"
else
  APP_DIR="$(pwd)/woocommerce-dashboard"
  mkdir -p "$APP_DIR"
fi

# Update system
echo -e "\n${BOLD}Updating system and installing dependencies${NC}"
apt update
apt upgrade -y
apt install -y python3-pip python3-dev python3-venv build-essential libssl-dev libffi-dev git nginx

# Set up Python environment
echo -e "\n${BOLD}Setting up Python environment${NC}"
if [[ "$CREATE_USER" =~ ^[Yy]$ ]]; then
  su - $USERNAME -c "cd $APP_DIR && python3 -m venv venv"
  su - $USERNAME -c "cd $APP_DIR && source venv/bin/activate && pip install --upgrade pip"
else
  cd "$APP_DIR"
  python3 -m venv venv
  source venv/bin/activate
  pip install --upgrade pip
fi

# Create requirements file
echo -e "\n${BOLD}Creating requirements file${NC}"
cat > "$APP_DIR/requirements.txt" << EOF
google-ads>=16.0.0
google-analytics-data>=0.16.0
google-api-python-client>=2.84.0
google-auth-httplib2>=0.1.0
google-auth-oauthlib>=1.0.0
numpy>=1.24.3
pandas>=2.0.1
plotly>=5.14.1
pytz>=2023.3
reportlab>=4.0.0
streamlit>=1.22.0
trafilatura>=1.5.0
twilio>=8.1.0
WooCommerce>=3.0.0
EOF

# Install Python requirements
echo -e "\n${BOLD}Installing Python requirements${NC}"
if [[ "$CREATE_USER" =~ ^[Yy]$ ]]; then
  su - $USERNAME -c "cd $APP_DIR && source venv/bin/activate && pip install -r requirements.txt"
else
  cd "$APP_DIR"
  source venv/bin/activate
  pip install -r requirements.txt
fi

# Create Streamlit config directory
echo -e "\n${BOLD}Setting up Streamlit configuration${NC}"
if [[ "$CREATE_USER" =~ ^[Yy]$ ]]; then
  su - $USERNAME -c "mkdir -p /home/$USERNAME/.streamlit"
  cat > "/home/$USERNAME/.streamlit/config.toml" << EOF
[server]
headless = true
address = "0.0.0.0"
port = $STREAMLIT_PORT
enableCORS = false
enableXsrfProtection = true
EOF
  chown -R $USERNAME:$USERNAME "/home/$USERNAME/.streamlit"
else
  mkdir -p "$APP_DIR/.streamlit"
  cat > "$APP_DIR/.streamlit/config.toml" << EOF
[server]
headless = true
address = "0.0.0.0"
port = $STREAMLIT_PORT
enableCORS = false
enableXsrfProtection = true
EOF
fi

# Configure environment variables
echo -e "\n${BOLD}Setting up environment variables${NC}"
cat > "$APP_DIR/.env" << EOF
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
EOF

cat > "$APP_DIR/load_env.sh" << EOF
#!/bin/bash
set -a
source .env
set +a
EOF
chmod +x "$APP_DIR/load_env.sh"

echo -e "${YELLOW}Please edit $APP_DIR/.env with your actual API credentials${NC}"

# Set up systemd service
echo -e "\n${BOLD}Setting up systemd service${NC}"
if [[ "$CREATE_USER" =~ ^[Yy]$ ]]; then
  SERVICE_PATH="/etc/systemd/system/woocommerce-dashboard.service"
  cat > "$SERVICE_PATH" << EOF
[Unit]
Description=WooCommerce Dashboard Streamlit App
After=network.target

[Service]
User=$USERNAME
WorkingDirectory=$APP_DIR
ExecStart=/bin/bash -c 'source $APP_DIR/venv/bin/activate && source $APP_DIR/load_env.sh && python -m streamlit run $APP_DIR/woocommerce_dashboard.py'
Restart=always
RestartSec=10
StandardOutput=syslog
StandardError=syslog
SyslogIdentifier=woocommerce-dashboard

[Install]
WantedBy=multi-user.target
EOF
else
  SERVICE_PATH="/etc/systemd/system/woocommerce-dashboard.service"
  cat > "$SERVICE_PATH" << EOF
[Unit]
Description=WooCommerce Dashboard Streamlit App
After=network.target

[Service]
WorkingDirectory=$APP_DIR
ExecStart=/bin/bash -c 'source $APP_DIR/venv/bin/activate && source $APP_DIR/load_env.sh && python -m streamlit run $APP_DIR/woocommerce_dashboard.py'
Restart=always
RestartSec=10
StandardOutput=syslog
StandardError=syslog
SyslogIdentifier=woocommerce-dashboard

[Install]
WantedBy=multi-user.target
EOF
fi

# Set up Nginx
echo -e "\n${BOLD}Setting up Nginx as reverse proxy${NC}"
if [ -n "$DOMAIN_NAME" ]; then
  NGINX_CONF="/etc/nginx/sites-available/woocommerce-dashboard"
  cat > "$NGINX_CONF" << EOF
server {
    listen 80;
    server_name $DOMAIN_NAME www.$DOMAIN_NAME;

    location / {
        proxy_pass http://localhost:$STREAMLIT_PORT;
        proxy_http_version 1.1;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_read_timeout 86400;
    }
}
EOF
  ln -sf "$NGINX_CONF" "/etc/nginx/sites-enabled/"
  nginx -t && systemctl restart nginx
  
  # Ask about SSL
  read -p "Set up SSL with Let's Encrypt? (y/n, default: y): " SETUP_SSL
  SETUP_SSL=${SETUP_SSL:-y}
  if [[ "$SETUP_SSL" =~ ^[Yy]$ ]]; then
    apt install -y certbot python3-certbot-nginx
    certbot --nginx -d $DOMAIN_NAME -d www.$DOMAIN_NAME
  fi
else
  NGINX_CONF="/etc/nginx/sites-available/woocommerce-dashboard"
  cat > "$NGINX_CONF" << EOF
server {
    listen 80;
    server_name _;

    location / {
        proxy_pass http://localhost:$STREAMLIT_PORT;
        proxy_http_version 1.1;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_read_timeout 86400;
    }
}
EOF
  ln -sf "$NGINX_CONF" "/etc/nginx/sites-enabled/"
  nginx -t && systemctl restart nginx
fi

# Configure UFW if installed
if command -v ufw &> /dev/null; then
  echo -e "\n${BOLD}Configuring firewall${NC}"
  ufw allow 'Nginx Full'
  ufw status
fi

# Setting up permissions
if [[ "$CREATE_USER" =~ ^[Yy]$ ]]; then
  chown -R $USERNAME:$USERNAME "$APP_DIR"
fi

# Install application files
echo -e "\n${BOLD}Setting up application files${NC}"
echo -e "${YELLOW}You now need to copy your WooCommerce Dashboard files into $APP_DIR${NC}"
echo -e "${YELLOW}Make sure to include woocommerce_dashboard.py and the utils/ directory${NC}"

# Final steps
echo -e "\n${BOLD}Final steps${NC}"
echo "1. Copy your WooCommerce Dashboard files to $APP_DIR"
echo "2. Edit your API credentials in $APP_DIR/.env"
echo "3. Start the service with: systemctl enable --now woocommerce-dashboard.service"
echo "4. Access your dashboard at: ${DOMAIN_NAME:-http://your-server-ip}"

echo -e "\n${GREEN}Installation preparation completed!${NC}"
echo -e "After copying your application files, run the following commands:"
echo -e "${YELLOW}systemctl enable woocommerce-dashboard.service${NC}"
echo -e "${YELLOW}systemctl start woocommerce-dashboard.service${NC}"
echo -e "${YELLOW}systemctl status woocommerce-dashboard.service${NC}"