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
            
            # Log the requested date range for debugging
            logger.info(f"Requesting Google Analytics data from {start_str} to {end_str}")
            
            # First try with the primary metrics for Google Ads integration
            metrics_to_try = [
                # First attempt with the standard advertiserAdCost
                [
                    Metric(name="advertiserAdCost"), 
                    Metric(name="transactions"),
                    Metric(name="totalRevenue")
                ],
                # Second attempt with adCost which is used for some GA4 properties
                [
                    Metric(name="adCost"), 
                    Metric(name="transactions"),
                    Metric(name="totalRevenue")
                ],
                # Last attempt with Google Ads cost and clicks
                [
                    Metric(name="googleAdsImpressions"),
                    Metric(name="googleAdsClicks"),
                    Metric(name="googleAdsCost"),
                    Metric(name="transactions"),
                    Metric(name="totalRevenue")
                ]
            ]
            
            # Try each set of metrics until we find data
            metrics = metrics_to_try[-1]  # Default to the last set (fallback)
            metric_names = [m.name for m in metrics]  # Initialize for error case
            
            found_data = False
            for attempt_metrics in metrics_to_try:
                try:
                    # Log which metrics we're trying
                    attempt_metric_names = [m.name for m in attempt_metrics]
                    logger.info(f"Trying Google Analytics metrics: {', '.join(attempt_metric_names)}")
                    
                    # Create the report request
                    request = RunReportRequest(
                        property=f"properties/{self.property_id}",
                        date_ranges=[DateRange(start_date=start_str, end_date=end_str)],
                        dimensions=[
                            Dimension(name="date"),
                            Dimension(name="campaign"),
                            Dimension(name="sourceMedium")
                        ],
                        metrics=attempt_metrics
                    )
                    
                    # Make the API request
                    response = self.client.run_report(request)
                    
                    # If we got rows, we found the right metrics!
                    if len(response.rows) > 0:
                        logger.info(f"Found data using metrics: {', '.join(attempt_metric_names)}")
                        metrics = attempt_metrics
                        metric_names = attempt_metric_names
                        found_data = True
                        break
                        
                except Exception as metric_error:
                    logger.warning(f"Error with metrics {', '.join(attempt_metric_names)}: {str(metric_error)}")
                    # Continue to the next set of metrics
                    continue
            
            if not found_data:
                logger.warning("None of the metric sets returned data")
                    
            # Create the report request with our final metrics
            # This will use the last successful metrics set, or the last one we tried
            request = RunReportRequest(
                property=f"properties/{self.property_id}",
                date_ranges=[DateRange(start_date=start_str, end_date=end_str)],
                dimensions=[
                    Dimension(name="date"),
                    Dimension(name="campaign"),
                    Dimension(name="sourceMedium")
                ],
                metrics=metrics
            )
            
            # Make the API request
            response = self.client.run_report(request)
            
            # Process the response into a DataFrame
            rows = []
            
            # Get metric names from the request to know what we're looking at
            metric_names = [m.name for m in metrics]
            logger.info(f"Processing response with metrics: {', '.join(metric_names)}")
            
            # Add debugging information about response structure
            logger.debug(f"Response has {len(response.rows)} rows and {len(response.metric_headers)} metrics")
            if len(response.metric_headers) > 0:
                header_names = [h.name for h in response.metric_headers]
                logger.debug(f"Metric headers: {', '.join(header_names)}")
            
            for row in response.rows:
                date_val = row.dimension_values[0].value
                campaign = row.dimension_values[1].value
                source_medium = row.dimension_values[2].value
                
                # Handle different metric configurations
                # Check which metrics we have based on our earlier selection
                data_row = {
                    'Date': datetime.datetime.strptime(date_val, '%Y%m%d').date(),
                    'Campaign': campaign,
                    'Source_Medium': source_medium,
                }
                
                # If we're using the standard metrics (advertiserAdCost or adCost)
                if "advertiserAdCost" in metric_names or "adCost" in metric_names:
                    data_row['Ad_Cost'] = float(row.metric_values[0].value) if row.metric_values[0].value else 0
                    data_row['Transactions'] = int(row.metric_values[1].value) if row.metric_values[1].value else 0
                    data_row['Revenue'] = float(row.metric_values[2].value) if row.metric_values[2].value else 0
                
                # If we're using the Google Ads specific metrics
                elif "googleAdsCost" in metric_names:
                    # The position will depend on our metric order
                    cost_index = metric_names.index("googleAdsCost")
                    data_row['Ad_Cost'] = float(row.metric_values[cost_index].value) if row.metric_values[cost_index].value else 0
                    
                    # Try to find transactions and revenue
                    if "transactions" in metric_names:
                        trans_index = metric_names.index("transactions")
                        data_row['Transactions'] = int(row.metric_values[trans_index].value) if row.metric_values[trans_index].value else 0
                    else:
                        data_row['Transactions'] = 0
                        
                    if "totalRevenue" in metric_names:
                        rev_index = metric_names.index("totalRevenue")
                        data_row['Revenue'] = float(row.metric_values[rev_index].value) if row.metric_values[rev_index].value else 0
                    else:
                        data_row['Revenue'] = 0
                
                # Fallback for any other metric configuration
                else:
                    # Just use the first metric as the ad cost if we don't recognize the pattern
                    # This is a fallback approach - not ideal but better than failing
                    data_row['Ad_Cost'] = float(row.metric_values[0].value) if row.metric_values[0].value else 0
                    data_row['Transactions'] = int(row.metric_values[1].value) if len(row.metric_values) > 1 and row.metric_values[1].value else 0
                    data_row['Revenue'] = float(row.metric_values[2].value) if len(row.metric_values) > 2 and row.metric_values[2].value else 0
                
                # Log the processed row for debugging
                logger.debug(f"Processed row: {data_row}")
                rows.append(data_row)
            
            # Create DataFrame from rows
            if rows:
                df = pd.DataFrame(rows)
                logger.info(f"Successfully retrieved ad cost data: {len(df)} rows")
                return df
            else:
                logger.warning("No ad cost data found for the specified period")
                # Return empty DataFrame but raise a specific error
                raise ValueError("No advertising cost data found in Google Analytics for the selected period")
                
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
        try:
            df = self.get_ad_costs(start_date, end_date)
            
            if df is None or df.empty:
                logger.warning("No ad cost data available for calculating total spend")
                return {
                    'total_spend': 0,
                    'spend_by_campaign': {},
                    'spend_by_date': {},
                    'has_data': False
                }
        except ValueError as ve:
            # Specific error for no data found
            logger.warning(f"No ad cost data found: {str(ve)}")
            return {
                'total_spend': 0,
                'spend_by_campaign': {},
                'spend_by_date': {},
                'has_data': False,
                'error_message': str(ve)
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
        try:
            df = self.get_ad_costs(start_date, end_date)
            
            if df is None or df.empty:
                logger.warning("No ad cost data available for calculating campaign performance")
                return pd.DataFrame()
        except ValueError as ve:
            # Specific error for no data found
            logger.warning(f"No ad cost data found for campaign performance: {str(ve)}")
            # Create empty DataFrame with error info
            empty_df = pd.DataFrame()
            empty_df.attrs['error_message'] = str(ve)
            return empty_df
        
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