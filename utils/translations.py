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
        # Add these missing help texts
        # Help texts
        'start_date_help': 'Velg startdato for perioden',
        'end_date_help': 'Velg sluttdato for perioden',
        'total_revenue_vat_help': 'Total omsetning inkludert MVA, ekskludert fraktkostnader',
        'total_revenue_ex_vat_help': 'Total omsetning ekskludert MVA og fraktkostnader',
        'total_profit_help': 'Fortjeneste beregnet fra omsetning (eks. MVA) minus produktkostnader',
        'total_shipping_help': 'Totale fraktkostnader inkludert MVA',
        'total_vat_help': 'Total MVA innkrevd (inkludert frakt-MVA)',
        'profit_margin_help': 'Fortjeneste som prosent av omsetning (eks. MVA)',
        'cogs_help': 'Total kostnad for solgte varer (eks. MVA)',
        'order_count_help': 'Totalt antall ordrer i valgt periode',
        'product_id_help': 'Unik identifikator for produktet',
        'total_quantity_help': 'Totalt antall solgt av dette produktet innenfor valgt periode',
        'stock_quantity_help': 'Nåværende lagerbeholdning',
        'order_total_help': 'Totalsum for ordren',
        'total_profit_before_costs': 'Total fortjeneste før annonsekostnader',
        'net_result_help': 'Total fortjeneste minus annonsekostnader',

        # Tab names
        'tab_dashboard': '📊 Dashboard',
        'tab_invoices': '🧾 Fakturaer',
        'tab_result': '📈 Resultat',
        'tab_export': '📤 Eksporter',

        # Headers
        'top_products_header': '10 mest solgte produkter basert på antall',
        'revenue_trends': 'Omsetning ({period})',
        'customer_overview': 'Oversikt over kunder',
        'invoices_header': 'Fakturaer',
        'result_header': '📈 Resultatberegning',
        'export_data': 'Eksporter data',
        'export_order_data': 'Eksporter ordredata',
        'export_product_data': 'Eksporter produktdata',

        # Captions and info texts
        'period_caption': 'For perioden: {start_date} til {end_date}',
        'download_invoices': 'Last ned fakturaer',
        'download_info': '💡 Klikk på lenkene under for å laste ned PDF-fakturaer direkte. Fakturaene vil lastes ned automatisk når du klikker på linken.',
        'no_invoices': 'Ingen fakturaer funnet for valgt periode',
        'no_order_data': 'Ingen ordredata tilgjengelig for valgt periode',
        'calculation_method': '''💡 Beregningsmetode:
- Total fortjeneste er brutto fortjeneste før annonsekostnader
- Annonsekostnad er beregnet som kr 30 per ordre
- Netto resultat er total fortjeneste minus annonsekostnader''',
        'select_export_format': 'Velg filformat for eksport av {data_type}',
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

        'start_date_help': 'Select start date for the period',
        'end_date_help': 'Select end date for the period',
        'total_revenue_vat_help': 'Total revenue including VAT, excluding shipping costs',
        'total_revenue_ex_vat_help': 'Total revenue excluding VAT and shipping costs',
        'total_profit_help': 'Profit calculated from revenue (excl. VAT) minus product costs',
        'total_shipping_help': 'Total shipping costs including VAT',
        'total_vat_help': 'Total VAT collected (including shipping VAT)',
        'profit_margin_help': 'Profit as a percentage of revenue (excl. VAT)',
        'cogs_help': 'Total cost of goods sold (excl. VAT)',
        'order_count_help': 'Total number of orders in the selected period',
        'product_id_help': 'Unique identifier for the product',
        'total_quantity_help': 'Total quantity sold of this product within the selected period',
        'stock_quantity_help': 'Current stock quantity',
        'order_total_help': 'Total amount for the order',
        'total_profit_before_costs': 'Total profit before advertising costs',
        'net_result_help': 'Total profit minus advertising costs',

        'tab_dashboard': '📊 Dashboard',
        'tab_invoices': '🧾 Invoices',
        'tab_result': '📈 Result',
        'tab_export': '📤 Export',

        'top_products_header': 'Top 10 Products by Quantity Sold',
        'revenue_trends': 'Revenue ({period})',
        'customer_overview': 'Customer Overview',
        'invoices_header': 'Invoices',
        'result_header': '📈 Result Calculation',
        'export_data': 'Export data',
        'export_order_data': 'Export order data',
        'export_product_data': 'Export product data',

        'period_caption': 'For the period: {start_date} to {end_date}',
        'download_invoices': 'Download invoices',
        'download_info': '💡 Click on the links below to download PDF invoices directly. The invoices will be downloaded automatically when you click on the link.',
        'no_invoices': 'No invoices found for the selected period',
        'no_order_data': 'No order data available for the selected period',
        'calculation_method': '''💡 Calculation method:
- Total profit is gross profit before advertising costs
- Advertising cost is calculated as kr 30 per order
- Net result is total profit minus advertising costs''',
        'select_export_format': 'Select file format for export of {data_type}',
    }
}

def get_text(key: str, lang: str = 'no', **kwargs: Any) -> str:
    """Get translated text for the given key and language"""
    translations = TRANSLATIONS.get(lang, TRANSLATIONS['no'])
    text = translations.get(key, TRANSLATIONS['no'][key])
    return text.format(**kwargs) if kwargs else text