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

            params = {
                "after": start_date_utc.isoformat(),
                "before": end_date_utc.isoformat(),
                "per_page": 100,
                "status": "any"
            }

            st.sidebar.write(f"API Request Parameters: {params}")
            response = self.wcapi.get("orders", params=params)
            data = response.json()

            if isinstance(data, list):
                st.sidebar.write(f"Number of orders returned: {len(data)}")
                for order in data[:1]:  # Log first order for debugging
                    st.sidebar.write("\nFirst order sample:")
                    st.sidebar.write(order)
                return data
            else:
                st.sidebar.error("Invalid response format")
                return []

        except Exception as e:
            st.sidebar.error(f"Error fetching orders: {str(e)}")
            return []

    def process_orders_to_df(self, orders):
        """
        Convert orders to pandas DataFrame with daily metrics and product information
        """
        if not orders:
            return pd.DataFrame(), pd.DataFrame()

        oslo_tz = pytz.timezone('Europe/Oslo')
        order_data = []
        product_data = []

        st.sidebar.write("\n=== Processing Orders ===")

        for order in orders:
            try:
                # Parse and convert date to Oslo timezone
                date_str = order.get('date_created')
                if not date_str:
                    continue

                utc_date = pd.to_datetime(date_str)
                order_date = utc_date.tz_localize('UTC').tz_convert(oslo_tz)

                # Initialize order info
                order_id = order.get('id')
                total = float(order.get('total', 0))
                shipping_base = 0
                shipping_tax = 0
                status = order.get('status', '')  # Get order status

                # Process shipping lines - now separating base and tax
                for shipping in order.get('shipping_lines', []):
                    base = float(shipping.get('total', 0))
                    tax = float(shipping.get('total_tax', 0))
                    shipping_base += base
                    shipping_tax += tax

                # Calculate total shipping (base + tax)
                total_shipping = shipping_base + shipping_tax
                total_tax = float(order.get('total_tax', 0))
                subtotal = sum(float(item.get('subtotal', 0)) for item in order.get('line_items', []))

                # Debug information for each order
                st.sidebar.write(f"\nOrder #{order_id} ({order_date}):")
                st.sidebar.write(f"Status: {status}")
                st.sidebar.write(f"Total (inc VAT): {total}")
                st.sidebar.write(f"Shipping Base (ex VAT): {shipping_base}")
                st.sidebar.write(f"Shipping Tax: {shipping_tax}")
                st.sidebar.write(f"Total Shipping (inc VAT): {total_shipping}")
                st.sidebar.write(f"Total Tax: {total_tax}")

                # Create order record - now including status
                order_info = {
                    'date': order_date,
                    'order_id': order_id,
                    'status': status,
                    'total': total,
                    'subtotal': subtotal,
                    'shipping_base': shipping_base,  # Base shipping cost (ex VAT)
                    'shipping_total': total_shipping,  # Total shipping (inc VAT)
                    'shipping_tax': shipping_tax,  # Shipping VAT
                    'tax_total': total_tax
                }

                order_data.append(order_info)

                # Process line items (unchanged)
                for item in order.get('line_items', []):
                    quantity = int(item.get('quantity', 0))
                    cost = 0
                    for meta in item.get('meta_data', []):
                        if meta.get('key') == '_yith_cog_item_cost':
                            try:
                                cost = float(meta.get('value', 0))
                            except (ValueError, TypeError):
                                cost = 0
                            break

                    product_data.append({
                        'date': order_date,
                        'product_id': item.get('product_id'),
                        'name': item.get('name'),
                        'quantity': quantity,
                        'total': float(item.get('total', 0)),
                        'subtotal': float(item.get('subtotal', 0)),
                        'tax': float(item.get('total_tax', 0)),
                        'cost': cost * quantity
                    })

            except Exception as e:
                st.sidebar.error(f"Error processing order {order.get('id')}: {str(e)}")
                continue

        df_orders = pd.DataFrame(order_data)
        df_products = pd.DataFrame(product_data)

        if df_orders.empty:
            return df_orders, df_products

        # Group orders by date for daily metrics
        daily_metrics = df_orders.groupby('date').agg({
            'total': 'sum',
            'subtotal': 'sum',
            'shipping_base': 'sum',  # Base shipping ex VAT
            'shipping_total': 'sum',  # Total shipping inc VAT
            'shipping_tax': 'sum',  # Shipping VAT
            'tax_total': 'sum',
            'status': lambda x: list(x)  # Include status in aggregation
        }).reset_index()

        st.sidebar.write("\n=== Daily Totals ===")
        for _, row in daily_metrics.iterrows():
            st.sidebar.write(f"\nDate: {row['date'].strftime('%Y-%m-%d')}")
            st.sidebar.write(f"Total Order Sum: {row['total']:.2f}")
            st.sidebar.write(f"Shipping Base (ex VAT): {row['shipping_base']:.2f}")
            st.sidebar.write(f"Shipping Tax: {row['shipping_tax']:.2f}")
            st.sidebar.write(f"Total Tax: {row['tax_total']:.2f}")
            st.sidebar.write(f"Order Statuses: {row['status']}")

        return daily_metrics, df_products