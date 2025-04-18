"""
Translations module for WooCommerce Dashboard
Contains translations for Norwegian and English
"""

class Translations:
    """
    Class to handle translations for the WooCommerce Dashboard
    """
    def __init__(self):
        self.translations = {
            'no': {
                # Page title and headers
                'page_title': 'WooCommerce Dashboard',
                'dashboard_title': '📊 Salgsstatistikk nettbutikk',
                
                # Welcome page
                'welcome_text': 'Gratulerer! Så mye penger har du tjent i dag:',
                'click_anywhere': '(Klikk hvor som helst for å se dashbordet)',
                
                # Main dashboard
                'connected_status': 'Koblet til WooCommerce API',
                
                # Sidebar elements
                'debug_mode': 'Debug Mode',
                'debug_info': 'Debug mode is enabled. API responses and error messages are being logged to woocommerce_api.log',
                'enable_notifications': 'Aktiver sanntidsvarsler',
                'enable_sound': '🔔 Aktiver lydvarsling',
                'sound_help': 'Spiller av Ca-Ching lyd når en ny ordre er mottatt.',
                'notification_success': '✨ Aktivert varsler - Du får beskjed når det kommer inn en ny bestilling!',
                'select_language': 'Velg språk',
                
                # View period selection
                'view_period': 'Velg visningsperiode',
                'view_period_help': 'Velg hvordan dataene skal aggregeres',
                'daily': 'Daglig',
                'weekly': 'Ukentlig',
                'monthly': 'Månedlig',
                
                # Date selection
                'date_range_header': 'Valg av ordreperiode',
                'start_date': 'Startdato',
                'end_date': 'Sluttdato',
                'date_help_start': 'Startdato (standard: {})',
                'date_help_end': 'Sluttdato (standard: {})',
                'date_error': 'Error: End date must be after start date',
                'date_info': 'Basert på ordre fra {} til {}',
                
                # Loading and errors
                'fetching_orders': 'Henter bestillinger fra nettbutikken...',
                'no_orders_found': 'Ingen ordre funnet fra perioden {} and {}',
                'error': 'Error: {}',
                'error_calculating': 'Error calculating metrics: {}',
                
                # Tabs
                'dashboard_tab': '📊 Dashboard',
                'invoices_tab': '🧾 Fakturaer',
                'results_tab': '📈 Resultat',
                'export_tab': '📤 Eksporter',
                
                # Metrics
                'total_revenue_incl_vat': 'Total omsetning (ink. MVA)',
                'total_revenue_incl_vat_help': 'Total revenue including VAT, excluding shipping costs',
                'total_revenue_excl_vat': 'Total omsetning (eks. MVA)',
                'total_revenue_excl_vat_help': 'Total revenue excluding VAT and shipping costs',
                'total_profit': 'Total fortjeneste',
                'total_profit_help': 'Profit calculated using revenue (excl. VAT) minus product costs',
                'total_shipping': 'Total frakt',
                'total_shipping_help': 'Total shipping costs including VAT',
                'total_tax': 'Total MVA',
                'total_tax_help': 'Total VAT collected (including shipping VAT)',
                'profit_margin': 'Fortjenestemargin',
                'profit_margin_help': 'Profit as percentage of revenue (excl. VAT)',
                'cogs': 'Kostnad for solgte varer',
                'cogs_help': 'Total cost of products sold (excl. VAT)',
                'order_count': 'Antall ordrer',
                'order_count_help': 'Total number of orders in selected period',
                
                # Explanations
                'calculation_info': """
                💡 Kalkulasjon av omsetning og profit:
                - Total omsetning (ink. MVA): Totalt produktsalg inkludert MVA, eks. frakt
                - Total omsetning (eks. MVA): Total omsetning eks. MVA og frakt.
                - Fraktkostnader vises ekskl. mva
                - Kostnad: Total varekostnad (eks. MVA)
                """,
                
                # Products section
                'top_products': '10 mest solgte produkter basert på antall',
                'period_caption': 'For perioden: {} til {}',
                'product_name_column': 'Produktnavn',
                'product_id_column': 'Produkt ID',
                'product_id_help': 'Unik identifikator for produktet',
                'quantity_sold_column': 'Antall solgt',
                'quantity_sold_help': 'Totalt antall solgt av dette produkter innenfor valg periode',
                'stock_column': 'På lager',
                'stock_help': 'Nåværende lagerbeholdning',
                'no_product_data': 'Ingen produktdata tilgjengelig for valgt periode',
                
                # Revenue and Customers section
                'revenue_trends': 'Omsetning',
                'customer_list': 'Oversikt over kunder',
                'customer_name': 'Navn på kunde',
                'customer_email': 'E-postadresse',
                'order_date': 'Ordre utført',
                'payment_method': 'Betalingsmetode',
                'shipping_method': 'Fraktmetode',
                'order_total': 'Ordretotal',
                'order_total_help': 'Totalsum for ordren',
                'no_customer_data': 'Ingen kundedata tilgjengelig for valgt periode',
            },
            'en': {
                # Page title and headers
                'page_title': 'WooCommerce Dashboard',
                'dashboard_title': '📊 Sales Statistics Online Store',
                
                # Welcome page
                'welcome_text': 'Congratulations! You have earned this much money today:',
                'click_anywhere': '(Click anywhere to see the dashboard)',
                
                # Main dashboard
                'connected_status': 'Connected to WooCommerce API',
                
                # Sidebar elements
                'debug_mode': 'Debug Mode',
                'debug_info': 'Debug mode is enabled. API responses and error messages are being logged to woocommerce_api.log',
                'enable_notifications': 'Enable real-time notifications',
                'enable_sound': '🔔 Enable sound notifications',
                'sound_help': 'Plays a Ca-Ching sound when a new order is received.',
                'notification_success': '✨ Notifications activated - You will be notified when a new order comes in!',
                'select_language': 'Select language',
                
                # View period selection
                'view_period': 'Select view period',
                'view_period_help': 'Select how the data should be aggregated',
                'daily': 'Daily',
                'weekly': 'Weekly',
                'monthly': 'Monthly',
                
                # Date selection
                'date_range_header': 'Order period selection',
                'start_date': 'Start date',
                'end_date': 'End date',
                'date_help_start': 'Start date (default: {})',
                'date_help_end': 'End date (default: {})',
                'date_error': 'Error: End date must be after start date',
                'date_info': 'Based on orders from {} to {}',
                
                # Loading and errors
                'fetching_orders': 'Fetching orders from the online store...',
                'no_orders_found': 'No orders found for the period {} to {}',
                'error': 'Error: {}',
                'error_calculating': 'Error calculating metrics: {}',
                
                # Tabs
                'dashboard_tab': '📊 Dashboard',
                'invoices_tab': '🧾 Invoices',
                'results_tab': '📈 Results',
                'export_tab': '📤 Export',
                
                # Metrics
                'total_revenue_incl_vat': 'Total revenue (incl. VAT)',
                'total_revenue_incl_vat_help': 'Total revenue including VAT, excluding shipping costs',
                'total_revenue_excl_vat': 'Total revenue (excl. VAT)',
                'total_revenue_excl_vat_help': 'Total revenue excluding VAT and shipping costs',
                'total_profit': 'Total profit',
                'total_profit_help': 'Profit calculated using revenue (excl. VAT) minus product costs',
                'total_shipping': 'Total shipping',
                'total_shipping_help': 'Total shipping costs including VAT',
                'total_tax': 'Total VAT',
                'total_tax_help': 'Total VAT collected (including shipping VAT)',
                'profit_margin': 'Profit margin',
                'profit_margin_help': 'Profit as percentage of revenue (excl. VAT)',
                'cogs': 'Cost of goods sold',
                'cogs_help': 'Total cost of products sold (excl. VAT)',
                'order_count': 'Order count',
                'order_count_help': 'Total number of orders in selected period',
                
                # Explanations
                'calculation_info': """
                💡 Calculation of revenue and profit:
                - Total revenue (incl. VAT): Total product sales including VAT, excl. shipping
                - Total revenue (excl. VAT): Total revenue excl. VAT and shipping.
                - Shipping costs are shown excl. VAT
                - Cost: Total product cost (excl. VAT)
                """,
                
                # Products section
                'top_products_header': '10 best-selling products based on quantity',
                'period_caption': 'For the period: {} to {}',
                'product_name': 'Product name',
                'product_id': 'Product ID',
                'product_id_help': 'Unique identifier for the product',
                'quantity_sold': 'Quantity sold',
                'quantity_sold_help': 'Total quantity sold of this product within the selected period',
                'stock_quantity': 'In stock',
                'stock_quantity_help': 'Current stock quantity',
                'no_product_data': 'No product data available',
            }
        }
    
    def get_text(self, key, lang='no', *args):
        """
        Get translated text for a given key
        
        Args:
            key (str): Translation key
            lang (str): Language code ('no' or 'en')
            *args: Format arguments if needed
            
        Returns:
            str: Translated text
        """
        # Default to Norwegian if language not supported
        if lang not in self.translations:
            lang = 'no'
        
        # Get translation text or key if not found
        text = self.translations[lang].get(key, key)
        
        # Format if args provided
        if args:
            try:
                return text.format(*args)
            except:
                return text
        
        return text