import streamlit as st
from woocommerce import API
import pandas as pd
from datetime import datetime, timedelta
import os
import requests
from requests.exceptions import SSLError, ConnectionError
from urllib.parse import urlparse

class WooCommerceClient:
    def __init__(self):
        try:
            # Validate store URL
            store_url = os.getenv('WOOCOMMERCE_URL')
            st.sidebar.write("Testing WooCommerce configuration...")
            st.sidebar.write(f"Store URL structure: {urlparse(store_url).scheme}://{urlparse(store_url).netloc}")

            if not store_url:
                raise ValueError("WooCommerce store URL is not configured")

            parsed_url = urlparse(store_url)
            if not parsed_url.scheme or not parsed_url.netloc:
                raise ValueError("Invalid WooCommerce store URL format")

            # Test basic connectivity first
            try:
                st.sidebar.write("Testing basic store connectivity...")
                response = requests.get(store_url, verify=False, timeout=30)
                st.sidebar.write(f"Basic connectivity test response: {response.status_code}")
            except Exception as e:
                st.sidebar.error(f"Basic connectivity test failed: {str(e)}")
                raise ConnectionError(f"Cannot connect to store URL: {str(e)}")

            # Initialize API client
            st.sidebar.write("Initializing WooCommerce API client...")
            self.wcapi = API(
                url=store_url,
                consumer_key=os.getenv('WOOCOMMERCE_KEY'),
                consumer_secret=os.getenv('WOOCOMMERCE_SECRET'),
                version="wc/v3",
                verify_ssl=False,  # Temporarily disable SSL verification for testing
                timeout=30
            )

            # Test connection with detailed error handling
            st.sidebar.write("Testing WooCommerce API connection...")
            response = self.wcapi.get("")
            st.sidebar.write(f"WooCommerce API Test Response: {response.status_code}")

            if response.status_code == 401:
                raise ValueError("Invalid API credentials (Unauthorized)")
            elif response.status_code != 200:
                error_data = response.json() if response.headers.get('content-type', '').startswith('application/json') else None
                error_message = error_data.get('message') if error_data else 'Unknown error'
                st.sidebar.error(f"API Error Response: {error_message}")
                raise Exception(f"API test failed with status {response.status_code}: {error_message}")

            response.json()  # Validate JSON response
            st.sidebar.success("Successfully connected to WooCommerce API")

        except SSLError as e:
            st.sidebar.error("SSL Certificate verification failed. Please ensure your store has a valid SSL certificate.")
            raise Exception(f"SSL Certificate verification failed: {str(e)}")
        except ConnectionError as e:
            st.sidebar.error(f"Failed to connect to WooCommerce store: {str(e)}")
            raise Exception(f"Failed to connect to WooCommerce store: {str(e)}")
        except ValueError as e:
            st.sidebar.error(str(e))
            raise
        except Exception as e:
            st.sidebar.error(f"Failed to initialize WooCommerce client: {str(e)}")
            raise Exception(f"Failed to initialize WooCommerce client: {str(e)}")

    def get_orders(self, start_date, end_date):
        """
        Fetch orders from WooCommerce API within the specified date range
        """
        try:
            # Convert dates to ISO format
            start_date_iso = start_date.isoformat()
            end_date_iso = (end_date + timedelta(days=1)).isoformat()

            st.debug(f"Fetching orders from {start_date_iso} to {end_date_iso}")

            # Fetch orders with pagination
            page = 1
            orders = []

            while True:
                params = {
                    "after": start_date_iso,
                    "before": end_date_iso,
                    "per_page": 100,
                    "page": page,
                    "status": ["completed", "processing", "on-hold"]  # Added more order statuses
                }

                st.debug(f"API Request Parameters: {params}")
                response = self.wcapi.get("orders", params=params)
                st.debug(f"API Response Status: {response.status_code}")

                try:
                    data = response.json()
                except Exception as e:
                    st.debug(f"Failed to parse JSON response: {str(e)}")
                    st.debug(f"Raw response: {response.text[:500]}")  # First 500 chars for debugging
                    raise Exception("Failed to parse API response")

                if not data or not isinstance(data, list):
                    st.debug(f"API Response: {data}")
                    break

                orders.extend(data)
                st.debug(f"Found {len(data)} orders on page {page}")

                if len(data) < 100:
                    break

                page += 1

            st.debug(f"Total orders fetched: {len(orders)}")
            return orders

        except SSLError as e:
            st.error("SSL Certificate verification failed while fetching orders.")
            raise Exception("SSL Certificate verification failed while fetching orders.")
        except ConnectionError as e:
            st.error(f"Connection error while fetching orders: {str(e)}")
            raise Exception(f"Connection error while fetching orders: {str(e)}")
        except Exception as e:
            st.error(f"Error fetching orders: {str(e)}")
            raise Exception(f"Error fetching orders: {str(e)}")

    def process_orders_to_df(self, orders):
        """
        Convert orders to pandas DataFrame with daily metrics
        """
        if not orders:
            st.debug("No orders to process")
            return pd.DataFrame(columns=['date', 'total', 'subtotal', 'shipping_total', 'tax_total'])

        # Extract relevant data from orders
        order_data = []
        for order in orders:
            try:
                order_data.append({
                    'date': datetime.fromisoformat(order['date_created']).date(),
                    'total': float(order['total']),
                    'subtotal': float(order['subtotal']),
                    'shipping_total': float(order['shipping_total']),
                    'tax_total': float(order['total_tax'])
                })
            except (KeyError, ValueError) as e:
                st.debug(f"Error processing order: {str(e)}")
                st.debug(f"Problematic order data: {order}")
                continue  # Skip malformed orders

        # Create DataFrame
        df = pd.DataFrame(order_data)

        if df.empty:
            st.debug("No valid orders found after processing")
            return df

        # Group by date and calculate daily metrics
        daily_metrics = df.groupby('date').agg({
            'total': 'sum',
            'subtotal': 'sum',
            'shipping_total': 'sum',
            'tax_total': 'sum'
        }).reset_index()

        st.debug(f"Processed {len(daily_metrics)} days of order data")
        return daily_metrics