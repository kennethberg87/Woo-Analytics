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

            # Test basic orders endpoint
            st.sidebar.write("Testing orders endpoint...")
            test_response = self.wcapi.get("orders", params={"per_page": 1})
            st.sidebar.write(f"Test orders response status: {test_response.status_code}")
            test_data = test_response.json()
            st.sidebar.write(f"Orders endpoint test: {'Successful' if isinstance(test_data, list) else 'Failed'}")
            if isinstance(test_data, dict) and 'message' in test_data:
                st.sidebar.error(f"Orders endpoint error: {test_data['message']}")

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

            st.sidebar.write(f"Fetching orders from {start_date_iso} to {end_date_iso}")

            # Fetch orders with pagination
            page = 1
            orders = []

            while True:
                params = {
                    "modified_after": f"{start_date_iso}T00:00:00",  # HPOS uses modified_after
                    "modified_before": f"{end_date_iso}T23:59:59",  # HPOS uses modified_before
                    "per_page": 100,
                    "page": page,
                    "status": ["completed", "processing", "on-hold", "pending"],  # Added more statuses
                    "orderby": "modified",  # HPOS uses modified date
                    "order": "desc"
                }

                st.sidebar.write(f"API Request Parameters: {params}")
                response = self.wcapi.get("orders", params=params)
                st.sidebar.write(f"API Response Status: {response.status_code}")

                try:
                    data = response.json()
                    if isinstance(data, dict) and 'message' in data:
                        st.sidebar.error(f"API Error: {data['message']}")
                        break
                except Exception as e:
                    st.sidebar.error(f"Failed to parse JSON response: {str(e)}")
                    st.sidebar.error(f"Raw response: {response.text[:500]}")  # First 500 chars for debugging
                    raise Exception("Failed to parse API response")

                if not isinstance(data, list):
                    st.sidebar.write("No orders returned from API")
                    st.sidebar.write(f"Full API Response: {data}")  # Add full response logging
                    break

                orders.extend(data)
                st.sidebar.write(f"Found {len(data)} orders on page {page}")

                # Break if we received fewer orders than the page size
                if len(data) < 100:
                    break

                page += 1

            st.sidebar.success(f"Total orders fetched: {len(orders)}")
            return orders

        except SSLError as e:
            st.sidebar.error("SSL Certificate verification failed while fetching orders.")
            raise Exception("SSL Certificate verification failed while fetching orders.")
        except ConnectionError as e:
            st.sidebar.error(f"Connection error while fetching orders: {str(e)}")
            raise Exception(f"Connection error while fetching orders: {str(e)}")
        except Exception as e:
            st.sidebar.error(f"Error fetching orders: {str(e)}")
            raise Exception(f"Error fetching orders: {str(e)}")

    def process_orders_to_df(self, orders):
        """
        Convert orders to pandas DataFrame with daily metrics
        """
        if not orders:
            st.sidebar.write("No orders to process")
            return pd.DataFrame(columns=['date', 'total', 'subtotal', 'shipping_total', 'tax_total'])

        # Extract relevant data from orders
        order_data = []
        for order in orders:
            try:
                # HPOS response format might be different
                date_created = order.get('date_modified', order.get('date_created', ''))
                order_data.append({
                    'date': datetime.fromisoformat(date_created.replace('Z', '+00:00')).date(),
                    'total': float(order.get('total', 0)),
                    'subtotal': float(order.get('subtotal', 0)),
                    'shipping_total': float(order.get('shipping_total', 0)),
                    'tax_total': float(order.get('total_tax', 0))
                })
            except (KeyError, ValueError) as e:
                st.sidebar.error(f"Error processing order: {str(e)}")
                st.sidebar.error(f"Problematic order data: {order}")
                continue  # Skip malformed orders

        # Create DataFrame
        df = pd.DataFrame(order_data)

        if df.empty:
            st.sidebar.warning("No valid orders found after processing")
            return df

        # Group by date and calculate daily metrics
        daily_metrics = df.groupby('date').agg({
            'total': 'sum',
            'subtotal': 'sum',
            'shipping_total': 'sum',
            'tax_total': 'sum'
        }).reset_index()

        st.sidebar.success(f"Processed {len(daily_metrics)} days of order data")
        return daily_metrics