#!/bin/bash
# Raspberry Pi Setup Script for WooCommerce Dashboard
# This script automates the setup of the WooCommerce Dashboard on a Raspberry Pi

# Text formatting
BOLD='\033[1m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BOLD}WooCommerce Dashboard - Raspberry Pi Setup Script${NC}"
echo "-------------------------------------------------------"
echo -e "${YELLOW}This script will set up the WooCommerce Dashboard to run on port 3000.${NC}"
echo

# Check if running on a Raspberry Pi
if [ ! -f /proc/device-tree/model ] || ! grep -q "Raspberry Pi" /proc/device-tree/model; then
    echo -e "${YELLOW}Warning: This device doesn't appear to be a Raspberry Pi.${NC}"
    echo "This script is optimized for Raspberry Pi devices."
    read -p "Continue anyway? (y/n): " CONTINUE
    if [[ ! "$CONTINUE" =~ ^[Yy]$ ]]; then
        echo "Setup cancelled."
        exit 0
    fi
fi

# Create application directory
APP_DIR="$HOME/woocommerce-dashboard"
echo -e "\n${BOLD}Setting up application directory${NC}"
mkdir -p "$APP_DIR"
cd "$APP_DIR"

# Update system and install required packages
echo -e "\n${BOLD}Updating system and installing dependencies${NC}"
echo "This may take some time..."
sudo apt update
sudo apt upgrade -y
sudo apt install -y python3-pip python3-venv git libatlas-base-dev

# Set up Python environment
echo -e "\n${BOLD}Setting up Python virtual environment${NC}"
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip

echo -e "\n${BOLD}Installing Python packages${NC}"
echo "For better performance, we'll install some packages with optimizations for Raspberry Pi."
echo "This may take 10-15 minutes..."

# Install numpy and pandas with optimizations for ARM
pip install numpy --only-binary :all:
pip install pandas --only-binary :all:

# Create a requirements file
cat > requirements.txt << EOF
streamlit
plotly
pytz
woocommerce
google-ads
google-analytics-data
google-api-python-client
google-auth-httplib2
google-auth-oauthlib
openpyxl
reportlab
EOF

pip install -r requirements.txt

# Set up environment file template
echo -e "\n${BOLD}Setting up environment configuration${NC}"
cat > .env << EOF
# WooCommerce Dashboard - Environment Configuration

# WooCommerce API credentials (required)
WOOCOMMERCE_URL=https://your-store.com
WOOCOMMERCE_KEY=your_consumer_key
WOOCOMMERCE_SECRET=your_consumer_secret

# Google Analytics credentials (optional)
GOOGLE_ANALYTICS_PROPERTY_ID=your_property_id

# Google Ads credentials (optional)
GOOGLE_ADS_DEVELOPER_TOKEN=your_developer_token
GOOGLE_ADS_CLIENT_ID=your_client_id
GOOGLE_ADS_CLIENT_SECRET=your_client_secret
GOOGLE_ADS_REFRESH_TOKEN=your_refresh_token
GOOGLE_ADS_CUSTOMER_ID=your_customer_id
EOF

# Create load_env.sh script
cat > load_env.sh << EOF
#!/bin/bash
# Helper script to load environment variables
set -a
source .env
set +a
EOF

chmod +x load_env.sh

# Create run script
cat > run_dashboard.sh << EOF
#!/bin/bash
# Run script for WooCommerce Dashboard on Raspberry Pi
cd "$APP_DIR"
source venv/bin/activate
source ./load_env.sh

# Apply Raspberry Pi optimizations
export STREAMLIT_SERVER_PORT=3000
export STREAMLIT_SERVER_ADDRESS="0.0.0.0"
export STREAMLIT_SERVER_HEADLESS=true
export STREAMLIT_SERVER_MAX_UPLOAD_SIZE=5
export STREAMLIT_BROWSER_GATHER_USAGE_STATS=false
export PYTHONOPTIMIZE=2

# Start the dashboard
echo "Starting WooCommerce Dashboard on port 3000..."
echo "Access the dashboard at http://\$(hostname -I | awk '{print \$1}'):3000"
echo "Press Ctrl+C to stop."

# Run the streamlit application
streamlit run woocommerce_dashboard.py
EOF

chmod +x run_dashboard.sh

# Set up Streamlit configuration
mkdir -p ~/.streamlit
cat > ~/.streamlit/config.toml << EOF
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
EOF

# Set up systemd service file
echo -e "\n${BOLD}Setting up systemd service${NC}"
cat > woocommerce-dashboard.service << EOF
[Unit]
Description=WooCommerce Dashboard Streamlit App
After=network.target

[Service]
User=$USER
WorkingDirectory=$APP_DIR
ExecStart=/bin/bash -c 'source $APP_DIR/venv/bin/activate && source $APP_DIR/load_env.sh && streamlit run $APP_DIR/woocommerce_dashboard.py --server.port 3000'
Restart=always
RestartSec=10
StandardOutput=syslog
StandardError=syslog
SyslogIdentifier=woocommerce-dashboard

[Install]
WantedBy=multi-user.target
EOF

# Optional: Set up swap file for better performance
echo -e "\n${BOLD}Setting up swap file for better performance${NC}"
read -p "Do you want to add a 2GB swap file for better performance? (y/n, default: y): " SETUP_SWAP
SETUP_SWAP=${SETUP_SWAP:-y}

if [[ "$SETUP_SWAP" =~ ^[Yy]$ ]]; then
    if [ -f /swapfile ]; then
        echo "Swap file already exists. Skipping."
    else
        echo "Creating 2GB swap file..."
        sudo fallocate -l 2G /swapfile
        sudo chmod 600 /swapfile
        sudo mkswap /swapfile
        sudo swapon /swapfile
        echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
        echo "Swap file created and enabled."
    fi
fi

# Create download instructions
echo -e "\n${BOLD}Creating download instructions${NC}"
cat > DOWNLOAD_INSTRUCTIONS.md << EOF
# WooCommerce Dashboard Files Download

To complete the setup of your WooCommerce Dashboard on Raspberry Pi, you need to download the following files:

1. **woocommerce_dashboard.py** - The main application file
2. **utils/** - Directory containing utility modules

Download these files from the source repository and place them in:
$APP_DIR

After downloading the files, edit the .env file to add your WooCommerce API credentials:
\`\`\`
nano $APP_DIR/.env
\`\`\`

Then run the dashboard with:
\`\`\`
$APP_DIR/run_dashboard.sh
\`\`\`

To set up as a system service:
\`\`\`
sudo cp $APP_DIR/woocommerce-dashboard.service /etc/systemd/system/
sudo systemctl enable woocommerce-dashboard.service
sudo systemctl start woocommerce-dashboard.service
\`\`\`
EOF

# Final steps and information
echo -e "\n${GREEN}Setup completed!${NC}"
echo -e "\n${BOLD}Next Steps:${NC}"
echo "1. Download the application files (see DOWNLOAD_INSTRUCTIONS.md)"
echo "2. Edit the .env file with your WooCommerce API credentials:"
echo "   nano $APP_DIR/.env"
echo "3. Run the dashboard:"
echo "   $APP_DIR/run_dashboard.sh"
echo
echo -e "${BOLD}To set up as a system service:${NC}"
echo "sudo cp $APP_DIR/woocommerce-dashboard.service /etc/systemd/system/"
echo "sudo systemctl enable woocommerce-dashboard.service"
echo "sudo systemctl start woocommerce-dashboard.service"
echo
echo -e "${BOLD}Access the dashboard:${NC}"
echo "http://$(hostname -I | awk '{print $1}'):3000"
echo
echo -e "${YELLOW}Remember to edit the .env file with your actual API credentials.${NC}"