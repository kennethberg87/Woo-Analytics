#!/bin/bash
# WooCommerce Dashboard - Raspberry Pi Setup Script
# This script installs all dependencies and sets up the environment

# Exit on error
set -e

# Display header
echo "-------------------------------------"
echo "  WooCommerce Dashboard Setup  "
echo "  For Raspberry Pi              "
echo "-------------------------------------"

INSTALL_DIR="$HOME/woocommerce-dashboard"

# Check if running as root (not recommended)
if [ "$EUID" -eq 0 ]; then
  echo "WARNING: Running as root is not recommended."
  echo "It's better to run as a normal user."
  read -p "Continue anyway? (y/n): " continue_response
  if [[ ! "$continue_response" =~ ^[Yy]$ ]]; then
    echo "Exiting. Please run as a normal user."
    exit 1
  fi
fi

# Update system packages
echo "Updating system packages..."
sudo apt-get update

# Install required system dependencies
echo "Installing system dependencies..."
sudo apt-get install -y python3-venv python3-pip python3-dev libatlas-base-dev libopenjp2-7 libtiff5 libxml2-dev libxslt1-dev

# Create installation directory
echo "Creating installation directory at $INSTALL_DIR..."
mkdir -p "$INSTALL_DIR"

# Copy files to installation directory
echo "Copying files to installation directory..."
cp -r * "$INSTALL_DIR/"
cd "$INSTALL_DIR"

# Create virtual environment
echo "Creating Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Optimize pip
echo "Optimizing pip..."
python -m pip install --upgrade pip setuptools wheel

# Install Python dependencies
echo "Installing Python dependencies (this may take some time)..."
# Install packages that need to be compiled separately with optimizations for Raspberry Pi
pip install --upgrade numpy
pip install --upgrade pandas

# Install the rest of the requirements
pip install streamlit>=1.22.0 woocommerce plotly reportlab openpyxl google-analytics-data google-api-python-client google-auth-httplib2 google-auth-oauthlib twilio

# Create the .env.example file
echo "Creating environment variables template..."
cat > .env.example << 'EOF'
# WooCommerce Dashboard Environment Variables
# Copy this file to .env and replace with your actual values

# WooCommerce API credentials (required)
WOOCOMMERCE_URL=https://your-store.com
WOOCOMMERCE_KEY=your_woocommerce_key
WOOCOMMERCE_SECRET=your_woocommerce_secret

# Google Analytics credentials (optional)
GOOGLE_ANALYTICS_PROPERTY_ID=your_property_id
GOOGLE_ANALYTICS_CREDENTIALS=path_to_credentials.json

# Google Ads credentials (optional)
GOOGLE_ADS_CUSTOMER_ID=your_customer_id
GOOGLE_ADS_DEVELOPER_TOKEN=your_developer_token
GOOGLE_ADS_CLIENT_ID=your_client_id
GOOGLE_ADS_CLIENT_SECRET=your_client_secret
GOOGLE_ADS_REFRESH_TOKEN=your_refresh_token
EOF

# Create load_env.sh script
echo "Creating environment loader script..."
cat > load_env.sh << 'EOF'
#!/bin/bash
# Load environment variables from .env file

# Check if .env file exists
if [ -f .env ]; then
    echo "Loading environment variables from .env file..."
    set -a
    source .env
    set +a
else
    echo "WARNING: .env file not found."
    echo "Please create a .env file with your credentials."
    echo "You can copy .env.example to .env and fill in your details."
fi
EOF

# Make scripts executable
chmod +x load_env.sh
chmod +x run_on_pi.sh

# Create systemd service file for auto-start
echo "Creating systemd service file..."
cat > woocommerce-dashboard.service << 'EOF'
[Unit]
Description=WooCommerce Dashboard
After=network.target

[Service]
Type=simple
User=REPLACE_WITH_YOUR_USERNAME
WorkingDirectory=REPLACE_WITH_INSTALL_DIR
Environment=PATH=REPLACE_WITH_INSTALL_DIR/venv/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
ExecStart=REPLACE_WITH_INSTALL_DIR/venv/bin/streamlit run woocommerce_dashboard.py --server.port 3000
Restart=on-failure
RestartSec=5s

[Install]
WantedBy=multi-user.target
EOF

# Update the service file with correct paths
sed -i "s|REPLACE_WITH_YOUR_USERNAME|$USER|g" woocommerce-dashboard.service
sed -i "s|REPLACE_WITH_INSTALL_DIR|$INSTALL_DIR|g" woocommerce-dashboard.service

# Create installation instructions
echo "Creating post-installation instructions..."
cat > NEXT_STEPS.txt << EOF
========================================
WooCommerce Dashboard - Next Steps
========================================

1. Create your environment file:
   cp .env.example .env
   nano .env  # Edit with your actual credentials

2. Test the dashboard:
   ./run_on_pi.sh

3. To set up automatic startup (optional):
   sudo cp $INSTALL_DIR/woocommerce-dashboard.service /etc/systemd/system/
   sudo systemctl daemon-reload
   sudo systemctl enable woocommerce-dashboard.service
   sudo systemctl start woocommerce-dashboard.service

4. Access your dashboard:
   http://$(hostname -I | awk '{print $1}'):3000

For troubleshooting, see RASPBERRY-PI-SETUP.md
EOF

# Success message
echo ""
echo "Installation completed successfully!"
echo ""
echo "Next steps:"
echo "1. Configure your credentials: cp .env.example .env && nano .env"
echo "2. Run the dashboard: ./run_on_pi.sh"
echo ""
echo "For detailed instructions, see:"
echo "- $INSTALL_DIR/NEXT_STEPS.txt"
echo "- $INSTALL_DIR/RASPBERRY-PI-SETUP.md"
echo ""
echo "To access your dashboard, go to:"
echo "http://$(hostname -I | awk '{print $1}'):3000"