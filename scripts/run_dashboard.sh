#!/bin/bash
# Run script for WooCommerce Dashboard on Raspberry Pi
# This script starts the dashboard on port 3000

# Exit on error
set -e

# Navigate to application directory - change this to match your setup
APPLICATION_DIR="$HOME/woocommerce-dashboard"
cd "$APPLICATION_DIR"

# Activate Python virtual environment
if [ -d "venv" ]; then
    echo "Activating virtual environment..."
    source venv/bin/activate
else
    echo "Error: Virtual environment not found!"
    echo "Please run setup script first."
    exit 1
fi

# Load environment variables
if [ -f "load_env.sh" ]; then
    echo "Loading environment variables..."
    source ./load_env.sh
else
    echo "Warning: load_env.sh not found. Using any existing environment variables."
fi

# Apply Raspberry Pi optimizations
echo "Applying Raspberry Pi performance optimizations..."
export STREAMLIT_SERVER_PORT=3000
export STREAMLIT_SERVER_ADDRESS="0.0.0.0"
export STREAMLIT_SERVER_HEADLESS=true
export STREAMLIT_SERVER_MAX_UPLOAD_SIZE=5
export STREAMLIT_BROWSER_GATHER_USAGE_STATS=false
export PYTHONOPTIMIZE=2

# Start the dashboard
echo "Starting WooCommerce Dashboard on port 3000..."
echo "Access the dashboard at http://$(hostname -I | awk '{print $1}'):3000"
echo "Press Ctrl+C to stop."

# Run the streamlit application
streamlit run woocommerce_dashboard.py