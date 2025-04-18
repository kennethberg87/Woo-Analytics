"""
Google Merchant Center Setup Page

This page allows the user to set up their Google Merchant Center
integration for accurate CAC data in the dashboard.
"""

import os
import json
import logging
import streamlit as st
from datetime import datetime, timedelta
import pandas as pd

import sys
sys.path.append('.')
from utils.google_merchant_client import GoogleMerchantClient, CREDENTIALS_FILE, TOKEN_FILE
from utils.translations import Translations

# Initialize translations
translations = Translations()
def t(key, *args):
    """Shorthand for translations.get_text"""
    return translations.get_text(key, st.session_state.get('language', 'no'), *args)

# Configure logging
logger = logging.getLogger(__name__)

def setup_credentials():
    """Set up Google Merchant Center credentials"""
    st.title("🔄 Google Merchant Center Integration")
    
    st.markdown("""
    ## Why Connect to Google Merchant?
    
    Connecting to your Google Merchant account will provide accurate Customer Acquisition Cost (CAC) 
    data for your WooCommerce store. This helps you make better marketing decisions by showing 
    the true cost of acquiring customers through Google Ads.
    
    ### Benefits
    - **Actual CAC Values**: Instead of estimating, get real advertising costs
    - **Campaign-Level Data**: See which campaigns perform best
    - **ROI Analysis**: Measure return on ad spend accurately
    """)
    
    # Check if credentials already exist
    credentials_exist = os.path.exists(CREDENTIALS_FILE)
    token_exists = os.path.exists(TOKEN_FILE)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Step 1: Provide Google API Credentials")
        
        if credentials_exist:
            st.success("✅ Google API credentials are already set up")
            
            # Option to upload new credentials
            if st.button("Update Credentials"):
                if os.path.exists(CREDENTIALS_FILE):
                    os.remove(CREDENTIALS_FILE)
                if os.path.exists(TOKEN_FILE):
                    os.remove(TOKEN_FILE)
                st.rerun()
        else:
            st.info("""
            To connect to Google Merchant, you need to:
            1. Go to [Google Cloud Console](https://console.cloud.google.com/)
            2. Create a project (or select an existing one)
            3. Enable the Content API for Shopping
            4. Create OAuth 2.0 credentials (Web application type)
            5. Download the credentials JSON file
            """)
            
            # File uploader for credentials
            uploaded_file = st.file_uploader("Upload Google API credentials (client_secret.json)", type=['json'])
            
            if uploaded_file is not None:
                try:
                    # Save the uploaded credentials
                    credentials_data = json.loads(uploaded_file.getvalue())
                    
                    # Validate it has the right structure
                    if 'web' in credentials_data or 'installed' in credentials_data:
                        with open(CREDENTIALS_FILE, 'w') as f:
                            json.dump(credentials_data, f)
                        st.success("✅ Credentials file uploaded successfully!")
                        
                        # Force refresh of the page
                        st.rerun()
                    else:
                        st.error("⚠️ Invalid credentials file. Please make sure you've downloaded the correct OAuth 2.0 credentials file.")
                except Exception as e:
                    st.error(f"⚠️ Error processing credentials file: {str(e)}")
    
    # Only show authentication step if credentials are uploaded
    if credentials_exist:
        with col1:
            st.subheader("Step 2: Authenticate with Google")
            
            if token_exists:
                st.success("✅ Already authenticated with Google Merchant Center")
                
                # Option to reauthenticate
                if st.button("Reauthenticate"):
                    if os.path.exists(TOKEN_FILE):
                        os.remove(TOKEN_FILE)
                    st.rerun()
            else:
                st.info("Click the button below to authenticate with your Google account")
                
                if st.button("Authenticate with Google"):
                    try:
                        with st.spinner("Waiting for authentication..."):
                            # Initialize the client which will trigger authentication
                            client = GoogleMerchantClient()
                            
                            # Check if we have a valid client after authentication
                            if client.merchant_id:
                                st.success(f"✅ Successfully authenticated with Google Merchant Center (ID: {client.merchant_id})")
                                st.balloons()
                                # Force refresh of the page
                                st.rerun()
                            else:
                                st.error("⚠️ Authentication completed but couldn't find a Merchant Center account")
                    except Exception as e:
                        st.error(f"⚠️ Authentication failed: {str(e)}")
                        logger.error(f"Authentication error: {str(e)}", exc_info=True)
    
    # Display test data if fully authenticated
    if credentials_exist and token_exists:
        with col2:
            st.subheader("Connection Status")
            st.success("✅ Connected to Google Merchant Center")
            
            # Test data retrieval
            try:
                client = GoogleMerchantClient()
                
                # Display merchant ID
                if client.merchant_id:
                    st.info(f"Merchant ID: {client.merchant_id}")
                
                # Test fetching last 7 days of data
                end_date = datetime.now()
                start_date = end_date - timedelta(days=7)
                
                with st.spinner("Testing data retrieval..."):
                    cac_data = client.get_cac_data_for_period(start_date, end_date)
                    
                    if cac_data['total_ad_spend'] > 0:
                        st.metric(
                            "Ad Spend (Last 7 days)", 
                            f"kr {cac_data['total_ad_spend']:,.2f}"
                        )
                        st.metric(
                            "Actual CAC", 
                            f"kr {cac_data['ad_cost_per_order']:,.2f}",
                            help="Average cost per acquisition"
                        )
                    else:
                        st.warning("No ad spend data available for the last 7 days")
            except Exception as e:
                st.error(f"Error testing connection: {str(e)}")
                logger.error(f"Test data retrieval error: {str(e)}", exc_info=True)
        
        # Show how to use in dashboard
        st.subheader("Step 3: Using Accurate CAC Data")
        st.info("""
        Now that you're connected to Google Merchant Center:
        
        1. Go to the **Results** tab in the dashboard
        2. Select the **Customer Acquisition Cost Analysis** subtab
        3. The dashboard will now display actual CAC values from Google instead of estimates
        
        The data will automatically update based on your selected date range in the dashboard.
        """)

if __name__ == "__main__":
    # Set page config
    st.set_page_config(
        page_title="Google Merchant Center Setup",
        page_icon="🔄",
        layout="wide",
    )
    
    # Initialize session state for language if not already set
    if 'language' not in st.session_state:
        st.session_state['language'] = 'no'
    
    # Set up the credentials
    setup_credentials()