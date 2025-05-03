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

    def get_stock_quantities_batch(self, product_ids, force_refresh=False):
        """
        Get stock quantities for multiple products in one API call
        
        Args:
            product_ids: List of product IDs to fetch stock quantities for
            force_refresh: If True, bypass cache and fetch fresh data
            
        Returns:
            Dictionary mapping product IDs to their stock quantities
        """
        try:
            # Check cache first if not forcing refresh
            now = datetime.now()
            
            # Clear cache if forcing refresh
            if force_refresh:
                logging.debug(f"Force refresh requested, clearing stock cache")
                self.stock_cache = {}
                self.cache_timestamp = None
            
            if not force_refresh and self.cache_timestamp and (now - self.cache_timestamp) < self.cache_duration:
                logging.debug(f"Using cached stock data, cache age: {(now - self.cache_timestamp).total_seconds()} seconds")
                # Return cached values if available
                return {pid: self.stock_cache.get(pid, 0) for pid in product_ids}
                
            logging.debug(f"Fetching fresh stock data for {len(product_ids)} products")

            # Fetch products in batches of 100 but use parallel processing for speed
            batch_size = 100
            all_stock = {}

            # Define helper functions for parallel processing
            def fetch_product_batch(batch_ids):
                batch_results = {}
                try:
                    products_query = ",".join(map(str, batch_ids))
                    response = self.wcapi.get("products", params={
                        "include": products_query,
                        "per_page": len(batch_ids),
                        "status": "any"  # Include all product statuses
                    })
                    products = response.json()
                    
                    if not isinstance(products, list):
                        logging.error(f"Invalid response format for products: {products}")
                        return batch_results
                        
                    # Collect variable products to fetch their variations in bulk
                    variable_products = []
                    variation_products = []
                    standard_products = []
                    
                    for product in products:
                        pid = product.get('id')
                        if pid is None:
                            continue
                            
                        stock = product.get('stock_quantity')
                        if stock is not None:
                            # If stock is directly available, store it immediately
                            batch_results[pid] = 0 if stock is None else stock
                            continue
                            
                        # Categorize products for optimized fetching
                        if product.get('type') == 'variable':
                            variable_products.append(product)
                        elif product.get('parent_id'):
                            variation_products.append(product)
                        else:
                            standard_products.append(product)
                    
                    # Process each category in parallel
                    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
                        # Process variable products
                        variable_futures = {
                            executor.submit(self._fetch_variable_product_stock, product): 
                            product.get('id') for product in variable_products
                        }
                        
                        # Process variation products
                        variation_futures = {
                            executor.submit(self._fetch_variation_product_stock, product):
                            product.get('id') for product in variation_products
                        }
                        
                        # Collect results from variable products
                        for future in concurrent.futures.as_completed(variable_futures):
                            pid = variable_futures[future]
                            try:
                                stock = future.result()
                                batch_results[pid] = stock
                            except Exception as e:
                                logging.error(f"Error processing variable product {pid}: {str(e)}")
                                batch_results[pid] = 0
                        
                        # Collect results from variation products
                        for future in concurrent.futures.as_completed(variation_futures):
                            pid = variation_futures[future]
                            try:
                                stock = future.result()
                                batch_results[pid] = stock
                            except Exception as e:
                                logging.error(f"Error processing variation {pid}: {str(e)}")
                                batch_results[pid] = 0
                    
                    # Process any remaining standard products
                    for product in standard_products:
                        pid = product.get('id')
                        stock = product.get('stock_quantity', 0) or 0
                        batch_results[pid] = stock
                        
                except Exception as e:
                    logging.error(f"Error fetching batch: {str(e)}")
                
                return batch_results
            
            # Create batches for parallel processing
            batches = []
            for i in range(0, len(product_ids), batch_size):
                batches.append(list(product_ids)[i:i + batch_size])
            
            # Process batches in parallel for maximum speed
            with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
                batch_futures = {executor.submit(fetch_product_batch, batch): i for i, batch in enumerate(batches)}
                
                for future in concurrent.futures.as_completed(batch_futures):
                    batch_results = future.result()
                    all_stock.update(batch_results)
                    # Update cache
                    for pid, stock in batch_results.items():
                        self.stock_cache[pid] = stock

            # Update cache timestamp
            self.cache_timestamp = now

            # Log the final stock quantities
            logging.debug(f"Final stock quantities: {all_stock}")
            return all_stock

        except Exception as e:
            logging.error(f"Error fetching stock quantities: {str(e)}")
            # Return 0 instead of None for missing stock quantities
            return {pid: 0 for pid in product_ids}

    def _fetch_variable_product_stock(self, product):
        """
        Helper method to fetch stock for variable products with variations
        
        Args:
            product: The variable product object
            
        Returns:
            Total stock quantity summed across all variations
        """
        pid = product.get('id')
        try:
            # For variable products, fetch variations
            variations_response = self.wcapi.get(f"products/{pid}/variations", params={"per_page": 100})
            variations = variations_response.json()
            
            if isinstance(variations, list) and variations:
                # Sum up stock quantities from all variations
                variation_stock = sum(v.get('stock_quantity', 0) or 0 for v in variations)
                logging.debug(f"Variable product {pid} has total stock: {variation_stock} from variations")
                return variation_stock
            return 0
        except Exception as e:
            logging.error(f"Error fetching variations for product {pid}: {str(e)}")
            return 0
            
    def _fetch_variation_product_stock(self, product):
        """
        Helper method to fetch stock for a variation of a variable product
        
        Args:
            product: The variation product object
            
        Returns:
            Stock quantity for the variation
        """
        pid = product.get('id')
        parent_id = product.get('parent_id')
        
        try:
            # Try to get stock from variation directly
            variation_response = self.wcapi.get(f"products/{parent_id}/variations/{pid}")
            variation = variation_response.json()
            
            if isinstance(variation, dict):
                variation_stock = variation.get('stock_quantity')
                if variation_stock is not None:
                    logging.debug(f"Variation {pid} has stock: {variation_stock}")
                    return variation_stock
                    
            # If variation doesn't have stock or request fails, try parent
            parent_response = self.wcapi.get(f"products/{parent_id}")
            parent_product = parent_response.json()
            parent_stock = parent_product.get('stock_quantity', 0) or 0
            logging.debug(f"Using parent stock for variation {pid}: {parent_stock}")
            return parent_stock
        except Exception as e:
            logging.error(f"Error fetching stock for variation {pid}: {str(e)}")
            return 0
    
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
        """Fetch orders from WooCommerce API within the specified date range using parallel requests"""
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

            with st.spinner('Henter ordrer...'):
                # First, determine the total number of pages
                params = {
                    "after": start_date_utc.isoformat(),
                    "before": end_date_utc.isoformat(),
                    "per_page": 100,  # Maximum allowed by WooCommerce API
                    "page": 1
                }
                
                response = self.wcapi.get("orders", params=params)
                data = response.json()
                
                if not isinstance(data, list):
                    logging.error(f"Invalid response format: {data}")
                    return []
                
                # Get total pages from WooCommerce headers
                total_orders = int(response.headers.get('X-WP-Total', '0'))
                total_pages = int(response.headers.get('X-WP-TotalPages', '1'))
                
                logging.debug(f"Total orders to fetch: {total_orders} across {total_pages} pages")
                
                # If we only have one page, return the data we already have
                if total_pages <= 1:
                    return data
                
                # Create a progress bar
                progress_bar = st.progress(0)
                
                # Function to fetch a single page
                def fetch_page(page_num):
                    try:
                        start_time = datetime.now()
                        page_params = {
                            "after": start_date_utc.isoformat(),
                            "before": end_date_utc.isoformat(),
                            "per_page": 100,
                            "page": page_num,
                            "status": "any"
                        }
                        page_response = self.wcapi.get("orders", params=page_params)
                        page_data = page_response.json()
                        
                        if not isinstance(page_data, list):
                            logging.error(f"Invalid response format for page {page_num}: {page_data}")
                            return []
                        
                        end_time = datetime.now()
                        duration = (end_time - start_time).total_seconds()
                        logging.debug(f"Page {page_num} fetched in {duration:.2f} seconds")
                        return page_data
                    except Exception as e:
                        logging.error(f"Error fetching page {page_num}: {str(e)}")
                        return []
                
                # Use the data from the first page that we already fetched
                all_orders = data
                
                # Fetch remaining pages in parallel
                remaining_pages = list(range(2, total_pages + 1))
                
                # Use ThreadPoolExecutor to fetch pages in parallel
                with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
                    future_to_page = {executor.submit(fetch_page, page_num): page_num for page_num in remaining_pages}
                    
                    # Process results as they complete
                    for i, future in enumerate(concurrent.futures.as_completed(future_to_page)):
                        page_num = future_to_page[future]
                        try:
                            page_data = future.result()
                            all_orders.extend(page_data)
                            
                            # Update progress bar
                            progress = (i + 1) / len(remaining_pages)
                            progress_bar.progress(progress)
                            
                        except Exception as e:
                            logging.error(f"Error processing page {page_num}: {str(e)}")
                
                progress_bar.empty()
                
                logging.debug(f"Total orders fetched: {len(all_orders)}")
                return all_orders

        except Exception as e:
            logging.error(f"Error fetching orders: {str(e)}")
            return []

    def process_orders_to_df(self, orders):
        """Convert orders to pandas DataFrame with daily metrics and product information using parallel processing"""
        if not orders:
            return pd.DataFrame(), pd.DataFrame()

        oslo_tz = pytz.timezone('Europe/Oslo')
        
        # Collect all product IDs first - This is much faster as a one-pass operation
        logging.debug("Extracting product IDs from orders")
        product_ids = set()
        for order in orders:
            for item in order.get('line_items', []):
                product_id = item.get('product_id')
                if product_id:
                    product_ids.add(product_id)

        # Batch fetch stock quantities in parallel
        with st.spinner('Henter lagerstatus...'):
            stock_quantities = self.get_stock_quantities_batch(product_ids)

        logging.debug(f"Processing {len(orders)} orders")
        start_time = datetime.now()
        
        # Define helper function to process one order
        def process_order(order):
            try:
                # Parse and convert date to Oslo timezone
                date_str = order.get('date_created')
                if not date_str:
                    return None, []  # Skip orders without dates
                
                utc_date = pd.to_datetime(date_str)
                order_date = utc_date.tz_localize('UTC').tz_convert(oslo_tz)
                
                # Initialize order info
                order_id = order.get('id')
                total = float(order.get('total', 0))
                status = order.get('status', '')
                
                # Process shipping lines
                shipping_lines = order.get('shipping_lines', [])
                shipping_base = sum(float(shipping.get('total', 0)) for shipping in shipping_lines)
                shipping_tax = sum(float(shipping.get('total_tax', 0)) for shipping in shipping_lines)
                
                # Calculate total shipping
                total_shipping = shipping_base + shipping_tax
                total_tax = float(order.get('total_tax', 0))
                subtotal = sum(float(item.get('subtotal', 0)) for item in order.get('line_items', []))
                
                # Get billing information
                billing = order.get('billing', {})
                
                # Get order number and payment method
                meta_data = order.get('meta_data', [])
                order_number = self.get_order_number(meta_data)
                dintero_method = self.get_dintero_payment_method(meta_data)
                shipping_method = self.get_shipping_method(shipping_lines)
                invoice_details = self.get_invoice_details(meta_data)
                
                # Create order record
                order_info = {
                    'date': order_date,
                    'order_id': order_id,
                    'order_number': order_number,
                    'status': self.get_order_status_display(status),
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
                }
                
                # Process line items
                products = []
                for item in order.get('line_items', []):
                    quantity = int(item.get('quantity', 0))
                    
                    # Extract cost from metadata
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
                    stock_quantity = stock_quantities.get(product_id, 0)
                    
                    products.append({
                        'date': order_date,
                        'product_id': product_id,
                        'sku': item.get('sku', ''),
                        'name': item.get('name'),
                        'quantity': quantity,
                        'total': float(item.get('total', 0)) + float(item.get('total_tax', 0)),
                        'subtotal': float(item.get('subtotal', 0)),
                        'tax': float(item.get('total_tax', 0)),
                        'cost': cost * quantity,
                        'stock_quantity': stock_quantity
                    })
                
                return order_info, products
                
            except Exception as e:
                logging.error(f"Error processing order {order.get('id')}: {str(e)}")
                return None, []
        
        # Process orders with progress bar
        with st.spinner('Behandler ordrer...'):
            progress_bar = st.progress(0)
            
            # Use ThreadPoolExecutor for parallel processing
            order_chunks = []
            product_chunks = []
            chunk_size = max(1, min(100, len(orders) // 10))  # Adaptive chunk size
            
            with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
                # Submit all orders for processing
                future_to_order = {executor.submit(process_order, order): i for i, order in enumerate(orders)}
                
                # Process results as they complete
                for i, future in enumerate(concurrent.futures.as_completed(future_to_order)):
                    order_info, products = future.result()
                    
                    # Only add valid results
                    if order_info:
                        order_chunks.append(order_info)
                    if products:
                        product_chunks.extend(products)
                    
                    # Update progress bar
                    progress = (i + 1) / len(orders)
                    progress_bar.progress(progress)
            
            progress_bar.empty()
        
        # Log processing duration
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        # Create DataFrames from collected data
        df_orders = pd.DataFrame(order_chunks)
        df_products = pd.DataFrame(product_chunks)
        
        logging.debug(f"Processed {len(orders)} orders in {duration:.2f} seconds")
        logging.debug(f"Created DataFrames with {len(df_orders)} orders and {len(df_products)} product records")
        
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