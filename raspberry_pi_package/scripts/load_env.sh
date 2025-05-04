#!/bin/bash
# WooCommerce Dashboard - Environment Variables Loader
# This script loads environment variables from the .env file

# Check if .env file exists
if [ -f .env ]; then
    echo "Loading environment variables from .env file..."
    set -a
    source .env
    set +a
else
    echo "WARNING: .env file not found."
    echo "Please create a .env file with your WooCommerce credentials."
    echo "You can copy .env.example to .env and fill in your details."
    exit 1
fi

# Display loaded variables (without showing secret values)
echo "Environment variables loaded:"
echo "WOOCOMMERCE_URL: ${WOOCOMMERCE_URL:-Not set}"
echo "WOOCOMMERCE_KEY: ${WOOCOMMERCE_KEY:0:3}...${WOOCOMMERCE_KEY: -3} (obscured for security)"
echo "WOOCOMMERCE_SECRET: ${WOOCOMMERCE_SECRET:0:3}...${WOOCOMMERCE_SECRET: -3} (obscured for security)"

# Check for optional Google Analytics variables
if [ -n "$GOOGLE_ANALYTICS_PROPERTY_ID" ]; then
    echo "GOOGLE_ANALYTICS_PROPERTY_ID: ${GOOGLE_ANALYTICS_PROPERTY_ID:0:3}...${GOOGLE_ANALYTICS_PROPERTY_ID: -3} (obscured for security)"
else
    echo "GOOGLE_ANALYTICS_PROPERTY_ID: Not set (optional)"
fi

if [ -n "$GOOGLE_ANALYTICS_CREDENTIALS" ]; then
    echo "GOOGLE_ANALYTICS_CREDENTIALS: ${GOOGLE_ANALYTICS_CREDENTIALS} (file path)"
else
    echo "GOOGLE_ANALYTICS_CREDENTIALS: Not set (optional)"
fi

# Check for optional Google Ads variables
if [ -n "$GOOGLE_ADS_CUSTOMER_ID" ]; then
    echo "GOOGLE_ADS_CUSTOMER_ID: Set (obscured for security)"
    echo "GOOGLE_ADS_DEVELOPER_TOKEN: Set (obscured for security)"
    echo "GOOGLE_ADS_CLIENT_ID: Set (obscured for security)"
    echo "GOOGLE_ADS_CLIENT_SECRET: Set (obscured for security)"
    echo "GOOGLE_ADS_REFRESH_TOKEN: Set (obscured for security)"
else
    echo "Google Ads credentials: Not set (optional)"
fi

echo "Environment variables loaded successfully."