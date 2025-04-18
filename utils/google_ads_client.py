import logging
import os
from datetime import datetime, timedelta
from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException

logger = logging.getLogger(__name__)

class GoogleAdsClient:
    """Client for interacting with Google Ads API to fetch advertising costs and campaign data"""
    
    def __init__(self):
        self.client = None
        self.is_initialized = False
        
        # Try to initialize client if environment variables are set
        try:
            self._initialize_client()
        except Exception as e:
            logger.warning(f"Google Ads client initialization failed: {str(e)}")
    
    def _initialize_client(self):
        """Initialize the Google Ads API client using environment variables"""
        required_vars = [
            "GOOGLE_ADS_CLIENT_ID", 
            "GOOGLE_ADS_CLIENT_SECRET", 
            "GOOGLE_ADS_REFRESH_TOKEN",
            "GOOGLE_ADS_DEVELOPER_TOKEN",
            "GOOGLE_ADS_LOGIN_CUSTOMER_ID"
        ]
        
        # Check if all required environment variables are set
        for var in required_vars:
            if not os.environ.get(var):
                raise ValueError(f"Missing required environment variable: {var}")
        
        # Create credentials dictionary from environment variables
        credentials = {
            "developer_token": os.environ.get("GOOGLE_ADS_DEVELOPER_TOKEN"),
            "refresh_token": os.environ.get("GOOGLE_ADS_REFRESH_TOKEN"),
            "client_id": os.environ.get("GOOGLE_ADS_CLIENT_ID"),
            "client_secret": os.environ.get("GOOGLE_ADS_CLIENT_SECRET"),
            "login_customer_id": os.environ.get("GOOGLE_ADS_LOGIN_CUSTOMER_ID"),
            "use_proto_plus": True,
        }
        
        # Initialize the client
        try:
            self.client = GoogleAdsClient.load_from_dict(credentials)
            self.is_initialized = True
        except Exception as e:
            logger.error(f"Failed to initialize Google Ads client: {str(e)}")
            raise
    
    def get_campaign_costs(self, customer_id, start_date, end_date):
        """
        Get campaign costs for a specific date range
        
        Args:
            customer_id (str): Google Ads customer ID without dashes
            start_date (datetime): Start date for the query
            end_date (datetime): End date for the query
            
        Returns:
            dict: Campaign costs data with campaign names and costs
        """
        if not self.is_initialized:
            try:
                self._initialize_client()
            except Exception as e:
                logger.error(f"Google Ads client not initialized: {str(e)}")
                return None
        
        # Format dates for Google Ads API
        start_date_str = start_date.strftime("%Y-%m-%d")
        end_date_str = end_date.strftime("%Y-%m-%d")
        
        # Construct the query
        query = f"""
            SELECT 
                campaign.id, 
                campaign.name, 
                metrics.cost_micros,
                metrics.impressions,
                metrics.clicks,
                metrics.conversions
            FROM campaign
            WHERE 
                segments.date BETWEEN '{start_date_str}' AND '{end_date_str}'
        """
        
        try:
            # Create the Google Ads service client
            google_ads_service = self.client.get_service("GoogleAdsService")
            
            # Issue the search request
            search_request = {
                "customer_id": customer_id,
                "query": query,
                "page_size": 1000  # Adjust as needed
            }
            
            # Execute the query
            response = google_ads_service.search(request=search_request)
            
            # Process results
            campaign_costs = {}
            total_cost = 0
            total_impressions = 0
            total_clicks = 0
            total_conversions = 0
            
            # Extract data from response
            for row in response:
                campaign_id = row.campaign.id
                campaign_name = row.campaign.name
                # Convert micros to actual currency (micros are millionths of the currency unit)
                cost = row.metrics.cost_micros / 1000000
                impressions = row.metrics.impressions
                clicks = row.metrics.clicks
                conversions = row.metrics.conversions
                
                # Add to campaign data
                campaign_costs[campaign_id] = {
                    "name": campaign_name,
                    "cost": cost,
                    "impressions": impressions,
                    "clicks": clicks, 
                    "conversions": conversions
                }
                
                # Update totals
                total_cost += cost
                total_impressions += impressions
                total_clicks += clicks
                total_conversions += conversions
            
            # Add summary data
            result = {
                "campaigns": campaign_costs,
                "summary": {
                    "total_cost": total_cost,
                    "total_impressions": total_impressions,
                    "total_clicks": total_clicks,
                    "total_conversions": total_conversions,
                    "start_date": start_date_str,
                    "end_date": end_date_str
                }
            }
            
            return result
            
        except GoogleAdsException as ex:
            logger.error(f"Request with ID '{ex.request_id}' failed with status {ex.error.code().name}")
            for error in ex.failure.errors:
                logger.error(f"\tError with message '{error.message}'.")
                if error.location:
                    for field_path_element in error.location.field_path_elements:
                        logger.error(f"\t\tOn field: {field_path_element.field_name}")
            return None
        except Exception as e:
            logger.error(f"Google Ads API error: {str(e)}")
            return None
    
    def get_ad_cost_by_date(self, customer_id, start_date, end_date):
        """
        Get daily advertising costs for a specific date range
        
        Args:
            customer_id (str): Google Ads customer ID without dashes
            start_date (datetime): Start date for the query
            end_date (datetime): End date for the query
            
        Returns:
            dict: Daily advertising costs with dates as keys
        """
        if not self.is_initialized:
            try:
                self._initialize_client()
            except Exception as e:
                logger.error(f"Google Ads client not initialized: {str(e)}")
                return None
        
        # Format dates for Google Ads API
        start_date_str = start_date.strftime("%Y-%m-%d")
        end_date_str = end_date.strftime("%Y-%m-%d")
        
        # Construct the query with date segmentation
        query = f"""
            SELECT 
                segments.date,
                metrics.cost_micros,
                metrics.impressions,
                metrics.clicks,
                metrics.conversions
            FROM campaign
            WHERE 
                segments.date BETWEEN '{start_date_str}' AND '{end_date_str}'
        """
        
        try:
            # Create the Google Ads service client
            google_ads_service = self.client.get_service("GoogleAdsService")
            
            # Issue the search request
            search_request = {
                "customer_id": customer_id,
                "query": query,
                "page_size": 1000
            }
            
            # Execute the query
            response = google_ads_service.search(request=search_request)
            
            # Process results
            daily_costs = {}
            
            # Extract data from response
            for row in response:
                date_str = str(row.segments.date)
                # Convert micros to actual currency (micros are millionths of the currency unit)
                cost = row.metrics.cost_micros / 1000000
                impressions = row.metrics.impressions
                clicks = row.metrics.clicks
                conversions = row.metrics.conversions
                
                # Initialize date entry if it doesn't exist
                if date_str not in daily_costs:
                    daily_costs[date_str] = {
                        "cost": 0,
                        "impressions": 0,
                        "clicks": 0,
                        "conversions": 0
                    }
                
                # Add metrics to the date
                daily_costs[date_str]["cost"] += cost
                daily_costs[date_str]["impressions"] += impressions
                daily_costs[date_str]["clicks"] += clicks
                daily_costs[date_str]["conversions"] += conversions
            
            return daily_costs
            
        except GoogleAdsException as ex:
            logger.error(f"Request with ID '{ex.request_id}' failed with status {ex.error.code().name}")
            for error in ex.failure.errors:
                logger.error(f"\tError with message '{error.message}'.")
                if error.location:
                    for field_path_element in error.location.field_path_elements:
                        logger.error(f"\t\tOn field: {field_path_element.field_name}")
            return None
        except Exception as e:
            logger.error(f"Google Ads API error: {str(e)}")
            return None
    
    def get_total_ad_cost(self, customer_id, start_date, end_date):
        """
        Get total advertising cost for a specific date range
        
        Args:
            customer_id (str): Google Ads customer ID without dashes
            start_date (datetime): Start date for the query
            end_date (datetime): End date for the query
            
        Returns:
            float: Total advertising cost
        """
        campaign_data = self.get_campaign_costs(customer_id, start_date, end_date)
        if campaign_data and "summary" in campaign_data:
            return campaign_data["summary"]["total_cost"]
        return 0
    
    def is_configured(self):
        """Check if the Google Ads client is properly configured"""
        return self.is_initialized