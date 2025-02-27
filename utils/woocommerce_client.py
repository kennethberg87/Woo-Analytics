from woocommerce import API
import pandas as pd
from datetime import datetime, timedelta
import os
import requests
from requests.exceptions import SSLError, ConnectionError

class WooCommerceClient:
    def __init__(self):
        try:
            self.wcapi = API(
                url=os.getenv('WOOCOMMERCE_URL'),
                consumer_key=os.getenv('WOOCOMMERCE_KEY'),
                consumer_secret=os.getenv('WOOCOMMERCE_SECRET'),
                version="wc/v3",
                verify_ssl=True,
                timeout=30
            )
            # Test connection
            self.wcapi.get("").json()
        except SSLError as e:
            raise Exception("SSL Certificate verification failed. Please ensure your store has a valid SSL certificate.")
        except ConnectionError as e:
            raise Exception(f"Failed to connect to WooCommerce store: {str(e)}")
        except Exception as e:
            raise Exception(f"Failed to initialize WooCommerce client: {str(e)}")

    def get_orders(self, start_date, end_date):
        """
        Fetch orders from WooCommerce API within the specified date range
        """
        try:
            # Convert dates to ISO format
            start_date_iso = start_date.isoformat()
            end_date_iso = (end_date + timedelta(days=1)).isoformat()

            # Fetch orders with pagination
            page = 1
            orders = []

            while True:
                response = self.wcapi.get("orders", params={
                    "after": start_date_iso,
                    "before": end_date_iso,
                    "per_page": 100,
                    "page": page,
                    "status": ["completed", "processing"]
                }).json()

                if not response or not isinstance(response, list):
                    break

                orders.extend(response)
                if len(response) < 100:
                    break

                page += 1

            return orders

        except SSLError as e:
            raise Exception("SSL Certificate verification failed while fetching orders.")
        except ConnectionError as e:
            raise Exception(f"Connection error while fetching orders: {str(e)}")
        except Exception as e:
            raise Exception(f"Error fetching orders: {str(e)}")

    def process_orders_to_df(self, orders):
        """
        Convert orders to pandas DataFrame with daily metrics
        """
        if not orders:
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
                continue  # Skip malformed orders

        # Create DataFrame
        df = pd.DataFrame(order_data)

        if df.empty:
            return df

        # Group by date and calculate daily metrics
        daily_metrics = df.groupby('date').agg({
            'total': 'sum',
            'subtotal': 'sum',
            'shipping_total': 'sum',
            'tax_total': 'sum'
        }).reset_index()

        return daily_metrics