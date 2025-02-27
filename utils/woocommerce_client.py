import streamlit as st
from woocommerce import API
import pandas as pd
from datetime import datetime, timedelta
import os
import requests
from requests.exceptions import SSLError, ConnectionError
from urllib.parse import urlparse
import pytz

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

        except Exception as e:
            st.sidebar.error(f"Failed to initialize WooCommerce client: {str(e)}")
            raise

    def get_orders(self, start_date, end_date):
        """
        Fetch orders from WooCommerce API within the specified date range
        """
        try:
            # Convert dates to UTC for API request
            oslo_tz = pytz.timezone('Europe/Oslo')
            utc_tz = pytz.UTC

            # Convert start and end dates to UTC
            start_date_oslo = oslo_tz.localize(datetime.combine(start_date, datetime.min.time()))
            end_date_oslo = oslo_tz.localize(datetime.combine(end_date, datetime.max.time()))

            start_date_utc = start_date_oslo.astimezone(utc_tz)
            end_date_utc = end_date_oslo.astimezone(utc_tz)

            st.sidebar.write(f"Fetching orders from {start_date} to {end_date}")

            params = {
                "after": start_date_utc.isoformat(),
                "before": end_date_utc.isoformat(),
                "per_page": 100,
                "status": "any"
            }

            st.sidebar.write(f"API Request Parameters: {params}")

            response = self.wcapi.get("orders", params=params)
            st.sidebar.write(f"API Response Status: {response.status_code}")

            try:
                data = response.json()
                if isinstance(data, list):
                    st.sidebar.write(f"Number of orders returned: {len(data)}")
                    if len(data) > 0:
                        st.sidebar.write("First order sample:", {k: v for k, v in data[0].items() if k in ['id', 'status', 'date_created']})
                else:
                    st.sidebar.write(f"API Response Content: {str(data)[:500]}")
            except Exception as e:
                st.sidebar.error(f"Failed to parse JSON response: {str(e)}")
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
            return pd.DataFrame(), pd.DataFrame()

        # Set timezone for processing
        oslo_tz = pytz.timezone('Europe/Oslo')

        order_data = []
        product_data = []

        for order in orders:
            try:
                # Convert UTC timestamp to Oslo timezone
                date_str = order.get('date_created')
                if not date_str:
                    st.sidebar.warning(f"No date found in order: {order}")
                    continue

                # Parse UTC timestamp and convert to Oslo time
                utc_date = pd.to_datetime(date_str)
                order_date = utc_date.tz_localize('UTC').tz_convert(oslo_tz)

                # Process main order data
                order_info = {
                    'date': order_date,
                    'order_id': order.get('id'),
                    'total': float(order.get('total', 0)),  # Total including VAT and shipping
                    'subtotal': sum(float(item.get('subtotal', 0)) for item in order.get('line_items', [])),  # Sum of line items
                    'shipping_total': float(order.get('shipping_total', 0)),  # Base shipping cost
                    'tax_total': float(order.get('total_tax', 0))  # Total VAT
                }

                # Add shipping tax if present
                shipping_lines = order.get('shipping_lines', [])
                if shipping_lines:
                    shipping_tax = sum(float(line.get('total_tax', 0)) for line in shipping_lines)
                    order_info['shipping_total'] += shipping_tax  # Include shipping tax in total shipping cost

                # Debug log for order totals
                st.sidebar.write(f"Processing Order #{order_info['order_id']}:")
                st.sidebar.write(f"Total (incl. VAT & shipping): {order_info['total']}")
                st.sidebar.write(f"Shipping: {order_info['shipping_total']}")
                st.sidebar.write(f"Tax: {order_info['tax_total']}")

                order_data.append(order_info)

                # Process line items (products) with cost information
                for item in order.get('line_items', []):
                    # Extract cost from meta_data
                    cost = 0
                    for meta in item.get('meta_data', []):
                        if meta.get('key') == '_yith_cog_item_cost':
                            try:
                                cost = float(meta.get('value', 0))
                            except (ValueError, TypeError):
                                cost = 0
                            break

                    quantity = int(item.get('quantity', 0))
                    product_data.append({
                        'date': order_date,
                        'product_id': item.get('product_id'),
                        'name': item.get('name'),
                        'quantity': quantity,
                        'total': float(item.get('total', 0)),  # Including VAT
                        'subtotal': float(item.get('subtotal', 0)),
                        'tax': float(item.get('total_tax', 0)),  # VAT
                        'cost': cost * quantity  # Total cost for the quantity ordered
                    })

            except Exception as e:
                st.sidebar.error(f"Error processing order: {str(e)}")
                continue

        # Create DataFrames
        df_orders = pd.DataFrame(order_data)
        df_products = pd.DataFrame(product_data)

        if df_orders.empty:
            st.sidebar.warning("No valid orders found after processing")
            return df_orders, df_products

        # Group orders by date for daily metrics (date is already in Oslo timezone)
        daily_metrics = df_orders.groupby('date').agg({
            'total': 'sum',
            'subtotal': 'sum',
            'shipping_total': 'sum',
            'tax_total': 'sum'
        }).reset_index()

        # Add debug information
        st.sidebar.write(f"Raw order count: {len(orders)}")
        if len(daily_metrics) > 0:
            st.sidebar.write("Sample daily totals:")
            st.sidebar.write(daily_metrics[['date', 'total', 'shipping_total']].to_dict('records'))

        st.sidebar.success(f"Processed {len(daily_metrics)} days of order data")
        st.sidebar.write("Processed data shape:", daily_metrics.shape)

        return daily_metrics, df_products