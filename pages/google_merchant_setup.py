"""
Google Merchant Center Setup Page

This page allows the user to set up their Google Merchant Center
integration for accurate CAC data in the dashboard.
"""

import os
import json
import time
import logging
import streamlit as st
from datetime import datetime, timedelta
import pandas as pd

import sys
sys.path.append('.')
from utils.google_merchant_client import GoogleMerchantClient, CREDENTIALS_FILE, TOKEN_FILE, SCOPES
from utils.translations import Translations
from google_auth_oauthlib.flow import InstalledAppFlow

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
            3. Enable the **Content API for Shopping** and **Google Analytics API**
            4. Create OAuth 2.0 credentials (Web application type)
            5. Add `https://localhost:8080/oauth2callback` to the list of authorized redirect URIs
            6. Make sure your Google account is added as a test user in the OAuth consent screen
            7. Download the credentials JSON file
            
            ⚠️ **Important:** If you see "403: access_denied" errors, please verify your OAuth settings
            in the Google Cloud Console, especially that the redirect URI is correctly configured.
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
                    st.info("""
                    ## Authentication Instructions:
                    
                    1. The authentication URL will appear below this message in a blue box
                    2. **Copy that URL** and open it in a new browser tab
                    3. **Sign in with your Google account** and authorize the application
                    4. You'll be redirected to localhost (which may show an error page - this is normal)
                    5. **Look at your browser's address bar** for a URL like: `http://localhost:8080/?code=4/XXXX...`
                    6. **Copy the entire code parameter** (everything after `code=` and before any `&` character)
                    7. **Paste this code** in the input field that appears below the URL
                    
                    ⚠️ **Important:** Make sure to use the code from the URL in your browser's address bar,
                    not any code that might be displayed on the error page itself.
                    """)
                    # Create containers for the authentication process
                    auth_url_container = st.empty()
                    auth_status_container = st.empty()
                    
                    # Generate Google Auth URL directly in Streamlit
                    if not os.path.exists(CREDENTIALS_FILE):
                        auth_url_container.error(f"Credentials file not found. Please upload your Google API credentials first.")
                    else:
                        # Load credentials
                        try:
                            with open(CREDENTIALS_FILE, 'r') as f:
                                creds_data = json.load(f)
                                
                            # Check if credentials are valid
                            if 'web' in creds_data or 'installed' in creds_data:
                                # Using the flow imported at the top of the file
                                # SCOPES are already imported from utils.google_merchant_client
                                
                                # The app may be running on Replit, so we need to use a public redirect URI
                                # For security, we're using a common pattern for testing apps
                                flow = InstalledAppFlow.from_client_secrets_file(
                                    CREDENTIALS_FILE, 
                                    SCOPES,
                                    redirect_uri='https://localhost:8080/oauth2callback'
                                )
                                
                                # Get the auth URL
                                auth_url, _ = flow.authorization_url(prompt='consent')
                                
                                # Display the auth URL
                                auth_url_container.code(
                                    f"🔗 Authentication URL:\n\n{auth_url}\n\n"
                                    "👆 Copy this URL and open it in your browser.\n"
                                    "After logging in, you'll be redirected to localhost (which may show an error page).\n"
                                    "Look in the browser's address bar for a URL that looks like:\n"
                                    "http://localhost:8080/?code=4/XXXX...\n\n"
                                    "ONLY copy the value of the 'code' parameter (everything after 'code=' and before any '&' character)\n"
                                    "For example, if you see: http://localhost:8080/?code=4/P7q-abcdef123456&scope=...\n"
                                    "You should only copy: 4/P7q-abcdef123456\n\n"
                                    "Paste ONLY this code in the box below. Do NOT paste the full URL."
                                )
                                
                                # Get the authorization code from the user
                                auth_code = auth_status_container.text_input(
                                    "Enter the authorization code provided by Google:",
                                    key="auth_code"
                                )
                                
                                if auth_code:
                                    # Clean up the authorization code if needed
                                    # The error "OAuth 2 parameters can only have a single value: client_id" 
                                    # occurs when the user copies the entire URL instead of just the code
                                    
                                    # If the user entered the full URL instead of just the code part
                                    if "client_id" in auth_code:
                                        st.warning("""
                                        It looks like you've pasted the entire URL instead of just the authorization code.
                                        
                                        Please copy ONLY the code parameter from the URL (the part after `code=` and before any `&` character).
                                        """)
                                        # Extract just the code parameter if possible
                                        try:
                                            if "code=" in auth_code:
                                                code_part = auth_code.split("code=")[1]
                                                if "&" in code_part:
                                                    auth_code = code_part.split("&")[0]
                                                    st.info(f"Automatically extracted code: {auth_code[:10]}...")
                                                else:
                                                    auth_code = code_part
                                                    st.info(f"Automatically extracted code: {auth_code[:10]}...")
                                        except Exception as e:
                                            st.error(f"Could not automatically extract the code. Please manually copy only the code parameter.")
                                            logger.error(f"Code extraction error: {str(e)}", exc_info=True)
                                            auth_code = None
                                    
                                    # Process the authorization code if provided
                                    if auth_code:
                                        # Clean up the authorization code if needed
                                        # The error "OAuth 2 parameters can only have a single value: client_id" 
                                        # occurs when the user copies the entire URL instead of just the code
                                        
                                        # If the user entered the full URL instead of just the code part
                                        if "client_id" in auth_code:
                                            st.warning("""
                                            It looks like you've pasted the entire URL instead of just the authorization code.
                                            
                                            Please copy ONLY the code parameter from the URL (the part after `code=` and before any `&` character).
                                            """)
                                            # Extract just the code parameter if possible
                                            try:
                                                if "code=" in auth_code:
                                                    code_part = auth_code.split("code=")[1]
                                                    if "&" in code_part:
                                                        auth_code = code_part.split("&")[0]
                                                        st.info(f"Automatically extracted code: {auth_code[:10]}...")
                                                    else:
                                                        auth_code = code_part
                                                        st.info(f"Automatically extracted code: {auth_code[:10]}...")
                                            except Exception as e:
                                                st.error(f"Could not automatically extract the code. Please manually copy only the code parameter.")
                                                logger.error(f"Code extraction error: {str(e)}", exc_info=True)
                                                auth_code = None
                                        
                                        # Continue with the authentication process if we have a clean code
                                        if auth_code:
                                            try:
                                                with st.spinner("Completing authentication..."):
                                                    # Exchange code for credentials
                                                    flow.fetch_token(code=auth_code)
                                                    
                                                    # Save credentials to token file
                                                    with open(TOKEN_FILE, 'w') as token:
                                                        token.write(flow.credentials.to_json())
                                                        
                                                    st.success("✅ Authentication successful! Refreshing page...")
                                                    st.balloons()
                                                    time.sleep(2)
                                                    st.rerun()
                                            except Exception as token_error:
                                                error_msg = str(token_error)
                                                if "invalid_grant" in error_msg.lower():
                                                    st.error("""
                                                    ⚠️ **Invalid authorization code**
                                                    
                                                    The code you entered was invalid or has expired. Authorization codes can only be used once 
                                                    and expire quickly. Please try the authentication process again by refreshing this page.
                                                    """)
                                                elif "access_denied" in error_msg.lower():
                                                    st.error("""
                                                    ⚠️ **Access Denied Error (403)**
                                                    
                                                    Google denied access to the requested resources. This usually means:
                                                    1. Your OAuth consent screen isn't properly configured
                                                    2. Your Google account isn't added as a test user
                                                    3. The requested API scopes haven't been added to your OAuth consent screen
                                                    
                                                    Please check these settings in your Google Cloud Console.
                                                    """)
                                                elif "redirect_uri_mismatch" in error_msg.lower():
                                                    st.error("""
                                                    ⚠️ **Redirect URI Mismatch**
                                                    
                                                    The redirect URI in your OAuth credentials doesn't match the one used by this application.
                                                    
                                                    Please add exactly `https://localhost:8080/oauth2callback` to your authorized redirect URIs
                                                    in the Google Cloud Console.
                                                    """)
                                                elif "client_id" in error_msg.lower():
                                                    st.error("""
                                                    ⚠️ **OAuth 2 parameter error**
                                                    
                                                    There's an issue with the client_id parameter. This usually happens when:
                                                    1. You've pasted the full URL instead of just the code
                                                    2. The credentials file is malformed or invalid
                                                    
                                                    Please make sure you're only pasting the authorization code, not the entire URL.
                                                    """)
                                                else:
                                                    st.error(f"⚠️ Error processing authorization code: {error_msg}")
                                                
                                                logger.error(f"Token error: {error_msg}", exc_info=True)
                            else:
                                auth_url_container.error("⚠️ Invalid credentials file format. Please make sure you've uploaded the correct OAuth 2.0 credentials file.")
                        except Exception as e:
                            auth_url_container.error(f"⚠️ Error setting up authentication: {str(e)}")
                            logger.error(f"Authentication setup error: {str(e)}", exc_info=True)
    
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