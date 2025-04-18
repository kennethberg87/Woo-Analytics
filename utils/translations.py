"""Translations for the WooCommerce Dashboard"""

class Translations:
    """Translations for the WooCommerce Dashboard"""
    
    # Available languages
    LANGUAGES = {
        'no': 'Norsk',
        'en': 'English'
    }
    
    # Translations dictionary
    TRANSLATIONS = {
        # Dashboard titles
        'dashboard_title': {
            'no': '📊 Salgsstatistikk nettbutikk',
            'en': '📊 Online Store Sales Statistics'
        },
        
        # Metrics
        'total_revenue_incl_vat': {
            'no': 'Total omsetning (ink. MVA)',
            'en': 'Total Revenue (incl. VAT)'
        },
        'total_revenue_excl_vat': {
            'no': 'Total omsetning (eks. MVA)',
            'en': 'Total Revenue (excl. VAT)'
        },
        'total_profit': {
            'no': 'Total fortjeneste',
            'en': 'Total Profit'
        },
        'total_shipping': {
            'no': 'Total frakt',
            'en': 'Total Shipping'
        },
        'total_shipping_costs': {
            'no': 'Totale fraktkostnader',
            'en': 'Total Shipping Costs'
        },
        'total_vat': {
            'no': 'Total MVA',
            'en': 'Total VAT'
        },
        'profit_margin': {
            'no': 'Fortjenestemargin',
            'en': 'Profit Margin'
        },
        'cost_of_goods_sold': {
            'no': 'Kostnad for solgte varer',
            'en': 'Cost of Goods Sold'
        },
        'order_count': {
            'no': 'Antall ordrer',
            'en': 'Order Count'
        },
        
        # Date range
        'view_period': {
            'no': 'Velg visningsperiode',
            'en': 'Select View Period'
        },
        'daily': {
            'no': 'Daglig',
            'en': 'Daily'
        },
        'weekly': {
            'no': 'Ukentlig',
            'en': 'Weekly'
        },
        'monthly': {
            'no': 'Månedlig',
            'en': 'Monthly'
        },
        'start_date': {
            'no': 'Startdato',
            'en': 'Start Date'
        },
        'end_date': {
            'no': 'Sluttdato',
            'en': 'End Date'
        },
        
        # Tabs
        'dashboard_tab': {
            'no': '📊 Dashboard',
            'en': '📊 Dashboard'
        },
        'invoices_tab': {
            'no': '🧾 Fakturaer',
            'en': '🧾 Invoices'
        },
        'results_tab': {
            'no': '📈 Resultat',
            'en': '📈 Results'
        },
        'export_tab': {
            'no': '📤 Eksporter',
            'en': '📤 Export'
        },
        
        # Settings
        'enable_notifications': {
            'no': 'Aktiver sanntidsvarsler',
            'en': 'Enable Real-time Notifications'
        },
        'enable_sound': {
            'no': '🔔 Aktiver lydvarsling',
            'en': '🔔 Enable Sound Notifications'
        },
        'debug_mode': {
            'no': 'Debug Modus',
            'en': 'Debug Mode'
        },
        'language': {
            'no': 'Språk',
            'en': 'Language'
        },
        
        # Products
        'top_products_title': {
            'no': '10 mest solgte produkter basert på antall',
            'en': '10 Best-selling Products by Quantity'
        },
        'product_name': {
            'no': 'Produktnavn',
            'en': 'Product Name'
        },
        'product_id': {
            'no': 'Produkt ID',
            'en': 'Product ID'
        },
        'quantity_sold': {
            'no': 'Antall solgt',
            'en': 'Quantity Sold'
        },
        'stock_quantity': {
            'no': 'På lager',
            'en': 'In Stock'
        },
        
        # Order statuses
        'processing': {
            'no': 'Under behandling',
            'en': 'Processing'
        },
        'completed': {
            'no': 'Fullført',
            'en': 'Completed'
        },
        'pending': {
            'no': 'Venter',
            'en': 'Pending'
        },
        'cancelled': {
            'no': 'Kansellert',
            'en': 'Cancelled'
        },
        'refunded': {
            'no': 'Refundert',
            'en': 'Refunded'
        },
        'failed': {
            'no': 'Mislyktes',
            'en': 'Failed'
        },
        'on-hold': {
            'no': 'På vent',
            'en': 'On Hold'
        },
        
        # Payment methods
        'payment_methods': {
            'no': 'Betalingsmetode',
            'en': 'Payment Method'
        },
        'unknown': {
            'no': 'Ukjent',
            'en': 'Unknown'
        },
        
        # Messages
        'connected_to_api': {
            'no': 'Koblet til WooCommerce API',
            'en': 'Connected to WooCommerce API'
        },
        'no_orders_found': {
            'no': 'Ingen ordre funnet fra perioden',
            'en': 'No orders found for the period'
        },
        'loading_orders': {
            'no': 'Henter bestillinger fra nettbutikken...',
            'en': 'Fetching orders from store...'
        },
        'date_range_info': {
            'no': 'Basert på ordre fra {} til {}',
            'en': 'Based on orders from {} to {}'
        },
        'calculation_info': {
            'no': '💡 Kalkulasjon av omsetning og profit:\n- Total omsetning (ink. MVA): Totalt produktsalg inkludert MVA, eks. frakt\n- Total omsetning (eks. MVA): Total omsetning eks. MVA og frakt.\n- Fraktkostnader vises ekskl. mva\n- Kostnad: Total varekostnad (eks. MVA)',
            'en': '💡 Revenue and profit calculation:\n- Total Revenue (incl. VAT): Total product sales including VAT, excl. shipping\n- Total Revenue (excl. VAT): Total revenue excl. VAT and shipping.\n- Shipping costs are shown excl. VAT\n- Cost: Total cost of goods (excl. VAT)'
        }
    }
    
    @staticmethod
    def get_text(key, language='no'):
        """Get translation for a key in the specified language"""
        if key not in Translations.TRANSLATIONS:
            return key
        
        if language not in Translations.TRANSLATIONS[key]:
            # Fall back to Norwegian if language not available
            return Translations.TRANSLATIONS[key]['no']
        
        return Translations.TRANSLATIONS[key][language]