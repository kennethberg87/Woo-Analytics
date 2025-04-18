"""
Google Ads Client for fetching ad cost data directly from Google Ads API
This module provides a client for connecting to Google Ads API
and retrieving advertising cost data for use in the CAC analysis.
"""
import os
import json
import logging
import datetime
from typing import Dict, List, Optional, Any, Union

import pandas as pd

# Initialize logger
logger = logging.getLogger(__name__)

class GoogleAdsClient:
    """
    Client for interacting with Google Ads API
    
    This class provides methods to fetch advertising cost data from
    Google Ads and convert it to a format suitable for CAC analysis.
    """
    
    def __init__(self):
        """
        Initialize the GoogleAdsClient
        
        Attempts to load credentials from environment variable or credentials file.
        """
        self.credentials = None
        self.api_ready = False
        
        # Get credentials from environment variable
        google_ads_creds = os.environ.get('GOOGLE_ADS_CREDENTIALS')
        if google_ads_creds:
            try:
                self.credentials = json.loads(google_ads_creds)
                logger.info("Loaded Google Ads credentials from environment variable")
                self.api_ready = True
            except Exception as e:
                logger.error(f"Failed to parse Google Ads credentials from environment: {str(e)}")
    
    def _check_required_libraries(self):
        """Check if required libraries are available"""
        try:
            # Import the Google Ads client library within this method to avoid errors
            # if the library is not installed
            import google.ads.googleads.client
            import google.ads.googleads.errors
            
            return True, None
        except ImportError as e:
            logger.error(f"Google Ads API libraries not installed: {str(e)}")
            return False, f"Google Ads API libraries not installed: {str(e)}"
    
    def get_ad_costs(self, start_date: datetime.date, end_date: datetime.date) -> Optional[pd.DataFrame]:
        """
        Fetch advertising costs from Google Ads for a date range
        
        Args:
            start_date: Start date for the data retrieval 
            end_date: End date for the data retrieval
            
        Returns:
            DataFrame with campaign costs or None if retrieval fails
        """
        if not self.api_ready:
            logger.warning("Google Ads client not properly initialized")
            return None
            
        # Check if required libraries are available
        libs_available, error_msg = self._check_required_libraries()
        if not libs_available:
            raise ImportError(error_msg)
        
        try:
            # Import here to avoid import errors if the package is not installed
            from google.ads.googleads.client import GoogleAdsClient
            
            logger.info(f"Attempting to fetch Google Ads cost data for {start_date} to {end_date}")
            
            # Check if we have credentials for Google Ads API
            client_id = os.environ.get("GOOGLE_ADS_CLIENT_ID")
            client_secret = os.environ.get("GOOGLE_ADS_CLIENT_SECRET")
            developer_token = os.environ.get("GOOGLE_ADS_DEVELOPER_TOKEN")
            customer_id = os.environ.get("GOOGLE_ADS_CUSTOMER_ID")
            refresh_token = os.environ.get("GOOGLE_ADS_REFRESH_TOKEN")
            
            if not all([client_id, client_secret, developer_token, customer_id, refresh_token]):
                logger.warning("Missing Google Ads API credentials")
                return None
                
            try:
                # Initialize Google Ads client
                credentials = {
                    "client_id": client_id,
                    "client_secret": client_secret,
                    "developer_token": developer_token,
                    "refresh_token": refresh_token,
                    "use_proto_plus": True
                }
                client = GoogleAdsClient.load_from_dict(credentials)
                
                # Format date range for the query
                start_date_str = start_date.strftime("%Y-%m-%d")
                end_date_str = end_date.strftime("%Y-%m-%d")
                
                # Create the GAQL query
                query = f"""
                    SELECT 
                        campaign.id, 
                        campaign.name, 
                        metrics.cost_micros, 
                        metrics.conversions,
                        segments.date 
                    FROM campaign 
                    WHERE segments.date BETWEEN '{start_date_str}' AND '{end_date_str}'
                    ORDER BY campaign.id
                """
                
                # Execute the query
                ga_service = client.get_service("GoogleAdsService")
                search_request = client.get_type("SearchGoogleAdsRequest")
                search_request.customer_id = customer_id
                search_request.query = query
                search_request.page_size = 1000  # Adjust as needed
                
                # Get the results
                results = []
                stream = ga_service.search_stream(search_request)
                
                for batch in stream:
                    for row in batch.results:
                        results.append({
                            'Campaign_ID': row.campaign.id,
                            'Campaign': row.campaign.name,
                            'Date': row.segments.date,
                            'Ad_Cost': row.metrics.cost_micros / 1000000,  # Convert micros to NOK
                            'Conversions': row.metrics.conversions
                        })
                
                # Convert to DataFrame
                if results:
                    df = pd.DataFrame(results)
                    df['Date'] = pd.to_datetime(df['Date'])
                    return df
                else:
                    logger.warning("No data returned from Google Ads API")
                    return None
                    
            except Exception as e:
                logger.error(f"Error executing Google Ads API request: {str(e)}", exc_info=True)
                return None
            
        except Exception as e:
            logger.error(f"Error fetching ad costs from Google Ads: {str(e)}", exc_info=True)
            return None
            
    def calculate_total_ad_spend(self, start_date: datetime.date, end_date: datetime.date) -> Dict[str, Any]:
        """
        Calculate the total ad spend for a date range
        
        Args:
            start_date: Start date for the calculation
            end_date: End date for the calculation
            
        Returns:
            dict: Dictionary with total ad spend and campaign breakdown
        """
        try:
            df = self.get_ad_costs(start_date, end_date)
            
            if df is None or df.empty:
                logger.warning("No ad cost data available from Google Ads")
                return {
                    'total_spend': 0,
                    'spend_by_campaign': {},
                    'spend_by_date': {},
                    'has_data': False,
                    'source': 'google_ads',
                    'error_message': "Google Ads API integration not fully implemented or no data found"
                }
            
            # Calculate total spend
            total_spend = df['Ad_Cost'].sum()
            
            # Calculate spend by campaign
            campaign_spend = df.groupby('Campaign')['Ad_Cost'].sum().to_dict()
            
            # Calculate spend by date
            date_spend = df.groupby('Date')['Ad_Cost'].sum().to_dict()
            
            return {
                'total_spend': total_spend,
                'spend_by_campaign': campaign_spend,
                'spend_by_date': date_spend,
                'has_data': True,
                'source': 'google_ads'
            }
            
        except ImportError as e:
            logger.error(f"Google Ads API libraries not available: {str(e)}")
            return {
                'total_spend': 0,
                'spend_by_campaign': {},
                'spend_by_date': {},
                'has_data': False,
                'source': 'google_ads',
                'error_message': f"Google Ads API libraries not available: {str(e)}"
            }
            
        except Exception as e:
            logger.error(f"Error calculating ad spend from Google Ads: {str(e)}", exc_info=True)
            return {
                'total_spend': 0,
                'spend_by_campaign': {},
                'spend_by_date': {},
                'has_data': False,
                'source': 'google_ads',
                'error_message': f"Error accessing Google Ads API: {str(e)}"
            }