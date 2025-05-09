import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
import logging
from utils.woocommerce_client import WooCommerceClient
from utils.data_processor import DataProcessor
from utils.export_handler import ExportHandler
from utils.notification_handler import NotificationHandler
from utils.translations import Translations
import os
import sys

# Configure logging with more details
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('streamlit_app.log')
    ]
)

logger = logging.getLogger(__name__)

try:
    #Setting Environment Variables
    if os.environ.get('STREAMLIT_SERVER_PORT') is None:
        os.environ['STREAMLIT_SERVER_PORT'] = '5000'

    if os.environ.get('STREAMLIT_SERVER_ADDRESS') is None:
        os.environ['STREAMLIT_SERVER_ADDRESS'] = '0.0.0.0'

    logger.info("Environment variables set successfully")

    # Page configuration
    st.set_page_config(
        page_title="WooCommerce Dashboard",
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="collapsed"
    )

    # Initialize session state for page switching
    if 'show_dashboard' not in st.session_state:
        st.session_state.show_dashboard = False

    # Function to switch to dashboard
    def switch_to_dashboard():
        st.session_state.show_dashboard = True

    logger.info("Page configuration set successfully")

    # Initialize session state
    if 'woo_client' not in st.session_state:
        logger.info("Initializing WooCommerce client")
        st.session_state.woo_client = WooCommerceClient()

    # Initialize notification handler
    if 'notification_handler' not in st.session_state:
        logger.info("Initializing notification handler")
        st.session_state.notification_handler = NotificationHandler()
        
    # Initialize translations
    if 'translator' not in st.session_state:
        logger.info("Initializing translator")
        st.session_state.translator = Translations()
        
    # Initialize language selection (default to Norwegian)
    if 'language' not in st.session_state:
        st.session_state.language = 'no'
        
    # Helper function to get translated text
    def t(key, *args):
        return st.session_state.translator.get_text(key, st.session_state.language, *args)

    def get_date_range(view_period):
        """Calculate date range based on view period"""
        today = datetime.now().date()

        if view_period == 'Daglig':
            return today, today
        elif view_period == 'Ukentlig':
            # Get the start of the current week (Monday)
            start_of_week = today - timedelta(days=today.weekday())
            return start_of_week, today
        elif view_period == 'Månedlig':
            # Get the start of the current month
            start_of_month = today.replace(day=1)
            return start_of_month, today

        return today, today  # Default to daily view

    def calculate_net_profit():
        """Calculate today's net profit"""
        today = datetime.now().date()
        try:
            # Fetch today's orders
            orders = st.session_state.woo_client.get_orders(today, today)
            df, df_products = st.session_state.woo_client.process_orders_to_df(orders)

            if df.empty:
                return 0

            # Calculate metrics
            metrics = DataProcessor.calculate_metrics(df, df_products, 'daglig')

            # Calculate net profit
            total_profit = metrics['total_profit']
            order_count = metrics['order_count']
            ad_cost_per_order = 30
            total_ad_cost = order_count * ad_cost_per_order
            return round(total_profit - total_ad_cost)  # Rounded to nearest krone
        except Exception as e:
            logger.error(f"Error calculating net profit: {str(e)}")
            return 0

    def show_welcome_page():
        # Center the content vertically and horizontally
        st.markdown(
            """
            <style>
            .welcome-container {
                display: flex;
                justify-content: center;
                align-items: center;
                height: 80vh;
                flex-direction: column;
                text-align: center;
            }
            .welcome-text {
                font-size: 24px;
                margin-bottom: 20px;
            }
            .profit-number {
                font-size: 48px;
                font-weight: bold;
                color: #FF4B4B;
            }
            .click-anywhere {
                margin-top: 20px;
                font-size: 14px;
                color: #666;
            }
            </style>
            """,
            unsafe_allow_html=True
        )

        net_profit = calculate_net_profit()

        # Create a clickable container
        with st.container():
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                st.markdown(
                    f"""
                    <div class="welcome-container">
                        <div class="welcome-text">{t('welcome_text')}</div>
                        <div class="profit-number">kr {net_profit:,}</div>
                        <div class="click-anywhere">{t('click_anywhere')}</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            # Full width button with custom styling
            st.markdown("""
                <style>
                .stButton>button {
                    width: 100%;
                    height: 100vh;
                    background: none;
                    border: none;
                    position: fixed;
                    top: 0;
                    left: 0;
                    opacity: 0;
                    cursor: pointer;
                }
                </style>
            """, unsafe_allow_html=True)

            if st.button("Click anywhere", key="fullscreen_button"):
                st.session_state.show_dashboard = True
                st.rerun()

    def main():
        try:
            if not st.session_state.show_dashboard:
                show_welcome_page()
            else:
                # Show WooCommerce connection status when dashboard is visible
                st.success(t('connected_status'))

                # Header
                st.title(t('dashboard_title'))
                
                # Add a sidebar divider
                st.sidebar.title("⚙️ Settings")
                
                # Language selector
                language_options = {'no': 'Norsk', 'en': 'English'}
                selected_language = st.sidebar.selectbox(
                    t('select_language'),
                    options=list(language_options.keys()),
                    format_func=lambda x: language_options[x],
                    index=0 if st.session_state.language == 'no' else 1
                )
                
                # Update language if changed
                if selected_language != st.session_state.language:
                    st.session_state.language = selected_language
                    st.rerun()
                
                # Add a divider
                st.sidebar.markdown("---")

                # Debug mode toggle
                debug_mode = st.sidebar.checkbox(t('debug_mode'), value=True)
                if debug_mode:
                    st.sidebar.info(t('debug_info'))

                # Real-time notifications toggle
                notifications_enabled = st.sidebar.checkbox(t('enable_notifications'),
                                                            value=True)

                # Add sound toggle if notifications are enabled
                if notifications_enabled:
                    st.session_state.sound_enabled = st.sidebar.checkbox(
                        t('enable_sound'),
                        value=st.session_state.get('sound_enabled', True),
                        help=t('sound_help'))

                    # Add a placeholder for notifications
                    notification_placeholder = st.empty()

                    # Check for new orders every 30 seconds
                    if st.session_state.notification_handler.monitor_orders(
                            st.session_state.woo_client):
                        notification_placeholder.success(t('notification_success'))

                # Get period options based on language
                period_options = [t('daily'), t('weekly'), t('monthly')]
                
                # View period selector (before date range)
                view_period = st.selectbox(t('view_period'),
                                           options=period_options,
                                           index=0,
                                           help=t('view_period_help'))

                # Map display period to internal period
                period_map = {
                    t('daily'): 'Daglig',
                    t('weekly'): 'Ukentlig',
                    t('monthly'): 'Månedlig'
                }
                internal_period = period_map.get(view_period, 'Daglig')
                
                # Calculate date range based on view period
                start_date, end_date = get_date_range(internal_period)

                # Date range selector with calculated defaults
                st.subheader(t('date_range_header'))

                # Create two columns for date pickers
                col1, col2 = st.columns(2)

                with col1:
                    selected_start_date = st.date_input(
                        t('start_date'),
                        value=start_date,
                        help=t('date_help_start', start_date.strftime('%d.%m.%Y')),
                        format="DD.MM.YYYY")

                with col2:
                    selected_end_date = st.date_input(
                        t('end_date'),
                        value=end_date,
                        help=t('date_help_end', end_date.strftime('%d.%m.%Y')),
                        format="DD.MM.YYYY")

                # Validate date range
                if selected_start_date > selected_end_date:
                    st.error(t('date_error'))
                    return

                st.info(t('date_info', 
                    selected_start_date.strftime('%d.%m.%Y'), 
                    selected_end_date.strftime('%d.%m.%Y')))

                # Fetch and process data
                try:
                    with st.spinner(t('fetching_orders')):
                        orders = st.session_state.woo_client.get_orders(
                            selected_start_date, selected_end_date)

                        # Log API details instead of showing in sidebar
                        if debug_mode:
                            logging.debug(f"Raw order count: {len(orders)}")
                            if len(orders) > 0:
                                logging.debug("Sample order data: " + str({
                                    k: v
                                    for k, v in orders[0].items()
                                    if k in ['id', 'status', 'date_created', 'total']
                                }))

                        df, df_products = st.session_state.woo_client.process_orders_to_df(
                            orders)

                        if debug_mode and not df.empty:
                            logging.debug(f"Processed data shape: {df.shape}")

                except Exception as e:
                    st.error(t('error', str(e)))
                    if debug_mode:
                        logging.error(f"Detailed error: {str(e)}")
                    return

                if df.empty:
                    st.warning(t('no_orders_found', 
                        selected_start_date.strftime('%d.%m.%Y'),
                        selected_end_date.strftime('%d.%m.%Y')))
                    return

                # Calculate metrics once, before creating tabs
                try:
                    # Convert view_period to lowercase for processing
                    period = view_period.lower()

                    # Calculate metrics including profit
                    metrics = DataProcessor.calculate_metrics(df, df_products, period)
                except Exception as e:
                    st.error(t('error_calculating', str(e)))
                    return

                # Create tabs
                tab1, tab2, tab3, tab4, tab5 = st.tabs([
                    t('dashboard_tab'), 
                    t('invoices_tab'), 
                    t('customer_insights_tab'),
                    t('results_tab'), 
                    t('export_tab')
                ])

                with tab1:
                    # Display metrics in columns with 5 columns
                    col1, col2, col3, col4, col5 = st.columns(5)
                    with col1:
                        st.metric(
                            t('total_revenue_incl_vat'),
                            f"kr {metrics['total_revenue_incl_vat']:,.2f}",
                            help=t('total_revenue_incl_vat_help'))
                    with col2:
                        st.metric(t('total_revenue_excl_vat'),
                                  f"kr {metrics['total_revenue_excl_vat']:,.2f}",
                                  help=t('total_revenue_excl_vat_help'))
                    with col3:
                        st.metric(
                            t('total_profit'),
                            f"kr {metrics['total_profit']:,.2f}",
                            help=t('total_profit_help')
                        )
                    with col4:
                        st.metric(
                            t('shipping_costs'),
                            f"kr {metrics['shipping_costs']:,.2f}",
                            help=t('shipping_costs_help')
                        )
                    with col5:
                        st.metric(
                            t('total_shipping'),
                            f"kr {metrics['shipping_total']:,.2f}",
                            help=t('total_shipping_help')
                        )

                    # Add second row of metrics
                    col5, col6, col7, col8, col9 = st.columns(5)
                    with col5:
                        st.metric(t('total_tax'),
                                  f"kr {metrics['total_tax']:,.2f}",
                                  help=t('total_tax_help'))
                    with col6:
                        st.metric(t('profit_margin'),
                                  f"{metrics['profit_margin']:.1f}%",
                                  help=t('profit_margin_help'))
                    with col7:
                        st.metric(t('cogs'),
                                  f"kr {metrics['total_cogs']:,.2f}",
                                  help=t('cogs_help'))
                    with col8:
                        st.metric(t('order_count'),
                                  f"{metrics['order_count']}",
                                  help=t('order_count_help'))
                    with col9:
                        st.metric(t('total_products_sold'),
                                  f"{metrics['total_products_sold']}",
                                  help=t('total_products_sold_help'))

                    # Add explanation about calculations
                    st.info(t('calculation_info'))

                    # Display Top 10 Products
                    st.header(t('top_products'))
                    st.caption(t('period_caption', 
                             selected_start_date.strftime('%d.%m.%Y'), 
                             selected_end_date.strftime('%d.%m.%Y')))

                    # Add a stock refresh button above the product table
                    stock_col1, stock_col2 = st.columns([1, 4])
                    with stock_col1:
                        if st.button(t('refresh_stock'), help=t('refresh_stock_help')):
                            # If refresh button is clicked, force a refresh of stock data
                            with st.spinner(t('refreshing_stock')):
                                # Get all product IDs from the current df_products
                                product_ids = df_products['product_id'].unique()
                                # Refresh stock quantities with force_refresh=True
                                stock_quantities = st.session_state.woo_client.get_stock_quantities_batch(
                                    product_ids, force_refresh=True)
                                
                                # Update stock_quantity in df_products
                                for idx, row in df_products.iterrows():
                                    pid = row['product_id']
                                    df_products.at[idx, 'stock_quantity'] = stock_quantities.get(pid, 0)
                                
                                st.success(t('stock_refreshed'))
                    
                    # Get top products with updated stock quantities
                    top_products = DataProcessor.get_top_products(df_products)
                    if not top_products.empty:
                        st.dataframe(
                            top_products,
                            column_config={
                                "name":
                                    t('product_name_column'),
                                "sku":
                                    st.column_config.TextColumn(
                                        t('sku_column'),
                                        help=t('sku_help')
                                    ),
                                "product_id":
                                    st.column_config.NumberColumn(
                                        t('product_id_column'),
                                        help=t('product_id_help'),
                                        format="%d"  # Format as plain integer without commas
                                    ),
                                "Total Quantity":
                                    st.column_config.NumberColumn(
                                        t('quantity_sold_column'),
                                        help=t('quantity_sold_help')
                                    ),
                                "Stock Quantity":
                                    st.column_config.NumberColumn(
                                        t('stock_column'), help=t('stock_help'))
                            },
                            hide_index=False,
                            use_container_width=True)
                    else:
                        st.warning(t('no_product_data'))

                    # Revenue Trends
                    st.subheader(f"{t('revenue_trends')} ({view_period})")
                    revenue_chart = DataProcessor.create_revenue_chart(df, period)
                    if revenue_chart:
                        st.plotly_chart(revenue_chart, use_container_width=True)

                    # Customer List
                    st.header(t('customer_list'))
                    st.caption(t('period_caption',
                              selected_start_date.strftime('%d.%m.%Y'),
                              selected_end_date.strftime('%d.%m.%Y')))

                    customers_df = DataProcessor.get_customer_list(df)
                    if not customers_df.empty:
                        st.dataframe(
                            customers_df,
                            column_config={
                                "Name":
                                    t('customer_name'),
                                "Email":
                                    t('customer_email'),
                                "Order Date":
                                    st.column_config.DatetimeColumn(t('order_date'),
                                                                    format="DD.MM.YYYY HH:mm"),
                                "Payment Method":
                                    t('payment_method'),
                                "Shipping Method":
                                    t('shipping_method'),
                                "Total Orders":
                                    st.column_config.NumberColumn(t('order_total'),
                                                                  help=t('order_total_help'),
                                                                  format="kr %.2f")
                            },
                            hide_index=True,
                            use_container_width=True)
                    else:
                        st.warning(t('no_customer_data'))

                with tab2:
                    # Render invoice section in the second tab
                    def render_invoice_section(df, selected_start_date, selected_end_date):
                        """Render the invoice section in a separate tab"""
                        st.header(t('invoices_header'))
                        st.caption(t('period_caption',
                                   selected_start_date.strftime('%d.%m.%Y'),
                                   selected_end_date.strftime('%d.%m.%Y')))

                        if not df.empty:
                            invoice_data = []
                            for _, order in df.iterrows():
                                # Use the invoice data directly from the DataFrame instead of meta_data
                                if order['invoice_number']:
                                    invoice_url = st.session_state.woo_client.get_invoice_url(
                                        order['order_id'])
                                    invoice_data.append({
                                        t('invoice_number_column'):
                                            order['invoice_number'],
                                        t('order_number_column'):
                                            order['order_number'],
                                        t('invoice_date_column'):
                                            order['invoice_date'],
                                        t('status_column'):
                                            order['status'],
                                        t('total_column'):
                                            order['total'],
                                        'URL':
                                            invoice_url
                                    })

                            if invoice_data:
                                # Create DataFrame for invoices
                                invoices_df = pd.DataFrame(invoice_data)

                                # Display invoices in a table
                                st.dataframe(invoices_df.drop(columns=['URL']).style.format(
                                    {t('total_column'): 'kr {:,.2f}'}),
                                             column_config={
                                                 t('invoice_number_column'):
                                                     t('invoice_number_column'),
                                                 t('order_number_column'):
                                                     t('order_number_column'),
                                                 t('invoice_date_column'):
                                                     st.column_config.DatetimeColumn(
                                                         t('invoice_date_column'), format="DD.MM.YYYY HH:mm"),
                                                 t('status_column'):
                                                     t('status_column'),
                                                 t('total_column'):
                                                     t('total_column'),
                                             },
                                             hide_index=True)

                                # Add download section with improved styling
                                st.subheader(t('download_invoices'))
                                st.info(t('download_invoices_info'))

                                # Create columns for better layout of download links
                                cols = st.columns(3)
                                for idx, invoice in enumerate(invoice_data):
                                    col_idx = idx % 3
                                    if invoice['URL']:
                                        cols[col_idx].markdown(
                                            f"📄 [{invoice[t('invoice_number_column')]} - {invoice[t('order_number_column')]}]({invoice['URL']})"
                                        )
                            else:
                                st.info(t('no_invoices_found'))
                        else:
                            st.warning(t('no_order_data'))
                    render_invoice_section(df, selected_start_date, selected_end_date)

                with tab3:
                    # Customer Insights tab
                    st.header(t('customer_insights_header'))
                    st.caption(t('customer_insights_period',
                              selected_start_date.strftime('%d.%m.%Y'),
                              selected_end_date.strftime('%d.%m.%Y')))
                    
                    # Calculate customer insights
                    customer_insights = DataProcessor.get_customer_insights(df)
                    
                    if not df.empty:
                        # Key Metrics in a 4-column layout
                        col1, col2, col3, col4 = st.columns(4)
                        with col1:
                            st.metric(
                                t('repeat_customers'),
                                f"{customer_insights['repeat_customers']}",
                                help=t('repeat_customers_help')
                            )
                        
                        with col2:
                            st.metric(
                                t('new_customers'),
                                f"{customer_insights['new_customers']}",
                                help=t('new_customers_help')
                            )
                        
                        with col3:
                            st.metric(
                                t('customer_retention'),
                                f"{customer_insights['customer_retention']:.1f}%",
                                help=t('customer_retention_help')
                            )
                        
                        with col4:
                            st.metric(
                                t('avg_order_value'),
                                f"kr {customer_insights['avg_order_value']:,.2f}",
                                help=t('avg_order_value_help')
                            )
                        
                        # Customer Lifetime Value
                        customer_lifetime_col1, customer_lifetime_col2 = st.columns([1, 3])
                        with customer_lifetime_col1:
                            st.metric(
                                t('customer_lifetime_value'),
                                f"kr {customer_insights['customer_lifetime_value']:,.2f}",
                                help=t('customer_lifetime_value_help')
                            )
                        
                        # Top Cities
                        st.subheader(t('top_cities'))
                        if not customer_insights['top_cities'].empty:
                            st.dataframe(
                                customer_insights['top_cities'],
                                column_config={
                                    "City": st.column_config.TextColumn(t('city_name')),
                                    "Order Count": st.column_config.NumberColumn(t('order_count_by_city')),
                                    "Customer Count": st.column_config.NumberColumn(t('customer_count_by_city'))
                                },
                                hide_index=True,
                                use_container_width=True
                            )
                        
                        # Payment and Shipping Distribution
                        st.subheader(t('payment_distribution'))
                        payment_chart = DataProcessor.create_distribution_chart(
                            customer_insights['payment_distribution'],
                            t('payment_distribution'),
                            color_sequence=px.colors.qualitative.Pastel
                        )
                        if payment_chart:
                            st.plotly_chart(payment_chart, use_container_width=True)
                        
                        st.subheader(t('shipping_distribution'))
                        shipping_chart = DataProcessor.create_distribution_chart(
                            customer_insights['shipping_distribution'],
                            t('shipping_distribution'),
                            color_sequence=px.colors.qualitative.Pastel1
                        )
                        if shipping_chart:
                            st.plotly_chart(shipping_chart, use_container_width=True)
                    else:
                        st.warning(t('no_customer_data'))

                with tab4:
                    try:
                        # Create subtabs for basic results and CAC analysis
                        subtab1, subtab2 = st.tabs([t('results_header'), t('cac_analysis_header')])
                        
                        # Basic Results Subtab
                        with subtab1:
                            total_profit = metrics['total_profit']
                            order_count = metrics['order_count']
                            ad_cost_per_order = 30
                            total_ad_cost = order_count * ad_cost_per_order
                            net_profit = round(total_profit - total_ad_cost)  # Rounded to nearest krone

                            # Display the calculation components
                            col1, col2, col3 = st.columns(3)

                            with col1:
                                st.metric(
                                    t('total_gross_profit'),
                                    f"kr {total_profit:,.2f}",
                                    help=t('total_gross_profit_help')
                                )

                            with col2:
                                st.metric(
                                    t('ad_costs'),
                                    f"kr {total_ad_cost:,.2f}",
                                    help=t('ad_costs_help', ad_cost_per_order, order_count)
                                )

                            with col3:
                                st.metric(
                                    t('net_result'),
                                    f"kr {net_profit:,.0f}",  # Changed format to show no decimals
                                    help=t('net_result_help')
                                )

                            # Add explanation
                            st.info(t('calculation_method_info'))
                            
                        # CAC Analysis Subtab
                        with subtab2:
                            st.subheader(t('cac_vs_revenue_period', selected_start_date.strftime('%d.%m.%Y'), selected_end_date.strftime('%d.%m.%Y')))
                            
                            # Option to use external ad cost data (Google Analytics or Google Ads)
                            use_external_data = st.checkbox(t('ga_use_actual_costs'), 
                                                value=False, 
                                                help=t('ga_use_actual_costs_help'))
                            
                            # Add debug mode option for advanced users
                            debug_mode = st.checkbox("Debug modus for API testing",
                                                   value=False,
                                                   help="Aktiverer diagnostikk-modus for å feilsøke Google Analytics og Google Ads-integrasjonen")
                                                
                            # Calculate CAC metrics
                            cac_metrics = DataProcessor.calculate_cac_metrics(df, ad_cost_per_order=ad_cost_per_order, use_ga_data=use_external_data)
                            
                            # Display data source info message
                            if use_external_data:
                                if 'using_external_data' in cac_metrics and cac_metrics['using_external_data']:
                                    # Show data source info
                                    data_source = cac_metrics.get('data_source', 'unknown')
                                    if data_source == 'google_analytics':
                                        st.success("✅ Bruker annonsekostnader fra Google Analytics")
                                    elif data_source == 'google_ads':
                                        st.success("✅ Bruker annonsekostnader fra Google Ads API")
                                    else:
                                        st.success("✅ Bruker annonsekostnader fra ekstern kilde")
                                else:
                                    # Show error if present
                                    if 'error_message' in cac_metrics and cac_metrics['error_message']:
                                        error_msg = cac_metrics['error_message']
                                        
                                        # Check if it's a "no data" error
                                        if "No advertising cost data found" in error_msg or "No ad cost data found" in error_msg:
                                            st.info(f"ℹ️ {t('ga_no_data')}")
                                        else:
                                            # Display general error message
                                            st.warning(f"⚠️ {t('ga_error')}: {error_msg}")
                                        
                                        st.info(t('ga_fallback_notice', ad_cost_per_order))
                            
                            # Display debugging information if requested
                            if debug_mode and use_external_data:
                                st.subheader("Diagnoseinformasjon")
                                if 'diagnostic_info' in cac_metrics:
                                    diagnostic = cac_metrics['diagnostic_info']
                                    
                                    # Display diagnostic information in an expander
                                    with st.expander("Vis diagnoseinformasjon for API-tilkoblinger"):
                                        # Google Analytics diagnostics
                                        st.markdown("### Google Analytics API")
                                        if 'ga_attempted' in diagnostic and diagnostic['ga_attempted']:
                                            st.markdown("- ✅ Forsøkte å bruke Google Analytics API")
                                            
                                            if 'ga_success' in diagnostic and diagnostic['ga_success']:
                                                st.markdown("- ✅ Vellykket tilkobling til Google Analytics")
                                                if 'ga_spend' in diagnostic:
                                                    st.markdown(f"- Totale annonsekostnader: kr {diagnostic['ga_spend']:.2f}")
                                            elif 'ga_error' in diagnostic:
                                                st.markdown(f"- ❌ Google Analytics feil: {diagnostic['ga_error']}")
                                        else:
                                            st.markdown("- ❌ Google Analytics API ikke forsøkt")
                                        
                                        # Google Ads diagnostics
                                        st.markdown("### Google Ads API")
                                        if 'ads_attempted' in diagnostic and diagnostic['ads_attempted']:
                                            st.markdown("- ✅ Forsøkte å bruke Google Ads API")
                                            
                                            if 'ads_success' in diagnostic and diagnostic['ads_success']:
                                                st.markdown("- ✅ Vellykket tilkobling til Google Ads")
                                                if 'ads_spend' in diagnostic:
                                                    st.markdown(f"- Totale annonsekostnader: kr {diagnostic['ads_spend']:.2f}")
                                            elif 'ads_error' in diagnostic:
                                                st.markdown(f"- ❌ Google Ads feil: {diagnostic['ads_error']}")
                                        else:
                                            st.markdown("- ℹ️ Google Ads API ikke forsøkt (sannsynligvis fordi Google Analytics fungerte)")
                                                    
                                else:
                                    st.info("Ingen diagnoseinformasjon tilgjengelig")
                            
                            # Display key metrics
                            col1, col2, col3 = st.columns(3)
                            
                            with col1:
                                st.metric(
                                    t('cac_metric'),
                                    f"kr {cac_metrics['cac']:,.2f}",
                                    help=t('cac_metric_help')
                                )
                                
                                st.metric(
                                    t('roi_metric'),
                                    f"{cac_metrics['roi']:.1f}%",
                                    help=t('roi_metric_help')
                                )
                            
                            with col2:
                                st.metric(
                                    t('new_customers'),
                                    f"{cac_metrics['new_customers_count']}",
                                    help=t('new_customers_help')
                                )
                                
                                st.metric(
                                    t('repeat_customers'),
                                    f"{cac_metrics['repeat_customers_count']}",
                                    help=t('repeat_customers_help')
                                )
                            
                            with col3:
                                st.metric(
                                    t('cac_to_ltv_ratio'),
                                    f"{cac_metrics['cac_to_ltv_ratio']:.2f}",
                                    help=t('cac_to_ltv_ratio_help')
                                )
                                
                                st.metric(
                                    t('revenue_per_customer'),
                                    f"kr {cac_metrics['revenue_per_customer']:,.2f}",
                                    help=t('revenue_per_customer_help')
                                )
                                
                            # Show data source info if not shown already above
                            if not use_external_data:
                                st.info(t('ga_using_estimated_costs'))
                            
                            # Show campaign performance data if using external data sources and data is available
                            if 'using_external_data' in cac_metrics and cac_metrics['using_external_data'] and not cac_metrics['campaign_data'].empty:
                                with st.expander(t('ga_campaign_performance'), expanded=True):
                                    st.subheader(t('ga_campaign_performance_title'))
                                    # Format the campaign data for display
                                    display_df = cac_metrics['campaign_data'].copy()
                                    # Format currency columns
                                    display_df['Ad_Cost'] = display_df['Ad_Cost'].apply(lambda x: f"kr {x:.2f}")
                                    display_df['Revenue'] = display_df['Revenue'].apply(lambda x: f"kr {x:.2f}")
                                    # Format percentage columns
                                    display_df['ROI'] = display_df['ROI'].apply(lambda x: f"{x:.1f}%" if not pd.isna(x) else "N/A")
                                    # Format other columns
                                    display_df['CPA'] = display_df['CPA'].apply(lambda x: f"kr {x:.2f}" if not pd.isna(x) else "N/A")
                                    display_df['ROAS'] = display_df['ROAS'].apply(lambda x: f"{x:.2f}x" if not pd.isna(x) else "N/A")
                                    # Rename columns for display
                                    display_df.columns = ['Kampanje', 'Annonsekostnad', 'Transaksjoner', 'Inntekt', 'ROI', 'CPA', 'ROAS']
                                    
                                    # Display the table
                                    st.table(display_df)
                                    
                                    # Add campaign performance charts if there's more than one campaign
                                    if len(display_df) > 1:
                                        # Create bar chart for campaign performance
                                        raw_df = cac_metrics['campaign_data']
                                        fig = px.bar(
                                            raw_df,
                                            x='Campaign',
                                            y='ROI',
                                            title=t('ga_roi_per_campaign'),
                                            labels={'Campaign': 'Kampanje', 'ROI': 'ROI (%)'},
                                            color='ROI',
                                            color_continuous_scale='RdYlGn'
                                        )
                                        st.plotly_chart(fig, use_container_width=True)
                            
                            # Display trend charts
                            if not cac_metrics['cac_trend_data'].empty and len(cac_metrics['cac_trend_data']) > 1:
                                col1, col2 = st.columns(2)
                                
                                with col1:
                                    st.subheader(t('cac_trend_title'))
                                    st.caption(t('cac_trend_help'))
                                    cac_chart = DataProcessor.create_cac_trend_chart(cac_metrics['cac_trend_data'])
                                    st.plotly_chart(cac_chart, use_container_width=True)
                                
                                with col2:
                                    st.subheader(t('roi_trend_title'))
                                    st.caption(t('roi_trend_help'))
                                    roi_chart = DataProcessor.create_roi_trend_chart(cac_metrics['roi_trend_data'])
                                    st.plotly_chart(roi_chart, use_container_width=True)
                            else:
                                st.info(t('not_enough_trend_data'))
                            
                            # Additional info
                            st.info(t('cac_analysis_info'))
                    except Exception as e:
                        st.error(t('result_error', str(e)))

                with tab5:
                    # Export tab content
                    st.header(t('export_header'))
                    st.caption(t('period_caption',
                              selected_start_date.strftime('%d.%m.%Y'),
                              selected_end_date.strftime('%d.%m.%Y')))

                    # Create two columns for export options
                    export_col1, export_col2 = st.columns(2)

                    with export_col1:
                        st.subheader(t('export_orders'))
                        export_format = st.selectbox(
                            t('select_format_orders'),
                            options=['CSV', 'Excel', 'JSON', 'PDF'],
                            key='orders_export_format')
                        ExportHandler.export_data(df, "orders", export_format)

                    with export_col2:
                        st.subheader(t('export_products'))
                        export_format_products = st.selectbox(
                            t('select_format_products'),
                            options=['CSV', 'Excel', 'JSON', 'PDF'],
                            key='products_export_format')
                        ExportHandler.export_data(df_products, "products",
                                                   export_format_products)

        except Exception as e:
            logger.error(f"Failed to start application: {str(e)}", exc_info=True)
            st.error(f"An error occurred while starting the application: {str(e)}")
            sys.exit(1)

    if __name__ == "__main__":
        try:
            logger.info("Starting main application")
            main()
            logger.info("Application started successfully")
        except Exception as e:
            logger.error(f"Failed to start application: {str(e)}", exc_info=True)
            st.error(f"An error occurred while starting the application: {str(e)}")
            sys.exit(1)

except Exception as e:
    logger.error(f"Critical error during startup: {str(e)}", exc_info=True)
    st.error("""
    Failed to initialize the application. Please check the following:
    1. All required environment variables are set
    2. The port 5000 is available
    3. You have sufficient permissions

    Error details: {str(e)}
    """)
    sys.exit(1)