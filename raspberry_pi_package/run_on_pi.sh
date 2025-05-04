#!/bin/bash
# WooCommerce Dashboard - Raspberry Pi Runner Script
# This script starts the dashboard on port 3000 with optimized settings

# Exit on error
set -e

# Display header
echo "-------------------------------------"
echo "  WooCommerce Dashboard for Raspberry Pi  "
echo "-------------------------------------"

# Check if we're in a Python virtual environment
if [ -z "$VIRTUAL_ENV" ]; then
    # Try to activate the virtual environment if it exists
    if [ -d "venv" ]; then
        echo "Activating virtual environment..."
        source venv/bin/activate
    else
        echo "WARNING: No virtual environment detected."
        echo "It's recommended to run inside a virtual environment."
        echo "Set up with: python3 -m venv venv && source venv/bin/activate"
        echo ""
        read -p "Continue anyway? (y/n): " continue_response
        if [[ ! "$continue_response" =~ ^[Yy]$ ]]; then
            echo "Exiting. Please set up a virtual environment first."
            exit 1
        fi
    fi
fi

# Load environment variables
if [ -f "load_env.sh" ]; then
    echo "Loading environment variables..."
    source ./load_env.sh
elif [ -f "scripts/load_env.sh" ]; then
    echo "Loading environment variables from scripts directory..."
    source ./scripts/load_env.sh
else
    echo "WARNING: Could not find load_env.sh"
    echo "Make sure your environment variables are loaded"
    
    # Check if .env file exists
    if [ -f ".env" ]; then
        echo "Found .env file, loading directly..."
        set -a
        source .env
        set +a
    else
        echo "ERROR: No .env file found!"
        echo "Please create a .env file with your WooCommerce credentials."
        exit 1
    fi
fi

# Apply Raspberry Pi optimizations
echo "Applying Raspberry Pi performance optimizations..."
export STREAMLIT_SERVER_PORT=3000
export STREAMLIT_SERVER_ADDRESS="0.0.0.0"
export STREAMLIT_SERVER_HEADLESS=true
export STREAMLIT_SERVER_MAX_UPLOAD_SIZE=5
export STREAMLIT_BROWSER_GATHER_USAGE_STATS=false
export PYTHONOPTIMIZE=2

# Get IP address for easy access
IP_ADDRESS=$(hostname -I | awk '{print $1}')

# Display access info
echo ""
echo "======================================"
echo "Starting WooCommerce Dashboard on port 3000"
echo "Access your dashboard at: http://$IP_ADDRESS:3000"
echo "Press Ctrl+C to stop"
echo "======================================"
echo ""

# Check if streamlit is installed
if ! command -v streamlit &> /dev/null; then
    echo "ERROR: Streamlit not found!"
    echo "Install with: pip install streamlit"
    exit 1
fi

# Run the streamlit application
streamlit run woocommerce_dashboard.py --server.port 3000