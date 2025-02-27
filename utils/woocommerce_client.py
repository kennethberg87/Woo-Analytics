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

    def get_payment_method_display(self, payment_method):
        """Convert payment method code to display name"""
        if not payment_method:
            return "Ukjent"

        payment_methods = {
            'Klarna': 'Klarna',
            'BamboraVipps': 'Vipps',
            'Vipps': 'Vipps',
            'BamboraApplepay': 'Apple Pay',
            'BamboraGooglepay': 'Google Pay',
            'CollectorInvoice': 'Faktura',
            'BamboraCreditcard': 'Kortbetaling',
            'CollectorInstallment': 'Walley Delbetaling'
        }

        return payment_methods.get(payment_method, "Ukjent")

    def get_dintero_payment_method(self, meta_data):
        """Extract Dintero payment method from order meta data"""
        for meta in meta_data:
            if meta.get('key') == '_dintero_payment_method':
                method = meta.get('value', '')
                return self.get_payment_method_display(method)
        return 'Ukjent'

    def get_shipping_method(self, shipping_lines):
        """Extract shipping method from order shipping lines"""
        if shipping_lines and len(shipping_lines) > 0:
            return shipping_lines[0].get('method_title', '')
        return ''

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
                status = order.get('status', '')
                shipping_base = 0
                shipping_tax = 0

                # Process shipping lines
                shipping_lines = order.get('shipping_lines', [])
                for shipping in shipping_lines:
                    base = float(shipping.get('total', 0))
                    tax = float(shipping.get('total_tax', 0))
                    shipping_base += base
                    shipping_tax += tax

                # Calculate total shipping
                total_shipping = shipping_base + shipping_tax
                total_tax = float(order.get('total_tax', 0))
                subtotal = sum(float(item.get('subtotal', 0)) for item in order.get('line_items', []))

                # Get billing information
                billing = order.get('billing', {})

                # Get Dintero payment method and shipping method
                dintero_method = self.get_dintero_payment_method(order.get('meta_data', []))
                shipping_method = self.get_shipping_method(shipping_lines)

                # Create order record
                order_info = {
                    'date': order_date,
                    'order_id': order_id,
                    'status': status,
                    'total': total,
                    'subtotal': subtotal,
                    'shipping_base': shipping_base,
                    'shipping_total': total_shipping,
                    'shipping_tax': shipping_tax,
                    'tax_total': total_tax,
                    'billing': billing,
                    'dintero_payment_method': dintero_method,
                    'shipping_method': shipping_method
                }

                order_data.append(order_info)

                # Process line items
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

        # Create DataFrames from collected data
        df_orders = pd.DataFrame(order_data)
        df_products = pd.DataFrame(product_data)

        if df_orders.empty:
            return df_orders, df_products

        # Do not aggregate by date - return the full orders DataFrame to preserve status and billing info
        return df_orders, df_products