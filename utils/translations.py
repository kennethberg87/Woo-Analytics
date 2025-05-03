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
                'customer_insights_tab': '👥 Kundeanalyse',
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
                'shipping_costs': 'Fraktkostnader',
                'shipping_costs_help': 'Isolerte fraktkostnader (eks. MVA)',
                'total_tax': 'Total MVA',
                'total_tax_help': 'Total VAT collected (including shipping VAT)',
                'profit_margin': 'Fortjenestemargin',
                'profit_margin_help': 'Profit as percentage of revenue (excl. VAT)',
                'cogs': 'Kostnad for solgte varer',
                'cogs_help': 'Total cost of products sold (excl. VAT)',
                'order_count': 'Antall ordrer',
                'order_count_help': 'Total number of orders in selected period',
                'total_products_sold': 'Totalt produkter solgt',
                'total_products_sold_help': 'Totalt antall produkter solgt i perioden',
                
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
                'sku_column': 'SKU',
                'sku_help': 'Produktkode',
                'product_id_column': 'Produkt-ID',
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
                
                # Customer Insights section
                'customer_insights_header': '👥 Kundeanalyse',
                'customer_insights_period': 'Kundeanalyse for perioden: {} til {}',
                'repeat_customers': 'Gjenkjøpskunder',
                'repeat_customers_help': 'Kunder som har handlet mer enn én gang',
                'new_customers': 'Nye kunder',
                'new_customers_help': 'Kunder som har handlet for første gang i valgt periode',
                'customer_retention': 'Kundelojalitet',
                'customer_retention_help': 'Prosentandel av gjenkjøpskunder',
                'avg_order_value': 'Gjennomsnittlig ordreverdi',
                'avg_order_value_help': 'Gjennomsnittlig beløp per ordre',
                'top_cities': 'Topp byer',
                'top_cities_help': 'De mest populære byene basert på antall ordre',
                'customer_lifetime_value': 'Kundeverdi (LTV)',
                'customer_lifetime_value_help': 'Gjennomsnittlig totalverdi per kunde over tid',
                'city_distribution': 'Geografisk fordeling',
                'city_name': 'By',
                'order_count_by_city': 'Antall ordre',
                'customer_count_by_city': 'Antall kunder',
                'payment_distribution': 'Fordeling av betalingsmetoder',
                'shipping_distribution': 'Fordeling av fraktmetoder',
                
                # Invoices section
                'invoices_header': 'Fakturaer',
                'invoice_number_column': 'Fakturanummer',
                'order_number_column': 'Ordrenummer',
                'invoice_date_column': 'Fakturadato',
                'status_column': 'Status',
                'total_column': 'Total',
                'download_invoices': 'Last ned fakturaer',
                'download_invoices_info': """
                💡 Klikk på lenkene under for å laste ned PDF-fakturaer direkte. 
                Fakturaene vil lastes ned automatisk når du klikker på linken.
                """,
                'no_invoices_found': 'Ingen fakturaer funnet for valgt periode',
                'no_order_data': 'Ingen ordredata tilgjengelig for valgt periode',
                
                # Results tab
                'results_header': '📈 Resultatberegning',
                'total_gross_profit': 'Total fortjeneste',
                'total_gross_profit_help': 'Total fortjeneste før annonsekostnader',
                'ad_costs': 'Annonsekostnader',
                'ad_costs_help': 'Beregnet som kr {} per ordre x {} ordrer',
                'net_result': 'Netto resultat',
                'net_result_help': 'Total fortjeneste minus annonsekostnader',
                'calculation_method_info': """
                💡 Beregningsmetode:
                - Total fortjeneste er brutto fortjeneste før annonsekostnader
                - Annonsekostnad er beregnet som kr 30 per ordre
                - Netto resultat er total fortjeneste minus annonsekostnader
                """,
                'result_error': 'Feil ved beregning av resultatkalkuleringer: {}',
                
                # CAC vs. Revenue Analysis
                'cac_analysis_header': 'Kundeakvisisjonskostnad Analyse',
                'cac_vs_revenue_period': 'CAC vs. Omsetning analyse for perioden: {} til {}',
                'cac_metric': 'Kundeakvisisjonskostnad (CAC)',
                'cac_metric_help': 'Gjennomsnittskostnad for å skaffe en ny kunde',
                'cac_to_ltv_ratio': 'CAC til LTV forhold',
                'cac_to_ltv_ratio_help': 'Kundens livstidsverdi delt på CAC (høyere er bedre, >3 er god)',
                'roi_metric': 'Markedsføring ROI',
                'roi_metric_help': 'Avkastning på investeringer i markedsføring',
                'breakeven_point': 'Nullpunkt',
                'breakeven_point_help': 'Antall kjøp som trengs for å dekke akvisisjonskostnaden',
                'new_customers': 'Nye kunder',
                'new_customers_help': 'Antall førstegangskunder i denne perioden',
                'repeat_customers': 'Gjentakende kunder',
                'repeat_customers_help': 'Antall returnerende kunder i denne perioden',
                'revenue_per_customer': 'Omsetning per kunde',
                'revenue_per_customer_help': 'Gjennomsnittlig omsetning generert per kunde',
                'cac_trend_title': 'CAC Trendanalyse',
                'roi_trend_title': 'ROI Trendanalyse',
                'cac_trend_help': 'Hvordan kundeakvisisjonskostnaden har endret seg over tid',
                'roi_trend_help': 'Hvordan markedsføringens avkastning har endret seg over tid',
                'cac_analysis_info': """
                💡 Om CAC Analyse:
                - Kundeakvisisjonskostnad (CAC) beregnes ved å dele totale markedsføringskostnader på antall nye kunder
                - Avkastning på investering (ROI) viser effektiviteten av markedsføringsutgifter
                - Et CAC:LTV-forhold større enn 3:1 indikerer god enhetøkonomi
                """,
                'not_enough_trend_data': "Ikke nok data for å vise trendanalyse. Velg en lengre tidsperiode.",
                'ga_use_actual_costs': "Bruk faktiske annonsekostnader fra Google Analytics",
                'ga_use_actual_costs_help': "Henter faktiske annonsekostnader fra Google Analytics i stedet for å bruke et estimat",
                'ga_using_actual_costs': "Bruker faktiske annonsekostnader fra Google Analytics",
                'ga_using_estimated_costs': "Bruker estimerte annonsekostnader basert på antall ordre",
                'ga_connection_error': "Kunne ikke hente data fra Google Analytics. Bruker estimerte kostnader i stedet.",
                'ga_error': "Google Analytics-feil",
                'ga_fallback_notice': "Bruker estimerte kostnader på kr {} per ordre i stedet.",
                'ga_no_data': "Ingen annonsekostnader funnet i Google Analytics for valgt periode. Prøv å velge en annen datoperiode.",
                'ga_campaign_performance': "Kampanjeytelse (fra Google Analytics)",
                'ga_campaign_performance_title': "Ytelse per kampanje",
                'ga_roi_per_campaign': "ROI per kampanje",
                
                # Export tab
                'export_header': 'Eksporter data',
                'export_orders': 'Eksporter ordredata',
                'export_products': 'Eksporter produktdata',
                'select_format_orders': 'Velg filformat for eksport av ordredata',
                'select_format_products': 'Velg filformat for eksport av produktdata',
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
                'customer_insights_tab': '👥 Customer Insights',
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
                'shipping_costs': 'Shipping costs',
                'shipping_costs_help': 'Isolated shipping costs (excl. VAT)',
                'total_tax': 'Total VAT',
                'total_tax_help': 'Total VAT collected (including shipping VAT)',
                'profit_margin': 'Profit margin',
                'profit_margin_help': 'Profit as percentage of revenue (excl. VAT)',
                'cogs': 'Cost of goods sold',
                'cogs_help': 'Total cost of products sold (excl. VAT)',
                'order_count': 'Order count',
                'order_count_help': 'Total number of orders in selected period',
                'total_products_sold': 'Total products sold',
                'total_products_sold_help': 'Total number of products sold in the period',
                
                # Explanations
                'calculation_info': """
                💡 Calculation of revenue and profit:
                - Total revenue (incl. VAT): Total product sales including VAT, excl. shipping
                - Total revenue (excl. VAT): Total revenue excl. VAT and shipping.
                - Shipping costs are shown excl. VAT
                - Cost: Total product cost (excl. VAT)
                """,
                
                # Products section
                'top_products': '10 best-selling products based on quantity',
                'period_caption': 'For the period: {} to {}',
                'product_name_column': 'Product name',
                'sku_column': 'SKU',
                'sku_help': 'Product code',
                'product_id_column': 'Product ID',
                'product_id_help': 'Unique identifier for the product',
                'quantity_sold_column': 'Quantity sold',
                'quantity_sold_help': 'Total quantity sold of this product within the selected period',
                'stock_column': 'In stock',
                'stock_help': 'Current stock quantity',
                'no_product_data': 'No product data available for the selected date range',
                'refresh_stock': 'Refresh stock',
                'refresh_stock_help': 'Get the latest stock quantity data from WooCommerce',
                'refreshing_stock': 'Refreshing stock quantities...',
                'stock_refreshed': 'Stock quantities refreshed successfully',
                
                # Revenue and Customers section
                'revenue_trends': 'Revenue',
                'customer_list': 'Customer overview',
                'customer_name': 'Customer name',
                'customer_email': 'Email address',
                'order_date': 'Order date',
                'payment_method': 'Payment method',
                'shipping_method': 'Shipping method',
                'order_total': 'Order total',
                'order_total_help': 'Total amount for the order',
                'no_customer_data': 'No customer data available for the selected date range',
                
                # Customer Insights section
                'customer_insights_header': '👥 Kundeanalyse',
                'customer_insights_period': 'Kundeanalyse for perioden: {} til {}',
                'repeat_customers': 'Gjenkjøpende kunder',
                'repeat_customers_help': 'Kunder som har foretatt mer enn ett kjøp',
                'new_customers': 'Nye kunder',
                'new_customers_help': 'Kunder som foretok sitt første kjøp i valgt periode',
                'customer_retention': 'Kundelojalitet',
                'customer_retention_help': 'Prosentandel gjenkjøpende kunder',
                'avg_order_value': 'Gjennomsnittlig ordrestørrelse',
                'avg_order_value_help': 'Gjennomsnittlig beløp per ordre',
                'top_cities': 'Topp byer',
                'top_cities_help': 'Mest populære byer basert på antall ordrer',
                'customer_lifetime_value': 'Kundeverdi (LTV)',
                'customer_lifetime_value_help': 'Gjennomsnittlig totalverdi per kunde over tid',
                'city_distribution': 'Geografisk fordeling',
                'city_name': 'By',
                'order_count_by_city': 'Antall ordrer',
                'customer_count_by_city': 'Antall kunder',
                'payment_distribution': 'Fordeling av betalingsmetoder',
                'shipping_distribution': 'Fordeling av fraktmetoder',
                
                # Invoices section
                'invoices_header': 'Invoices',
                'invoice_number_column': 'Invoice number',
                'order_number_column': 'Order number',
                'invoice_date_column': 'Invoice date',
                'status_column': 'Status',
                'total_column': 'Total',
                'download_invoices': 'Download invoices',
                'download_invoices_info': """
                💡 Click on the links below to download PDF invoices directly. 
                The invoices will be downloaded automatically when you click on the link.
                """,
                'no_invoices_found': 'No invoices found for the selected period',
                'no_order_data': 'No order data available for the selected period',
                
                # Results tab
                'results_header': '📈 Results calculation',
                'total_gross_profit': 'Total gross profit',
                'total_gross_profit_help': 'Total profit before advertising costs',
                'ad_costs': 'Advertising costs',
                'ad_costs_help': 'Calculated as kr {} per order x {} orders',
                'net_result': 'Net result',
                'net_result_help': 'Total profit minus advertising costs',
                'calculation_method_info': """
                💡 Calculation method:
                - Total gross profit is before advertising costs
                - Advertising cost is calculated as kr 30 per order
                - Net result is total profit minus advertising costs
                """,
                'result_error': 'Error calculating result metrics: {}',
                
                # CAC vs. Revenue Analysis
                'cac_analysis_header': 'Customer Acquisition Cost Analysis',
                'cac_vs_revenue_period': 'CAC vs. Revenue analysis for the period: {} to {}',
                'cac_metric': 'Customer Acquisition Cost (CAC)',
                'cac_metric_help': 'Average cost to acquire a new customer',
                'cac_to_ltv_ratio': 'CAC to LTV Ratio',
                'cac_to_ltv_ratio_help': 'Lifetime Value divided by CAC (higher is better, >3 is good)',
                'roi_metric': 'Marketing ROI',
                'roi_metric_help': 'Return on Investment for marketing spend',
                'breakeven_point': 'Breakeven Point',
                'breakeven_point_help': 'Number of purchases needed to cover acquisition cost',
                'new_customers': 'New Customers',
                'new_customers_help': 'Number of first-time customers in this period',
                'repeat_customers': 'Repeat Customers',
                'repeat_customers_help': 'Number of returning customers in this period',
                'revenue_per_customer': 'Revenue per Customer',
                'revenue_per_customer_help': 'Average revenue generated per customer',
                'cac_trend_title': 'CAC Trend Analysis',
                'roi_trend_title': 'ROI Trend Analysis',
                'cac_trend_help': 'How customer acquisition cost has changed over time',
                'roi_trend_help': 'How marketing return on investment has changed over time',
                'cac_analysis_info': """
                💡 About CAC Analysis:
                - Customer Acquisition Cost (CAC) is calculated by dividing total marketing spend by number of new customers acquired
                - Return on Investment (ROI) shows the effectiveness of marketing spend
                - A CAC:LTV ratio greater than 3:1 indicates good unit economics
                """,
                'not_enough_trend_data': "Not enough data to show trend analysis. Please select a longer time period.",
                'ga_use_actual_costs': "Use actual advertising costs from Google Analytics",
                'ga_use_actual_costs_help': "Fetches actual advertising costs from Google Analytics instead of using an estimate",
                'ga_using_actual_costs': "Using actual advertising costs from Google Analytics",
                'ga_using_estimated_costs': "Using estimated advertising costs based on order count",
                'ga_connection_error': "Could not fetch data from Google Analytics. Using estimated costs instead.",
                'ga_error': "Google Analytics Error",
                'ga_fallback_notice': "Using estimated costs of kr {} per order instead.",
                'ga_no_data': "No advertising cost data found in Google Analytics for the selected period. Try selecting a different date range.",
                'ga_campaign_performance': "Campaign performance (from Google Analytics)",
                'ga_campaign_performance_title': "Performance by campaign",
                'ga_roi_per_campaign': "ROI per campaign",
                
                # Export tab
                'export_header': 'Export data',
                'export_orders': 'Export order data',
                'export_products': 'Export product data',
                'select_format_orders': 'Select file format for order data export',
                'select_format_products': 'Select file format for product data export',
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