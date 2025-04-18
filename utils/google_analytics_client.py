"""
Google Analytics Client for fetching ad cost data
This module provides a client for connecting to Google Analytics API (GA4)
and retrieving advertising cost data for use in the CAC analysis.
"""

import os
import datetime
import logging
import json
import pandas as pd
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import (
    DateRange,
    Dimension,
    Metric,
    RunReportRequest,
    FilterExpression,
    Filter,
)
from google.oauth2.service_account import Credentials

logger = logging.getLogger(__name__)

class GoogleAnalyticsClient:
    """
    Client for interacting with Google Analytics Data API (GA4)
    
    This class provides methods to fetch advertising cost data from
    Google Analytics and convert it to a format suitable for CAC analysis.
    """
    
    def __init__(self):
        """
        Initialize the GoogleAnalyticsClient
        
        Attempts to load credentials from environment variable or credentials file.
        """
        self.client = None
        self.property_id = os.environ.get('GOOGLE_ANALYTICS_PROPERTY_ID')
        self.credentials_str = os.environ.get('GOOGLE_ANALYTICS_CREDENTIALS')
        
        # Log initialization info
        logger.info("Initializing Google Analytics client")
        if not self.property_id:
            logger.warning("Google Analytics Property ID not found in environment variables")
        if not self.credentials_str:
            logger.warning("Google Analytics credentials not found in environment variables")
            
        # Try to initialize the client with credentials
        try:
            self._initialize_client()
        except Exception as e:
            logger.error(f"Failed to initialize Google Analytics client: {str(e)}", exc_info=True)
    
    def _initialize_client(self):
        """
        Initialize the GA4 client with credentials
        
        Raises:
            Exception: If credentials are not available or invalid
        """
        if not self.credentials_str or not self.property_id:
            logger.warning("Missing Google Analytics credentials or property ID")
            return
        
        try:
            # Parse the JSON credentials from the environment variable
            try:
                credentials_json = json.loads(self.credentials_str)
            except json.JSONDecodeError as json_err:
                logger.error(f"Error parsing Google Analytics credentials JSON: {str(json_err)}")
                logger.info("Checking if credentials string might be a file path...")
                
                # Try if the string might be a file path instead
                if os.path.exists(self.credentials_str):
                    try:
                        with open(self.credentials_str, 'r') as cred_file:
                            credentials_json = json.load(cred_file)
                        logger.info("Successfully loaded credentials from file")
                    except Exception as file_err:
                        logger.error(f"Error loading credentials from file: {str(file_err)}")
                        raise
                else:
                    # Not a valid JSON string or file path
                    raise json_err
            
            # Try to initialize with service account credentials
            scopes = ['https://www.googleapis.com/auth/analytics.readonly']
            
            try:
                credentials = Credentials.from_service_account_info(
                    credentials_json, 
                    scopes=scopes
                )
                self.client = BetaAnalyticsDataClient(credentials=credentials)
                logger.info("Successfully initialized Google Analytics client")
            except Exception as e:
                logger.error(f"Error creating credentials from service account info: {str(e)}")
                
                # Try alternative initialization if needed
                if 'client_id' in credentials_json and 'client_secret' in credentials_json:
                    logger.info("Attempting to use OAuth2 client credentials instead of service account")
                    # Handle OAuth client credentials differently if needed
                    # This would require additional implementation
                    raise NotImplementedError("OAuth2 client credentials not yet supported")
                else:
                    raise
                    
        except Exception as e:
            logger.error(f"Error initializing GA client with credentials: {str(e)}", exc_info=True)
            raise
    
    def get_ad_costs(self, start_date, end_date):
        """
        Retrieve advertising costs from Google Analytics for a date range
        
        Args:
            start_date (datetime): Start date for the data retrieval
            end_date (datetime): End date for the data retrieval
            
        Returns:
            DataFrame with campaign costs or None if retrieval fails
        """
        if not self.client:
            logger.warning("Google Analytics client not initialized, cannot fetch ad costs")
            return None
        
        try:
            # Format dates as required by GA4 API
            start_str = start_date.strftime('%Y-%m-%d')
            end_str = end_date.strftime('%Y-%m-%d')
            
            # Create the report request
            request = RunReportRequest(
                property=f"properties/{self.property_id}",
                date_ranges=[DateRange(start_date=start_str, end_date=end_str)],
                dimensions=[
                    Dimension(name="date"),
                    Dimension(name="campaign"),
                    Dimension(name="sourceMedium")
                ],
                metrics=[
                    Metric(name="advertiserAdCost"),
                    Metric(name="transactions"),
                    Metric(name="totalRevenue")
                ]
            )
            
            # Make the API request
            response = self.client.run_report(request)
            
            # Process the response into a DataFrame
            rows = []
            for row in response.rows:
                date_val = row.dimension_values[0].value
                campaign = row.dimension_values[1].value
                source_medium = row.dimension_values[2].value
                
                ad_cost = float(row.metric_values[0].value) if row.metric_values[0].value else 0
                transactions = int(row.metric_values[1].value) if row.metric_values[1].value else 0
                revenue = float(row.metric_values[2].value) if row.metric_values[2].value else 0
                
                rows.append({
                    'Date': datetime.datetime.strptime(date_val, '%Y%m%d').date(),
                    'Campaign': campaign,
                    'Source_Medium': source_medium,
                    'Ad_Cost': ad_cost,
                    'Transactions': transactions,
                    'Revenue': revenue
                })
            
            # Create DataFrame from rows
            if rows:
                df = pd.DataFrame(rows)
                logger.info(f"Successfully retrieved ad cost data: {len(df)} rows")
                return df
            else:
                logger.warning("No ad cost data found for the specified period")
                return pd.DataFrame()
                
        except Exception as e:
            logger.error(f"Error fetching ad costs from Google Analytics: {str(e)}", exc_info=True)
            return None
    
    def calculate_total_ad_spend(self, start_date, end_date):
        """
        Calculate the total ad spend for a date range
        
        Args:
            start_date (datetime): Start date for the calculation
            end_date (datetime): End date for the calculation
            
        Returns:
            dict: Dictionary with total ad spend and campaign breakdown
        """
        df = self.get_ad_costs(start_date, end_date)
        
        if df is None or df.empty:
            logger.warning("No ad cost data available for calculating total spend")
            return {
                'total_spend': 0,
                'spend_by_campaign': {},
                'spend_by_date': {},
                'has_data': False
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
            'has_data': True
        }
    
    def calculate_campaign_performance(self, start_date, end_date):
        """
        Calculate campaign performance metrics (ROI, CPA, etc.)
        
        Args:
            start_date (datetime): Start date for the calculation
            end_date (datetime): End date for the calculation
            
        Returns:
            DataFrame with campaign performance metrics
        """
        df = self.get_ad_costs(start_date, end_date)
        
        if df is None or df.empty:
            logger.warning("No ad cost data available for calculating campaign performance")
            return pd.DataFrame()
        
        # Group by campaign
        campaign_data = df.groupby('Campaign').agg({
            'Ad_Cost': 'sum',
            'Transactions': 'sum',
            'Revenue': 'sum'
        }).reset_index()
        
        # Calculate performance metrics
        campaign_data['ROI'] = (campaign_data['Revenue'] - campaign_data['Ad_Cost']) / campaign_data['Ad_Cost'] * 100
        campaign_data['CPA'] = campaign_data.apply(
            lambda x: x['Ad_Cost'] / x['Transactions'] if x['Transactions'] > 0 else float('inf'), 
            axis=1
        )
        campaign_data['ROAS'] = campaign_data.apply(
            lambda x: x['Revenue'] / x['Ad_Cost'] if x['Ad_Cost'] > 0 else float('inf'),
            axis=1
        )
        
        # Replace inf values with NaN for better display
        campaign_data.replace([float('inf'), -float('inf')], pd.NA, inplace=True)
        
        return campaign_data