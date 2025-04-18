"""
Google Merchant Account Client for WooCommerce Dashboard

This module provides functionality to connect to Google Merchant Center
and fetch data about advertising costs and campaign performance.
"""

import os
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional

import pandas as pd
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

# Configure logging
logger = logging.getLogger(__name__)

# Define scopes needed for Google Merchant Center and Google Analytics
SCOPES = [
    'https://www.googleapis.com/auth/content',               # Merchant Center API
    'https://www.googleapis.com/auth/analytics.readonly',    # Google Analytics API
    'https://www.googleapis.com/auth/adwords'                # Google Ads API
]

# Token file path
TOKEN_FILE = 'google_merchant_token.json'
CREDENTIALS_FILE = 'google_merchant_credentials.json'

class GoogleMerchantClient:
    """Client for interacting with Google Merchant Center to fetch ad cost data"""
    
    def __init__(self):
        """Initialize the Google Merchant Client"""
        self.creds = None
        self.merchant_service = None
        self.analytics_service = None
        self.merchant_id = None
        self._authenticate()
    
    def _authenticate(self) -> None:
        """
        Authenticate with Google Merchant Center using OAuth2
        
        This will open a browser window for the user to authenticate if credentials
        are not already saved.
        """
        try:
            # Check if token file exists and is valid
            if os.path.exists(TOKEN_FILE):
                with open(TOKEN_FILE, 'r') as token:
                    self.creds = Credentials.from_authorized_user_info(json.load(token), SCOPES)
            
            # If credentials don't exist or are invalid, prompt authentication
            if not self.creds or not self.creds.valid:
                if self.creds and self.creds.expired and self.creds.refresh_token:
                    self.creds.refresh(Request())
                else:
                    # If credentials file doesn't exist, raise an exception
                    if not os.path.exists(CREDENTIALS_FILE):
                        raise FileNotFoundError(
                            f"Google Merchant Center credentials file '{CREDENTIALS_FILE}' not found. "
                            "Please create this file with your OAuth client ID and client secret."
                        )
                    
                    # Create OAuth flow for Replit environment
                    flow = InstalledAppFlow.from_client_secrets_file(
                        CREDENTIALS_FILE, 
                        SCOPES,
                        redirect_uri='urn:ietf:wg:oauth:2.0:oob'  # Use out-of-band flow for Replit
                    )
                    
                    # Get the authorization URL
                    auth_url, _ = flow.authorization_url(prompt='consent')
                    print("\n")
                    print("="*80)
                    print("AUTHENTICATION REQUIRED")
                    print("="*80)
                    print(f"1. Go to this URL in your browser:\n\n{auth_url}\n")
                    print("2. Log in and authorize access if prompted")
                    print("3. Copy the authorization code from the browser")
                    print("4. Paste the code here and press Enter:")
                    print("="*80)
                    
                    # Get the authorization code from user
                    code = input("Enter authorization code: ").strip()
                    
                    # Exchange authorization code for credentials
                    flow.fetch_token(code=code)
                    self.creds = flow.credentials
                
                # Save the credentials for the next run
                with open(TOKEN_FILE, 'w') as token:
                    token.write(self.creds.to_json())
            
            # Build services once authenticated
            self.merchant_service = build('content', 'v2.1', credentials=self.creds)
            self.analytics_service = build('analyticsreporting', 'v4', credentials=self.creds)
            
            # Get Merchant ID (first account accessible to the authenticated user)
            accounts = self.merchant_service.accounts().list().execute()
            if accounts.get('resources'):
                self.merchant_id = accounts['resources'][0]['id']
                logger.info(f"Authenticated with Google Merchant Center. Merchant ID: {self.merchant_id}")
            else:
                logger.warning("No merchant accounts found for the authenticated user")
                
        except Exception as e:
            logger.error(f"Google Merchant Center authentication failed: {str(e)}")
            raise
    
    def get_ad_costs(self, start_date: datetime, end_date: datetime) -> pd.DataFrame:
        """
        Fetch advertising costs for the specified date range
        
        Args:
            start_date: Start date for fetching costs
            end_date: End date for fetching costs
            
        Returns:
            DataFrame with daily ad costs
        """
        try:
            # Format dates as required by the API
            start_date_str = start_date.strftime('%Y-%m-%d')
            end_date_str = end_date.strftime('%Y-%m-%d')
            
            # Fetch the data from Google Analytics
            response = self.analytics_service.reports().batchGet(
                body={
                    'reportRequests': [
                        {
                            'viewId': self._get_analytics_view_id(),
                            'dateRanges': [{'startDate': start_date_str, 'endDate': end_date_str}],
                            'metrics': [
                                {'expression': 'ga:adCost'},
                                {'expression': 'ga:adClicks'},
                                {'expression': 'ga:adImpressions'},
                                {'expression': 'ga:transactions'},
                                {'expression': 'ga:transactionRevenue'}
                            ],
                            'dimensions': [{'name': 'ga:date'}]
                        }
                    ]
                }
            ).execute()
            
            # Process response into DataFrame
            data = []
            for report in response.get('reports', []):
                for row in report.get('data', {}).get('rows', []):
                    date_str = row['dimensions'][0]  # Date in format YYYYMMDD
                    date = datetime.strptime(date_str, '%Y%m%d').strftime('%Y-%m-%d')
                    metrics = row.get('metrics', [{}])[0].get('values', [])
                    
                    if len(metrics) >= 5:
                        data.append({
                            'Date': date,
                            'Ad_Cost': float(metrics[0]),
                            'Ad_Clicks': int(metrics[1]),
                            'Ad_Impressions': int(metrics[2]),
                            'Transactions': int(metrics[3]),
                            'Revenue': float(metrics[4]),
                        })
            
            if not data:
                logger.warning("No advertising cost data found in the specified date range")
                return pd.DataFrame(columns=['Date', 'Ad_Cost', 'Ad_Clicks', 'Ad_Impressions', 'Transactions', 'Revenue'])
                
            return pd.DataFrame(data)
            
        except Exception as e:
            logger.error(f"Error fetching ad costs from Google: {str(e)}")
            # If API access fails, return empty DataFrame
            return pd.DataFrame(columns=['Date', 'Ad_Cost', 'Ad_Clicks', 'Ad_Impressions', 'Transactions', 'Revenue'])
    
    def get_cac_data_for_period(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """
        Calculate CAC metrics using Google Merchant data for the specified period
        
        Args:
            start_date: Start date for analysis 
            end_date: End date for analysis
            
        Returns:
            Dictionary with CAC metrics
        """
        try:
            # Fetch ad costs data
            ad_data = self.get_ad_costs(start_date, end_date)
            
            if ad_data.empty:
                # Return default values if no data available
                return {
                    'total_ad_spend': 0,
                    'ad_cost_per_order': 0,
                    'daily_costs': pd.DataFrame(columns=['Date', 'Ad_Cost'])
                }
            
            # Calculate total advertising spend and metrics
            total_ad_spend = ad_data['Ad_Cost'].sum()
            total_transactions = ad_data['Transactions'].sum()
            
            # Calculate ad cost per order (actual CAC)
            ad_cost_per_order = total_ad_spend / total_transactions if total_transactions > 0 else 0
            
            # Prepare daily costs data
            daily_costs = ad_data[['Date', 'Ad_Cost']].copy()
            
            return {
                'total_ad_spend': total_ad_spend,
                'ad_cost_per_order': ad_cost_per_order,
                'ctr': ad_data['Ad_Clicks'].sum() / ad_data['Ad_Impressions'].sum() if ad_data['Ad_Impressions'].sum() > 0 else 0,
                'roas': ad_data['Revenue'].sum() / total_ad_spend if total_ad_spend > 0 else 0,
                'daily_costs': daily_costs
            }
            
        except Exception as e:
            logger.error(f"Error calculating CAC metrics from Google data: {str(e)}")
            # Return default values if calculation fails
            return {
                'total_ad_spend': 0,
                'ad_cost_per_order': 0,
                'daily_costs': pd.DataFrame(columns=['Date', 'Ad_Cost'])
            }
    
    def _get_analytics_view_id(self) -> str:
        """Get the first available Google Analytics view ID"""
        try:
            analytics_admin = build('analyticsadmin', 'v1alpha', credentials=self.creds)
            response = analytics_admin.properties().list().execute()
            properties = response.get('properties', [])
            
            if not properties:
                raise ValueError("No Google Analytics properties found")
                
            # Get first property ID
            property_id = properties[0]['name'].split('/')[-1]
            
            # Get data streams for this property
            streams = analytics_admin.properties().dataStreams().list(
                parent=f"properties/{property_id}"
            ).execute()
            
            if not streams.get('dataStreams'):
                raise ValueError("No data streams found in Google Analytics property")
                
            # Return the first data stream ID
            return streams['dataStreams'][0]['name'].split('/')[-1]
            
        except Exception as e:
            logger.error(f"Error getting Analytics view ID: {str(e)}")
            # Return a placeholder value - will be overridden by environment
            return os.environ.get('GOOGLE_ANALYTICS_VIEW_ID', '')