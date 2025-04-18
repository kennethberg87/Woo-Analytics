import streamlit as st
from woocommerce import API
import pandas as pd
from datetime import datetime, timedelta
import os
import requests
from requests.exceptions import SSLError, ConnectionError
from urllib.parse import urlparse
import pytz
import logging
import concurrent.futures

logging.basicConfig(level=logging.DEBUG) #Added logging configuration

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

            # Initialize API client with optimized settings
            self.wcapi = API(url=store_url,
                                  consumer_key=os.getenv('WOOCOMMERCE_KEY'),
                                  consumer_secret=os.getenv('WOOCOMMERCE_SECRET'),
                                  version="wc/v3",
                                  verify_ssl=False,
                                  timeout=30)

            # Initialize cache
            self.stock_cache = {}
            self.cache_timestamp = None
            self.cache_duration = timedelta(minutes=5)  # Cache valid for 5 minutes

        except Exception as e:
            st.sidebar.error(f"Failed to initialize WooCommerce client: {str(e)}")
            raise

    def get_stock_quantities_batch(self, product_ids):
        """Get stock quantities for multiple products in one API call"""
        try:
            # Check cache first
            now = datetime.now()
            if self.cache_timestamp and (now - self.cache_timestamp) < self.cache_duration:
                # Return cached values if available
                return {pid: self.stock_cache.get(pid) for pid in product_ids}

            # Fetch products in batches of 100
            batch_size = 100
            all_stock = {}

            for i in range(0, len(product_ids), batch_size):
                batch_ids = list(product_ids)[i:i + batch_size]
                products_query = ",".join(map(str, batch_ids))

                try:
                    response = self.wcapi.get("products", params={
                        "include": products_query,
                        "per_page": batch_size,
                        "status": "any"  # Include all product statuses
                    })

                    products = response.json()

                    if not isinstance(products, list):
                        logging.error(f"Invalid response format for products: {products}")
                        continue

                    for product in products:
                        pid = product.get('id')
                        if pid is None:
                            continue

                        stock = product.get('stock_quantity')
                        # If stock is None, try to get it from the parent product
                        if stock is None and product.get('parent_id'):
                            parent_response = self.wcapi.get(f"products/{product['parent_id']}")
                            parent_product = parent_response.json()
                            stock = parent_product.get('stock_quantity')

                        logging.debug(f"Product {pid} stock quantity: {stock}")
                        all_stock[pid] = 0 if stock is None else stock
                        self.stock_cache[pid] = 0 if stock is None else stock  # Update cache

                except Exception as e:
                    logging.error(f"Error fetching batch {i}: {str(e)}")
                    continue

            # Update cache timestamp
            self.cache_timestamp = now

            # Log the final stock quantities
            logging.debug(f"Final stock quantities: {all_stock}")
            return all_stock

        except Exception as e:
            logging.error(f"Error fetching stock quantities: {str(e)}")
            # Return 0 instead of None for missing stock quantities
            return {pid: 0 for pid in product_ids}

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

    def get_invoice_details(self, meta_data):
        """Extract invoice details from order meta data"""
        invoice_details = {
            'invoice_number': '',
            'invoice_date': None,
            'order_number': ''
        }

        for meta in meta_data:
            if meta.get('key') == '_wcpdf_invoice_number':
                invoice_details['invoice_number'] = meta.get('value', '')
            elif meta.get('key') == '_wcpdf_invoice_date_formatted':
                invoice_details['invoice_date'] = meta.get('value', '')
            elif meta.get('key') == '_order_number_formatted':
                invoice_details['order_number'] = meta.get('value', '')

        return invoice_details

    def get_invoice_url(self, order_id):
        """Generate invoice download URL"""
        try:
            # Get base store URL
            store_url = os.getenv('WOOCOMMERCE_URL')
            if not store_url:
                logging.error("WooCommerce store URL not configured")
                return None

            # Remove trailing slash if present
            store_url = store_url.rstrip('/')

            # For PDF Invoices & Packing Slips plugin, we need to construct a URL that includes
            # the direct download endpoint with a static hash
            invoice_url = f"{store_url}/wcpdf/invoice/{order_id}/9e9c036d2f/pdf"

            logging.debug(f"Generated invoice URL: {invoice_url}")
            return invoice_url

        except Exception as e:
            logging.error(f"Error getting invoice URL for order {order_id}: {str(e)}")
            return None

    def get_order_number(self, meta_data):
        """Extract formatted order number from order meta data"""
        for meta in meta_data:
            if meta.get('key') == '_order_number_formatted':
                return meta.get('value', '')
        return ''

    def get_orders(self, start_date, end_date):
        """Fetch orders from WooCommerce API within the specified date range"""
        try:
            # Convert dates to UTC for API request
            oslo_tz = pytz.timezone('Europe/Oslo')
            utc_tz = pytz.UTC

            # Convert start and end dates to UTC
            start_date_oslo = oslo_tz.localize(
                datetime.combine(start_date, datetime.min.time()))
            end_date_oslo = oslo_tz.localize(
                datetime.combine(end_date, datetime.max.time()))

            start_date_utc = start_date_oslo.astimezone(utc_tz)
            end_date_utc = end_date_oslo.astimezone(utc_tz)

            all_orders = []
            page = 1
            per_page = 100  # Maximum allowed by WooCommerce API

            with st.spinner('Henter ordrer...'):
                progress_bar = st.progress(0)

                while True:
                    logging.debug(f"Fetching orders page {page}")
                    start_time = datetime.now()

                    params = {
                        "after": start_date_utc.isoformat(),
                        "before": end_date_utc.isoformat(),
                        "per_page": per_page,
                        "page": page,
                        "status": "any"
                    }

                    response = self.wcapi.get("orders", params=params)
                    data = response.json()

                    if not isinstance(data, list):
                        logging.error("Invalid response format")
                        break

                    if not data:  # No more orders
                        break

                    all_orders.extend(data)

                    # Update progress bar
                    progress = min(1.0, page * per_page / (len(all_orders) + per_page))
                    progress_bar.progress(progress)

                    # Check if we've received less than per_page items
                    if len(data) < per_page:
                        break

                    page += 1

                    # Log performance metrics
                    end_time = datetime.now()
                    duration = (end_time - start_time).total_seconds()
                    logging.debug(f"Page {page} fetched in {duration:.2f} seconds")

                progress_bar.empty()

            logging.debug(f"Total orders fetched: {len(all_orders)}")
            return all_orders

        except Exception as e:
            logging.error(f"Error fetching orders: {str(e)}")
            return []

    def process_orders_to_df(self, orders):
        """Convert orders to pandas DataFrame with daily metrics and product information"""
        if not orders:
            return pd.DataFrame(), pd.DataFrame()

        oslo_tz = pytz.timezone('Europe/Oslo')
        order_data = []
        product_data = []

        # Collect all product IDs first
        product_ids = set()
        for order in orders:
            for item in order.get('line_items', []):
                product_ids.add(item.get('product_id'))

        # Batch fetch stock quantities
        with st.spinner('Henter lagerstatus...'):
            stock_quantities = self.get_stock_quantities_batch(product_ids)

        logging.debug(f"Processing {len(orders)} orders")
        start_time = datetime.now()

        # Process orders with progress bar
        with st.spinner('Behandler ordrer...'):
            progress_bar = st.progress(0)

            for i, order in enumerate(orders):
                try:
                    # Update progress
                    progress = (i + 1) / len(orders)
                    progress_bar.progress(progress)

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
                    subtotal = sum(float(item.get('subtotal', 0))
                                   for item in order.get('line_items', []))

                    # Get billing information
                    billing = order.get('billing', {})

                    # Get order number and payment method
                    order_number = self.get_order_number(order.get('meta_data', []))
                    dintero_method = self.get_dintero_payment_method(
                        order.get('meta_data', []))
                    shipping_method = self.get_shipping_method(shipping_lines)
                    invoice_details = self.get_invoice_details(order.get('meta_data', []))

                    # Create order record
                    order_info = {
                        'date': order_date,
                        'order_id': order_id,
                        'order_number': order_number,
                        'status': self.get_order_status_display(status), # Apply translation here
                        'total': total,
                        'subtotal': subtotal,
                        'shipping_base': shipping_base,
                        'shipping_total': total_shipping,
                        'shipping_tax': shipping_tax,
                        'tax_total': total_tax,
                        'billing': billing,
                        'dintero_payment_method': dintero_method,
                        'shipping_method': shipping_method,
                        'invoice_number': invoice_details['invoice_number'],
                        'invoice_date': invoice_details['invoice_date']
                        # Removed meta_data to avoid pyarrow conversions issues
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

                        # Get stock quantity from cached data
                        product_id = item.get('product_id')
                        stock_quantity = stock_quantities.get(product_id)

                        product_data.append({
                            'date': order_date,
                            'product_id': product_id,
                            'sku': item.get('sku', ''),  # Add SKU field
                            'name': item.get('name'),
                            'quantity': quantity,
                            'total': float(item.get('total', 0)) + float(item.get('total_tax', 0)),
                            'subtotal': float(item.get('subtotal', 0)),
                            'tax': float(item.get('total_tax', 0)),
                            'cost': cost * quantity,
                            'stock_quantity': stock_quantity
                        })

                except Exception as e:
                    logging.error(f"Error processing order {order.get('id')}: {str(e)}")
                    continue

            progress_bar.empty()

        # Log processing duration
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        logging.debug(f"Processed {len(orders)} orders in {duration:.2f} seconds")

        # Create DataFrames from collected data
        df_orders = pd.DataFrame(order_data)
        df_products = pd.DataFrame(product_data)

        return df_orders, df_products

    def get_order_status_display(self, status):
        """Convert order status to Norwegian display text"""
        status_mapping = {
            'completed': 'Fullført',
            'processing': 'Under behandling',
            'on-hold': 'På vent',
            'pending': 'Venter',
            'cancelled': 'Kansellert',
            'refunded': 'Refundert',
            'failed': 'Mislykket'
        }
        return status_mapping.get(status, status)  # Return original if no mapping found