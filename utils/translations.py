from typing import Dict, Any

TRANSLATIONS: Dict[str, Dict[str, str]] = {
    'no': {
        # Welcome page
        'welcome_greeting': 'Gratulerer! Så mye penger har du tjent i dag:',
        'click_anywhere': 'Klikk hvor som helst for å se dashbordet',
        
        # Dashboard
        'dashboard_title': '📊 Salgsstatistikk nettbutikk',
        'api_connected': 'Koblet til WooCommerce API',
        'debug_mode': 'Debug Mode',
        'debug_info': 'Debug mode is enabled. API responses and error messages are being logged to woocommerce_api.log',
        
        # Notifications
        'enable_notifications': 'Aktiver sanntidsvarsler',
        'enable_sound': '🔔 Aktiver lydvarsling',
        'sound_help': 'Spiller av Ca-Ching lyd når en ny ordre er mottatt.',
        'notifications_active': '✨ Aktivert varsler - Du får beskjed når det kommer inn en ny bestilling!',
        
        # View period
        'select_period': 'Velg visningsperiode',
        'period_help': 'Velg hvordan dataene skal aggregeres',
        'daily': 'Daglig',
        'weekly': 'Ukentlig',
        'monthly': 'Månedlig',
        
        # Date selection
        'order_period': 'Valg av ordreperiode',
        'start_date': 'Startdato',
        'end_date': 'Sluttdato',
        'date_range_error': 'Error: End date must be after start date',
        'based_on_orders': 'Basert på ordre fra {start_date} til {end_date}',
        'loading_orders': 'Henter bestillinger fra nettbutikken...',
        'no_orders': 'Ingen ordre funnet fra perioden {start_date} and {end_date}',
        
        # Metrics
        'total_revenue_vat': 'Total omsetning (ink. MVA)',
        'total_revenue_ex_vat': 'Total omsetning (eks. MVA)',
        'total_profit': 'Total fortjeneste',
        'total_shipping': 'Total frakt',
        'total_vat': 'Total MVA',
        'profit_margin': 'Fortjenestemargin',
        'cogs': 'Kostnad for solgte varer',
        'order_count': 'Antall ordrer',
        
        # Calculations info
        'calculations_info': '''💡 Kalkulasjon av omsetning og profit:
- Total omsetning (ink. MVA): Totalt produktsalg inkludert MVA, eks. frakt
- Total omsetning (eks. MVA): Total omsetning eks. MVA og frakt.
- Fraktkostnader vises ekskl. mva
- Kostnad: Total varekostnad (eks. MVA)''',
        
        # Products
        'top_products_title': '10 mest solgte produkter basert på antall',
        'product_name': 'Produktnavn',
        'product_id': 'Produkt ID',
        'quantity_sold': 'Antall solgt',
        'stock': 'På lager',
        'no_product_data': 'No product data available for the selected date range',
        
        # Revenue
        'revenue_title': 'Omsetning',
        
        # Customers
        'customers_title': 'Ovesikt over kunder',
        'customer_name': 'Navn på kunde',
        'email': 'E-postadresse',
        'order_date': 'Ordre utført',
        'payment_method': 'Betalingsmetode',
        'shipping_method': 'Fraktmetode',
        'order_total': 'Ordretotal',
    },
    'en': {
        # Welcome page
        'welcome_greeting': 'Congratulations! This is how much money you earned today:',
        'click_anywhere': 'Click anywhere to see the dashboard',
        
        # Dashboard
        'dashboard_title': '📊 Sales Statistics Dashboard',
        'api_connected': 'Connected to WooCommerce API',
        'debug_mode': 'Debug Mode',
        'debug_info': 'Debug mode is enabled. API responses and error messages are being logged to woocommerce_api.log',
        
        # Notifications
        'enable_notifications': 'Enable real-time notifications',
        'enable_sound': '🔔 Enable sound notifications',
        'sound_help': 'Plays a Ca-Ching sound when a new order is received.',
        'notifications_active': '✨ Notifications activated - You will be notified when a new order arrives!',
        
        # View period
        'select_period': 'Select view period',
        'period_help': 'Choose how to aggregate the data',
        'daily': 'Daily',
        'weekly': 'Weekly',
        'monthly': 'Monthly',
        
        # Date selection
        'order_period': 'Select order period',
        'start_date': 'Start date',
        'end_date': 'End date',
        'date_range_error': 'Error: End date must be after start date',
        'based_on_orders': 'Based on orders from {start_date} to {end_date}',
        'loading_orders': 'Loading orders from the store...',
        'no_orders': 'No orders found between {start_date} and {end_date}',
        
        # Metrics
        'total_revenue_vat': 'Total Revenue (incl. VAT)',
        'total_revenue_ex_vat': 'Total Revenue (excl. VAT)',
        'total_profit': 'Total Profit',
        'total_shipping': 'Total Shipping',
        'total_vat': 'Total VAT',
        'profit_margin': 'Profit Margin',
        'cogs': 'Cost of Goods Sold',
        'order_count': 'Order Count',
        
        # Calculations info
        'calculations_info': '''💡 Revenue and profit calculations:
- Total Revenue (incl. VAT): Total product sales including VAT, excl. shipping
- Total Revenue (excl. VAT): Total revenue excluding VAT and shipping
- Shipping costs are shown excl. VAT
- Cost: Total cost of goods (excl. VAT)''',
        
        # Products
        'top_products_title': 'Top 10 Products by Quantity Sold',
        'product_name': 'Product Name',
        'product_id': 'Product ID',
        'quantity_sold': 'Quantity Sold',
        'stock': 'In Stock',
        'no_product_data': 'No product data available for the selected date range',
        
        # Revenue
        'revenue_title': 'Revenue',
        
        # Customers
        'customers_title': 'Customer Overview',
        'customer_name': 'Customer Name',
        'email': 'Email',
        'order_date': 'Order Date',
        'payment_method': 'Payment Method',
        'shipping_method': 'Shipping Method',
        'order_total': 'Order Total',
    }
}

def get_text(key: str, lang: str = 'no', **kwargs: Any) -> str:
    """Get translated text for the given key and language"""
    translations = TRANSLATIONS.get(lang, TRANSLATIONS['no'])
    text = translations.get(key, TRANSLATIONS['no'][key])
    return text.format(**kwargs) if kwargs else text
