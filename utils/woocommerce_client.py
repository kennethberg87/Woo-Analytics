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
from threading import Lock
from functools import lru_cache
import json
import time

logging.basicConfig(level=logging.DEBUG)

class WooCommerceClient:
    def __init__(self):
        try:
            store_url = os.getenv('WOOCOMMERCE_URL')
            if not store_url:
                raise ValueError("WooCommerce store URL is not configured")

            parsed_url = urlparse(store_url)
            if not parsed_url.scheme or not parsed_url.netloc:
                raise ValueError("Invalid WooCommerce store URL format")

            self.wcapi = API(
                url=store_url,
                consumer_key=os.getenv('WOOCOMMERCE_KEY'),
                consumer_secret=os.getenv('WOOCOMMERCE_SECRET'),
                version="wc/v3",
                verify_ssl=False,
                timeout=30
            )

            # Initialize caches with locks for thread safety
            self.cache_lock = Lock()
            self.cache_timeout = 3600  # 1 hour cache
            self.max_workers = 20  # Increased parallel workers

            # Initialize caches
            if 'order_cache' not in st.session_state:
                st.session_state.order_cache = {}
            if 'stock_cache' not in st.session_state:
                st.session_state.stock_cache = {}
            if 'product_cache' not in st.session_state:
                st.session_state.product_cache = {}

        except Exception as e:
            st.sidebar.error(f"Failed to initialize WooCommerce client: {str(e)}")
            raise

    def _get_cached_data(self, cache_type, key, timeout=None):
        """Get data from cache with timeout validation"""
        if timeout is None:
            timeout = self.cache_timeout

        cache = getattr(st.session_state, f"{cache_type}_cache")
        with self.cache_lock:
            if key in cache:
                timestamp, data = cache[key]
                if (datetime.now() - timestamp).total_seconds() < timeout:
                    return data
        return None

    def _set_cached_data(self, cache_type, key, data):
        """Set data in cache with current timestamp"""
        cache = getattr(st.session_state, f"{cache_type}_cache")
        with self.cache_lock:
            cache[key] = (datetime.now(), data)

    def _fetch_orders_batch(self, params):
        """Fetch a batch of orders with error handling and retry"""
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = self.wcapi.get("orders", params=params)
                return response.json() if isinstance(response.json(), list) else []
            except Exception as e:
                if attempt == max_retries - 1:
                    logging.error(f"Failed to fetch orders after {max_retries} attempts: {str(e)}")
                    return []
                time.sleep(1)  # Wait before retry

    def get_orders(self, start_date, end_date):
        """Fetch orders with improved caching and parallel processing"""
        try:
            # Convert dates to UTC
            oslo_tz = pytz.timezone('Europe/Oslo')
            utc_tz = pytz.UTC

            start_date_oslo = oslo_tz.localize(datetime.combine(start_date, datetime.min.time()))
            end_date_oslo = oslo_tz.localize(datetime.combine(end_date, datetime.max.time()))

            start_date_utc = start_date_oslo.astimezone(utc_tz)
            end_date_utc = end_date_oslo.astimezone(utc_tz)

            # Check cache
            cache_key = f"{start_date}_{end_date}"
            cached_orders = self._get_cached_data('order', cache_key)
            if cached_orders:
                return cached_orders

            # Show progress
            progress_bar = st.progress(0)
            st.write("Henter ordrer...")

            # First batch to determine total orders
            initial_params = {
                "after": start_date_utc.isoformat(),
                "before": end_date_utc.isoformat(),
                "per_page": 100,
                "page": 1
            }

            first_batch = self._fetch_orders_batch(initial_params)
            if not first_batch:
                progress_bar.empty()
                return []

            # Prepare batches for parallel processing
            total_pages = (len(first_batch) // 100) + 1
            batches = [
                {
                    "after": start_date_utc.isoformat(),
                    "before": end_date_utc.isoformat(),
                    "per_page": 100,
                    "page": page,
                }
                for page in range(1, total_pages + 1)
            ]

            # Fetch orders in parallel
            all_orders = []
            with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                future_to_batch = {executor.submit(self._fetch_orders_batch, batch): batch for batch in batches}
                completed = 0

                for future in concurrent.futures.as_completed(future_to_batch):
                    orders_batch = future.result()
                    all_orders.extend(orders_batch)
                    completed += 1
                    progress_bar.progress(min(1.0, completed / len(batches)))

            # Cache results
            self._set_cached_data('order', cache_key, all_orders)
            progress_bar.empty()

            return all_orders

        except Exception as e:
            logging.error(f"Error fetching orders: {str(e)}")
            if 'progress_bar' in locals():
                progress_bar.empty()
            return []

    def _process_single_order(self, order, oslo_tz, stock_quantities):
        """Process a single order with optimized data handling"""
        try:
            # Extract date
            date_str = order.get('date_created')
            if not date_str:
                return None, []

            order_date = pd.to_datetime(date_str).tz_localize('UTC').tz_convert(oslo_tz)

            # Process order details
            order_info = {
                'date': order_date,
                'order_id': order.get('id'),
                'order_number': self._get_order_number(order),
                'status': order.get('status', ''),
                'total': float(order.get('total', 0)),
                'subtotal': sum(float(item.get('subtotal', 0)) for item in order.get('line_items', [])),
                'shipping_total': sum(float(s.get('total', 0)) for s in order.get('shipping_lines', [])),
                'tax_total': float(order.get('total_tax', 0)),
                'billing': order.get('billing', {}),
                'meta_data': order.get('meta_data', [])
            }

            # Process line items
            product_info = []
            for item in order.get('line_items', []):
                product_id = item.get('product_id')
                quantity = int(item.get('quantity', 0))

                product_info.append({
                    'date': order_date,
                    'product_id': product_id,
                    'name': item.get('name'),
                    'quantity': quantity,
                    'total': float(item.get('total', 0)) + float(item.get('total_tax', 0)),
                    'stock_quantity': stock_quantities.get(product_id)
                })

            return order_info, product_info

        except Exception as e:
            logging.error(f"Error processing order {order.get('id')}: {str(e)}")
            return None, []

    def process_orders_to_df(self, orders):
        """Convert orders to DataFrame with optimized processing"""
        if not orders:
            return pd.DataFrame(), pd.DataFrame()

        oslo_tz = pytz.timezone('Europe/Oslo')
        progress_bar = st.progress(0)
        st.write("Behandler ordrer...")

        try:
            # Get unique product IDs
            product_ids = {
                item['product_id']
                for order in orders
                for item in order.get('line_items', [])
            }

            # Batch fetch stock quantities
            stock_quantities = self._get_cached_data('stock', 'all_stocks') or {}
            missing_products = product_ids - set(stock_quantities.keys())

            if missing_products:
                new_quantities = self._batch_get_stock_quantities(missing_products)
                stock_quantities.update(new_quantities)
                self._set_cached_data('stock', 'all_stocks', stock_quantities)

            # Process orders in parallel
            order_data = []
            product_data = []
            total_orders = len(orders)

            with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                future_to_order = {
                    executor.submit(self._process_single_order, order, oslo_tz, stock_quantities): order
                    for order in orders
                }

                completed = 0
                for future in concurrent.futures.as_completed(future_to_order):
                    try:
                        order_info, products_info = future.result()
                        if order_info:
                            order_data.append(order_info)
                        product_data.extend(products_info)

                        completed += 1
                        progress_bar.progress(min(1.0, completed / total_orders))
                    except Exception as e:
                        logging.error(f"Error processing order batch: {str(e)}")

            # Create DataFrames
            df_orders = pd.DataFrame(order_data)
            df_products = pd.DataFrame(product_data)

            progress_bar.empty()
            return df_orders, df_products

        except Exception as e:
            logging.error(f"Error in process_orders_to_df: {str(e)}")
            if 'progress_bar' in locals():
                progress_bar.empty()
            return pd.DataFrame(), pd.DataFrame()

    def _batch_get_stock_quantities(self, product_ids):
        """Fetch stock quantities in parallel batches"""
        stock_quantities = {}
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {
                executor.submit(self._get_product_stock, product_id): product_id
                for product_id in product_ids
            }

            for future in concurrent.futures.as_completed(futures):
                product_id = futures[future]
                try:
                    stock_quantities[product_id] = future.result()
                except Exception as e:
                    logging.error(f"Error fetching stock for product {product_id}: {str(e)}")
                    stock_quantities[product_id] = None

        return stock_quantities

    def _get_product_stock(self, product_id):
        """Get stock quantity for a single product"""
        try:
            cached_stock = self._get_cached_data('stock', product_id)
            if cached_stock is not None:
                return cached_stock

            response = self.wcapi.get(f"products/{product_id}")
            product_data = response.json()
            stock_quantity = product_data.get('stock_quantity')
            self._set_cached_data('stock', product_id, stock_quantity)
            return stock_quantity
        except Exception as e:
            logging.error(f"Error fetching product {product_id}: {str(e)}")
            return None

    def _get_order_number(self, order):
        """Extract order number from meta data"""
        meta_data = order.get('meta_data', [])
        for meta in meta_data:
            if meta.get('key') == '_order_number_formatted':
                return meta.get('value', '')
        return str(order.get('id', ''))

    def batch_get_stock_quantities(self, product_ids):
        """Get stock quantities for multiple products in parallel"""
        stock_quantities = {}
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_id = {
                executor.submit(self.get_stock_quantity, product_id): product_id
                for product_id in product_ids
            }
            for future in concurrent.futures.as_completed(future_to_id):
                product_id = future_to_id[future]
                try:
                    stock_quantities[product_id] = future.result()
                except Exception as e:
                    logging.error(f"Error fetching stock for product {product_id}: {str(e)}")
                    stock_quantities[product_id] = None
        return stock_quantities

    @lru_cache(maxsize=1000)
    def get_stock_quantity(self, product_id):
        """Get current stock quantity for a product with caching"""
        try:
            # Check cache first
            cache_key = f"stock_{product_id}"
            with self.cache_lock:
                cached_data = st.session_state.stock_cache.get(cache_key)
                if cached_data:
                    timestamp, value = cached_data
                    if (datetime.now() - timestamp).total_seconds() < self.cache_timeout:
                        return value

            response = self.wcapi.get(f"products/{product_id}")
            product_data = response.json()

            if 'stock_quantity' in product_data:
                # Update cache
                with self.cache_lock:
                    st.session_state.stock_cache[cache_key] = (datetime.now(), product_data['stock_quantity'])
                return product_data['stock_quantity']
            return None

        except Exception as e:
            logging.error(f"Error fetching stock for product {product_id}: {str(e)}")
            return None
    
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
            store_url = os.getenv('WOOCOMMERCE_URL')
            if not store_url:
                logging.error("WooCommerce store URL not configured")
                return None

            store_url = store_url.rstrip('/')

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

    def _process_order_details(self, order, order_date):
        """Helper method to process individual order details"""
        try:
            order_id = order.get('id')
            total = float(order.get('total', 0))
            status = order.get('status', '')

            # Process shipping
            shipping_lines = order.get('shipping_lines', [])
            shipping_base = sum(float(shipping.get('total', 0)) for shipping in shipping_lines)
            shipping_tax = sum(float(shipping.get('total_tax', 0)) for shipping in shipping_lines)
            total_shipping = shipping_base + shipping_tax

            # Calculate totals
            total_tax = float(order.get('total_tax', 0))
            subtotal = sum(float(item.get('subtotal', 0)) for item in order.get('line_items', []))

            return {
                'date': order_date,
                'order_id': order_id,
                'order_number': self.get_order_number(order.get('meta_data', [])),
                'status': status,
                'total': total,
                'subtotal': subtotal,
                'shipping_base': shipping_base,
                'shipping_total': total_shipping,
                'shipping_tax': shipping_tax,
                'tax_total': total_tax,
                'billing': order.get('billing', {}),
                'dintero_payment_method': self.get_dintero_payment_method(order.get('meta_data', [])),
                'shipping_method': self.get_shipping_method(shipping_lines),
                'meta_data': order.get('meta_data', [])
            }
        except Exception as e:
            logging.error(f"Error processing order details for {order.get('id')}: {str(e)}")
            return None

    def _process_line_items(self, order, order_date, stock_quantities):
        """Helper method to process line items from an order"""
        product_info = []
        try:
            for item in order.get('line_items', []):
                quantity = int(item.get('quantity', 0))
                cost = 0

                # Get cost from meta data
                for meta in item.get('meta_data', []):
                    if meta.get('key') == '_yith_cog_item_cost':
                        try:
                            cost = float(meta.get('value', 0))
                        except (ValueError, TypeError):
                            cost = 0
                        break

                product_id = item.get('product_id')
                stock_quantity = stock_quantities.get(product_id)

                product_info.append({
                    'date': order_date,
                    'product_id': product_id,
                    'name': item.get('name'),
                    'quantity': quantity,
                    'total': float(item.get('total', 0)) + float(item.get('total_tax', 0)),
                    'subtotal': float(item.get('subtotal', 0)),
                    'tax': float(item.get('total_tax', 0)),
                    'cost': cost * quantity,
                    'stock_quantity': stock_quantity
                })
        except Exception as e:
            logging.error(f"Error processing line items: {str(e)}")

        return product_info