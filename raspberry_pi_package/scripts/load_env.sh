#!/bin/bash
# Helper script to load environment variables for the WooCommerce Dashboard
# Place this file in the same directory as your .env file

set -a  # automatically export all variables
source .env
set +a  # stop automatically exporting

echo "Environment variables loaded successfully!"
echo "WOOCOMMERCE_URL is set to: ${WOOCOMMERCE_URL}"
echo "WooCommerce credentials are loaded. API keys are hidden for security."