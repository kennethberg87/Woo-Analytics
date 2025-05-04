# WooCommerce Dashboard - Local Setup Guide

This guide will help you set up and run the WooCommerce Dashboard on your local computer. Follow these steps for Windows, macOS, or Linux.

## Prerequisites

- Python 3.9+ installed on your system
- Basic familiarity with command line/terminal
- Your WooCommerce API credentials (key and secret)

## Setup Instructions

### Step 1: Download the Application Files

1. Download the zipped application files (`woocommerce-dashboard.zip`)
2. Extract the files to a location on your computer (e.g., `Documents/woocommerce-dashboard`)

### Step 2: Set Up Python Environment

#### Windows

Open Command Prompt or PowerShell and navigate to the extracted folder:

```powershell
cd \path\to\woocommerce-dashboard
```

Create and activate a virtual environment:

```powershell
python -m venv venv
venv\Scripts\activate
```

Install required packages:

```powershell
pip install -r requirements.txt
```

#### macOS/Linux

Open Terminal and navigate to the extracted folder:

```bash
cd /path/to/woocommerce-dashboard
```

Create and activate a virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate
```

Install required packages:

```bash
pip install -r requirements.txt
```

### Step 3: Configure Environment Variables

Create a `.env` file in the application directory with your WooCommerce credentials:

#### Windows (Using Notepad)

Create a file named `.env` (make sure it's not saved as `.env.txt`) with the following content:

```
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
```

#### macOS/Linux

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

### Step 4: Configure Streamlit (Optional)

Create a Streamlit configuration directory:

#### Windows

```powershell
mkdir .streamlit
echo "[server]`nheadless = false`nport = 8501" | Out-File -Encoding utf8 .streamlit/config.toml
```

#### macOS/Linux

```bash
mkdir -p .streamlit
echo "[server]
headless = false
port = 8501" > .streamlit/config.toml
```

### Step 5: Run the Application

#### Windows

```powershell
# Make sure your virtual environment is activated
venv\Scripts\activate

# Load environment variables (using a helper script included in the zip)
.\load_env.bat  

# Run the application
streamlit run woocommerce_dashboard.py
```

#### macOS/Linux

```bash
# Make sure your virtual environment is activated
source venv/bin/activate

# Load environment variables and run
source load_env.sh && streamlit run woocommerce_dashboard.py
```

The application will start and automatically open in your default web browser at `http://localhost:8501`.

## Troubleshooting Common Issues

### Package Installation Errors

If you encounter errors during package installation:

```bash
# Try upgrading pip first
pip install --upgrade pip

# Install packages one by one if needed
pip install streamlit pandas plotly woocommerce
```

### Environment Variable Issues

If the application can't find your WooCommerce credentials:

1. Check that your `.env` file is in the correct location (same directory as `woocommerce_dashboard.py`)
2. Verify the environment variables are being loaded correctly
3. As a temporary test, you can set them directly in your terminal/command prompt:

#### Windows

```powershell
$env:WOOCOMMERCE_URL = "https://your-store.com"
$env:WOOCOMMERCE_KEY = "your_key"
$env:WOOCOMMERCE_SECRET = "your_secret"
```

#### macOS/Linux

```bash
export WOOCOMMERCE_URL="https://your-store.com"
export WOOCOMMERCE_KEY="your_key"
export WOOCOMMERCE_SECRET="your_secret"
```

### Connection Issues

If you encounter API connection issues:

1. Verify your WooCommerce site is accessible
2. Check that your API credentials are correct
3. Ensure your WooCommerce REST API is enabled
4. Check if your store has restrictions on API access based on IP addresses

## Updating the Application

To update the application when new versions are available:

1. Download the latest version
2. Extract it to a new directory
3. Copy your `.env` file to the new directory
4. Set up a new environment or install any new dependencies
5. Run the application as described above

## Additional Notes

- For Windows users: If you see "Access Denied" errors when creating files that start with a dot (like `.env`), use Notepad and save with quotes: Save as `".env"` (including the quotes)
- For macOS users: Files starting with a dot are hidden by default. Use Command+Shift+. to show hidden files in Finder
- The dashboard will automatically cache API responses to improve performance. To clear the cache, restart the application