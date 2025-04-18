import streamlit as st
import pandas as pd
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
                    col5, col6, col7, col8 = st.columns(4)
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

                    # Add explanation about calculations
                    st.info(t('calculation_info'))

                    # Display Top 10 Products
                    st.header(t('top_products'))
                    st.caption(t('period_caption', 
                             selected_start_date.strftime('%d.%m.%Y'), 
                             selected_end_date.strftime('%d.%m.%Y')))

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
                                invoice_details = st.session_state.woo_client.get_invoice_details(
                                    order['meta_data'])
                                if invoice_details['invoice_number']:
                                    invoice_url = st.session_state.woo_client.get_invoice_url(
                                        order['order_id'])
                                    invoice_data.append({
                                        t('invoice_number_column'):
                                            invoice_details['invoice_number'],
                                        t('order_number_column'):
                                            invoice_details['order_number'],
                                        t('invoice_date_column'):
                                            invoice_details['invoice_date'],
                                        t('status_column'):
                                            st.session_state.woo_client.get_order_status_display(
                                                order['status']),
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
                    try:
                        # Results tab
                        st.header(t('results_header'))

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
                    except Exception as e:
                        st.error(t('result_error', str(e)))

                with tab4:
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