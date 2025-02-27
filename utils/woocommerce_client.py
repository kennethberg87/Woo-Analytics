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
            if not store_url:
                raise ValueError("WooCommerce store URL is not configured")

            parsed_url = urlparse(store_url)
            if not parsed_url.scheme or not parsed_url.netloc:
                raise ValueError("Invalid WooCommerce store URL format")

            # Initialize API client
            self.wcapi = API(
                url=store_url,
                consumer_key=os.getenv('WOOCOMMERCE_KEY'),
                consumer_secret=os.getenv('WOOCOMMERCE_SECRET'),
                version="wc/v3",
                verify_ssl=False,
                timeout=30
            )

            # Test API connection
            response = self.wcapi.get("")
            if response.status_code == 401:
                raise ValueError("Invalid API credentials (Unauthorized)")
            elif response.status_code != 200:
                error_data = response.json() if response.headers.get('content-type', '').startswith('application/json') else None
                error_message = error_data.get('message') if error_data else 'Unknown error'
                raise Exception(f"API test failed with status {response.status_code}: {error_message}")

            # Test orders endpoint
            test_response = self.wcapi.get("orders", params={"per_page": 1})
            if test_response.status_code != 200:
                raise Exception(f"Orders endpoint test failed with status {test_response.status_code}")

            test_data = test_response.json()
            if not isinstance(test_data, list):
                st.sidebar.error(f"Unexpected orders endpoint response format: {test_data}")

        except Exception as e:
            st.sidebar.error(f"Failed to initialize WooCommerce client: {str(e)}")
            raise

    def get_orders(self, start_date, end_date):
        """
        Fetch orders from WooCommerce API within the specified date range
        """
        try:
            # Convert dates to ISO format
            start_date_iso = start_date.isoformat()
            end_date_iso = end_date.isoformat()

            st.sidebar.write(f"Fetching orders from {start_date_iso} to {end_date_iso}")

            # Simplify the query parameters to basic WooCommerce v3 format
            params = {
                "after": f"{start_date_iso}T00:00:00",
                "before": f"{end_date_iso}T23:59:59",
                "per_page": 100,
                "status": "any"  # Try fetching all order statuses
            }

            st.sidebar.write(f"API Request Parameters: {params}")

            # Add detailed response logging
            response = self.wcapi.get("orders", params=params)
            st.sidebar.write(f"API Response Status: {response.status_code}")
            st.sidebar.write(f"API Response Headers: {dict(response.headers)}")

            try:
                data = response.json()
                st.sidebar.write(f"API Response Type: {type(data)}")
                if isinstance(data, list):
                    st.sidebar.write(f"Number of orders returned: {len(data)}")
                    if len(data) > 0:
                        st.sidebar.write("First order sample:", {k: v for k, v in data[0].items() if k in ['id', 'status', 'date_created']})
                else:
                    st.sidebar.write(f"API Response Content: {str(data)[:500]}")
            except Exception as e:
                st.sidebar.error(f"Failed to parse JSON response: {str(e)}")
                st.sidebar.error(f"Raw response: {response.text[:500]}")
                return []

            if isinstance(data, dict):
                st.sidebar.error(f"API Error Response: {data}")
                return []
            elif not isinstance(data, list):
                st.sidebar.error(f"Unexpected response format: {type(data)}")
                return []

            st.sidebar.success(f"Successfully fetched {len(data)} orders")
            return data

        except Exception as e:
            st.sidebar.error(f"Error fetching orders: {str(e)}")
            return []

    def process_orders_to_df(self, orders):
        """
        Convert orders to pandas DataFrame with daily metrics and product information
        """
        if not orders:
            st.sidebar.write("No orders to process")
            return pd.DataFrame(columns=['date', 'total', 'subtotal', 'shipping_total', 'tax_total']), pd.DataFrame()

        # Extract relevant data from orders
        order_data = []
        product_data = []

        for order in orders:
            try:
                # Try multiple date fields
                date_str = order.get('date_modified') or order.get('date_created') or order.get('date_modified_gmt') or order.get('date_created_gmt')
                if not date_str:
                    st.sidebar.warning(f"No date found in order: {order}")
                    continue

                # Remove timezone suffix if present and convert to datetime
                date_str = date_str.replace('Z', '+00:00')
                order_date = pd.to_datetime(date_str)

                # Process main order data
                order_data.append({
                    'date': order_date,
                    'total': float(order.get('total', 0)),
                    'subtotal': float(order.get('subtotal', 0)),
                    'shipping_total': float(order.get('shipping_total', 0)),
                    'tax_total': float(order.get('total_tax', 0))
                })

                # Process line items (products)
                for item in order.get('line_items', []):
                    product_data.append({
                        'date': order_date,
                        'product_id': item.get('product_id'),
                        'name': item.get('name'),
                        'quantity': int(item.get('quantity', 0)),
                        'total': float(item.get('total', 0)),
                        'subtotal': float(item.get('subtotal', 0)),
                        'tax': float(item.get('total_tax', 0))
                    })

            except Exception as e:
                st.sidebar.error(f"Error processing order: {str(e)}")
                st.sidebar.error(f"Problematic order data: {order}")
                continue

        # Create main orders DataFrame
        df_orders = pd.DataFrame(order_data)
        if df_orders.empty:
            st.sidebar.warning("No valid orders found after processing")
            return df_orders, pd.DataFrame()

        # Create products DataFrame
        df_products = pd.DataFrame(product_data)

        # Ensure date columns are datetime
        df_orders['date'] = pd.to_datetime(df_orders['date'])
        if not df_products.empty:
            df_products['date'] = pd.to_datetime(df_products['date'])

        # Group orders by date for daily metrics
        daily_metrics = df_orders.groupby('date').agg({
            'total': 'sum',
            'subtotal': 'sum',
            'shipping_total': 'sum',
            'tax_total': 'sum'
        }).reset_index()

        st.sidebar.success(f"Processed {len(daily_metrics)} days of order data")
        return daily_metrics, df_products