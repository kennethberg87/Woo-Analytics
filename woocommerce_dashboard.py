import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import logging
from utils.woocommerce_client import WooCommerceClient
from utils.data_processor import DataProcessor
from utils.export_handler import ExportHandler
from utils.notification_handler import NotificationHandler
from utils.translations import get_text
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

    # Initialize session state for page switching and language
    if 'show_dashboard' not in st.session_state:
        st.session_state.show_dashboard = False
    if 'language' not in st.session_state:
        st.session_state.language = 'no'  # Default to Norwegian

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

    def get_date_range(view_period):
        """Calculate date range based on view period"""
        today = datetime.now().date()

        if view_period == get_text('daily', st.session_state.language):
            return today, today
        elif view_period == get_text('weekly', st.session_state.language):
            start_of_week = today - timedelta(days=today.weekday())
            return start_of_week, today
        elif view_period == get_text('monthly', st.session_state.language):
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
            metrics = DataProcessor.calculate_metrics(df, df_products, 'daily')

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
                        <div class="welcome-text">{get_text('welcome_greeting', st.session_state.language)}</div>
                        <div class="profit-number">kr {net_profit:,}</div>
                        <div class="click-anywhere">{get_text('click_anywhere', st.session_state.language)}</div>
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
                st.success(get_text('api_connected', st.session_state.language))

                # Header
                st.title(get_text('dashboard_title', st.session_state.language))

                # Language selector in sidebar
                lang = st.sidebar.selectbox(
                    "Language / Språk",
                    options=['Norsk', 'English'],
                    index=0 if st.session_state.language == 'no' else 1,
                    key='sidebar_lang'
                )
                new_language = 'no' if lang == 'Norsk' else 'en'

                # Only update language if it changed
                if new_language != st.session_state.language:
                    st.session_state.language = new_language
                    st.rerun()  # Rerun to update UI without refetching data

                # Initialize data session state
                if 'current_data' not in st.session_state:
                    st.session_state.current_data = {
                        'df': None,
                        'df_products': None,
                        'start_date': None,
                        'end_date': None,
                        'view_period': None
                    }

                # Debug mode toggle
                debug_mode = st.sidebar.checkbox(get_text('debug_mode', st.session_state.language), value=True)
                if debug_mode:
                    st.sidebar.info(get_text('debug_info', st.session_state.language))

                # Real-time notifications toggle
                notifications_enabled = st.sidebar.checkbox(
                    get_text('enable_notifications', st.session_state.language),
                    value=True
                )

                # Add sound toggle if notifications are enabled
                if notifications_enabled:
                    st.session_state.sound_enabled = st.sidebar.checkbox(
                        get_text('enable_sound', st.session_state.language),
                        value=st.session_state.get('sound_enabled', True),
                        help=get_text('sound_help', st.session_state.language)
                    )

                    # Add a placeholder for notifications
                    notification_placeholder = st.empty()

                    # Check for new orders every 30 seconds
                    if st.session_state.notification_handler.monitor_orders(
                            st.session_state.woo_client):
                        notification_placeholder.success(
                            get_text('notifications_active', st.session_state.language)
                        )

                # View period selector
                view_period = st.selectbox(
                    get_text('select_period', st.session_state.language),
                    options=[
                        get_text('daily', st.session_state.language),
                        get_text('weekly', st.session_state.language),
                        get_text('monthly', st.session_state.language)
                    ],
                    index=0,
                    help=get_text('period_help', st.session_state.language)
                )

                # Calculate date range based on view period
                start_date, end_date = get_date_range(view_period)

                # Date range selector with calculated defaults
                st.subheader(get_text('order_period', st.session_state.language))

                # Create two columns for date pickers
                col1, col2 = st.columns(2)

                with col1:
                    selected_start_date = st.date_input(
                        get_text('start_date', st.session_state.language),
                        value=start_date,
                        help=f"{get_text('start_date_help', st.session_state.language)} (default: {start_date.strftime('%d.%m.%Y')})",
                        format="DD.MM.YYYY"
                    )

                with col2:
                    selected_end_date = st.date_input(
                        get_text('end_date', st.session_state.language),
                        value=end_date,
                        help=f"{get_text('end_date_help', st.session_state.language)} (default: {end_date.strftime('%d.%m.%Y')})",
                        format="DD.MM.YYYY"
                    )

                # Validate date range
                if selected_start_date > selected_end_date:
                    st.error(get_text('date_range_error', st.session_state.language))
                    return

                st.info(
                    get_text('based_on_orders', st.session_state.language,
                            start_date=selected_start_date.strftime('%d.%m.%Y'),
                            end_date=selected_end_date.strftime('%d.%m.%Y'))
                )

                # Only fetch new data if date range or view period changed
                data_changed = (
                    st.session_state.current_data['start_date'] != selected_start_date or
                    st.session_state.current_data['end_date'] != selected_end_date or
                    st.session_state.current_data['view_period'] != view_period
                )

                if data_changed:
                    try:
                        with st.spinner(get_text('loading_orders', st.session_state.language)):
                            orders = st.session_state.woo_client.get_orders(selected_start_date, selected_end_date)
                            df, df_products = st.session_state.woo_client.process_orders_to_df(orders)

                            # Update session state with new data
                            st.session_state.current_data = {
                                'df': df,
                                'df_products': df_products,
                                'start_date': selected_start_date,
                                'end_date': selected_end_date,
                                'view_period': view_period
                            }
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
                        if debug_mode:
                            logging.error(f"Detailed error: {str(e)}")
                        return
                else:
                    # Use cached data
                    df = st.session_state.current_data['df']
                    df_products = st.session_state.current_data['df_products']

                if df.empty:
                    st.warning(
                        get_text('no_orders', st.session_state.language,
                                start_date=selected_start_date,
                                end_date=selected_end_date)
                    )
                    return

                # Calculate metrics
                try:
                    period = view_period.lower()
                    metrics = DataProcessor.calculate_metrics(df, df_products, period)
                except Exception as e:
                    st.error(f"Error calculating metrics: {str(e)}")
                    return

                # Create tabs
                tab1, tab2, tab3, tab4 = st.tabs([get_text('tab_dashboard', st.session_state.language), get_text('tab_invoices', st.session_state.language), get_text('tab_result', st.session_state.language), get_text('tab_export', st.session_state.language)])

                with tab1:
                    # Display metrics in columns
                    col1, col2, col3, col4, col5 = st.columns(5)
                    with col1:
                        st.metric(
                            get_text('total_revenue_vat', st.session_state.language),
                            f"kr {metrics['total_revenue_incl_vat']:,.2f}",
                            help=get_text('total_revenue_vat_help', st.session_state.language)
                        )
                    with col2:
                        st.metric(
                            get_text('total_revenue_ex_vat', st.session_state.language),
                            f"kr {metrics['total_revenue_excl_vat']:,.2f}",
                            help=get_text('total_revenue_ex_vat_help', st.session_state.language)
                        )
                    with col3:
                        st.metric(
                            get_text('total_profit', st.session_state.language),
                            f"kr {metrics['total_profit']:,.2f}",
                            help=get_text('total_profit_help', st.session_state.language)
                        )
                    with col4:
                        st.metric(
                            get_text('total_shipping', st.session_state.language),
                            f"kr {metrics['shipping_total']:,.2f}",
                            help=get_text('total_shipping_help', st.session_state.language)
                        )
                    with col5:
                        pass

                    # Add second row of metrics
                    col5, col6, col7, col8 = st.columns(4)
                    with col5:
                        st.metric(
                            get_text('total_vat', st.session_state.language),
                            f"kr {metrics['total_tax']:,.2f}",
                            help=get_text('total_vat_help', st.session_state.language)
                        )
                    with col6:
                        st.metric(
                            get_text('profit_margin', st.session_state.language),
                            f"{metrics['profit_margin']:.1f}%",
                            help=get_text('profit_margin_help', st.session_state.language)
                        )
                    with col7:
                        st.metric(
                            get_text('cogs', st.session_state.language),
                            f"kr {metrics['total_cogs']:,.2f}",
                            help=get_text('cogs_help', st.session_state.language)
                        )
                    with col8:
                        st.metric(
                            get_text('order_count', st.session_state.language),
                            f"{metrics['order_count']}",
                            help=get_text('order_count_help', st.session_state.language)
                        )

                    # Add explanation about calculations
                    st.info(get_text('calculations_info', st.session_state.language))

                    # Display Top 10 Products
                    st.header(get_text('top_products_header', st.session_state.language))
                    st.caption(
                        get_text('period_caption', st.session_state.language,
                                 start_date=selected_start_date.strftime('%d.%m.%Y'),
                                 end_date=selected_end_date.strftime('%d.%m.%Y'))
                    )

                    top_products = DataProcessor.get_top_products(df_products)
                    if not top_products.empty:
                        st.dataframe(
                            top_products,
                            column_config={
                                "name":
                                    get_text('product_name', st.session_state.language),
                                "product_id":
                                    st.column_config.NumberColumn(
                                        get_text('product_id', st.session_state.language),
                                        help=get_text('product_id_help', st.session_state.language),
                                        format="%d"  # Format as plain integer without commas
                                    ),
                                "quantity_sold":
                                    st.column_config.NumberColumn(
                                        get_text('quantity_sold', st.session_state.language),
                                        help=get_text('quantity_sold_help', st.session_state.language)
                                    ),
                                "stock":
                                    st.column_config.NumberColumn(
                                        get_text('stock', st.session_state.language),
                                        help=get_text('stock_quantity_help', st.session_state.language)
                                    )
                            },
                            hide_index=False,
                            use_container_width=True)
                    else:
                        st.warning(get_text('no_product_data', st.session_state.language))

                    # Revenue Trends
                    st.subheader(get_text('revenue_trends', st.session_state.language, period=view_period))
                    revenue_chart = DataProcessor.create_revenue_chart(df, period)
                    if revenue_chart:
                        st.plotly_chart(revenue_chart, use_container_width=True)

                    # Customer List
                    st.header(get_text('customer_overview', st.session_state.language))
                    st.caption(
                        get_text('period_caption', st.session_state.language,
                                 start_date=selected_start_date.strftime('%d.%m.%Y'),
                                 end_date=selected_end_date.strftime('%d.%m.%Y'))
                    )

                    customers_df = DataProcessor.get_customer_list(df)
                    if not customers_df.empty:
                        st.dataframe(
                            customers_df,
                            column_config={
                                "Name":
                                    get_text('customer_name', st.session_state.language),
                                "Email":
                                    get_text('customer_email', st.session_state.language),
                                "Order Date":
                                    st.column_config.DatetimeColumn(get_text('order_date', st.session_state.language),
                                                                    format="DD.MM.YYYY HH:mm"),
                                "Payment Method":
                                    get_text('payment_method', st.session_state.language),
                                "Shipping Method":
                                    get_text('shipping_method', st.session_state.language),
                                "Total Orders":
                                    st.column_config.NumberColumn(get_text('order_total', st.session_state.language),
                                                                  help=get_text('order_total_help', st.session_state.language),
                                                                  format="kr %.2f")
                            },
                            hide_index=True,
                            use_container_width=True)
                    else:
                        st.warning(get_text('no_customer_data', st.session_state.language))

                with tab2:
                    # Render invoice section in the second tab
                    def render_invoice_section(df, selected_start_date, selected_end_date):
                        """Render the invoice section in a separate tab"""
                        st.header(get_text('invoices_header', st.session_state.language))
                        st.caption(
                            get_text('period_caption', st.session_state.language,
                                     start_date=selected_start_date.strftime('%d.%m.%Y'),
                                     end_date=selected_end_date.strftime('%d.%m.%Y'))
                        )

                        if not df.empty:
                            invoice_data = []
                            for _, order in df.iterrows():
                                invoice_details = st.session_state.woo_client.get_invoice_details(
                                    order['meta_data'])
                                if invoice_details['invoice_number']:
                                    invoice_url = st.session_state.woo_client.get_invoice_url(
                                        order['order_id'])
                                    invoice_data.append({
                                        'Fakturanummer':
                                            invoice_details['invoice_number'],
                                        'Ordrenummer':
                                            invoice_details['order_number'],
                                        'Fakturadato':
                                            invoice_details['invoice_date'],
                                        'Status':
                                            st.session_state.woo_client.get_order_status_display(
                                                order['status']),
                                        'Total':
                                            order['total'],
                                        'URL':
                                            invoice_url
                                    })

                            if invoice_data:
                                # Create DataFrame for invoices
                                invoices_df = pd.DataFrame(invoice_data)

                                # Display invoices in a table
                                st.dataframe(invoices_df.drop(columns=['URL']).style.format(
                                    {'Total': 'kr {:,.2f}'}),
                                             column_config={
                                                 "Fakturanummer":
                                                     get_text('invoice_number', st.session_state.language),
                                                 "Ordrenummer":
                                                     get_text('order_number', st.session_state.language),
                                                 "Fakturadato":
                                                     st.column_config.DatetimeColumn(
                                                         get_text('invoice_date', st.session_state.language), format="DD.MM.YYYY HH:mm"),
                                                 "Status":
                                                     get_text('status', st.session_state.language),
                                                 "Total":
                                                     get_text('total', st.session_state.language),
                                             },
                                             hide_index=True)

                                # Add download section with improved styling
                                st.subheader(get_text('download_invoices', st.session_state.language))
                                st.info(get_text('download_info', st.session_state.language))

                                # Create columns for better layout of download links
                                cols = st.columns(3)
                                for idx, invoice in enumerate(invoice_data):
                                    col_idx = idx % 3
                                    if invoice['URL']:
                                        cols[col_idx].markdown(
                                            f"📄 [{invoice['Fakturanummer']} - {invoice['Ordrenummer']}]({invoice['URL']})"
                                        )
                            else:
                                st.info(get_text('no_invoices', st.session_state.language))
                        else:
                            st.warning(get_text('no_order_data', st.session_state.language))
                    render_invoice_section(df, selected_start_date, selected_end_date)

                with tab3:
                    try:
                        # Resultat tab
                        st.header(get_text('result_header', st.session_state.language))

                        total_profit = metrics['total_profit']
                        order_count = metrics['order_count']
                        ad_cost_per_order = 30
                        total_ad_cost = order_count * ad_cost_per_order
                        net_profit = round(total_profit - total_ad_cost)  # Rounded to nearest krone

                        # Display the calculation components
                        col1, col2, col3 = st.columns(3)

                        with col1:
                            st.metric(
                                get_text('total_profit', st.session_state.language),
                                f"kr {total_profit:,.2f}",
                                help=get_text('total_profit_before_costs', st.session_state.language)
                            )

                        with col2:
                            st.metric(
                                get_text('ad_costs', st.session_state.language),
                                f"kr {total_ad_cost:,.2f}",
                                help=get_text('ad_costs_help', st.session_state.language,
                                              ad_cost_per_order=ad_cost_per_order,
                                              order_count=order_count)
                            )

                        with col3:
                            st.metric(
                                get_text('net_result', st.session_state.language),
                                f"kr {net_profit:,.0f}",  # Changed format to show no decimals
                                help=get_text('net_result_help', st.session_state.language)
                            )

                        # Add explanation
                        st.info(get_text('calculation_method', st.session_state.language))
                    except Exception as e:
                        st.error(f"Error calculating result metrics: {str(e)}")

                with tab4:
                    # Original Export tab content (moved from tab3)
                    st.header(get_text('export_data', st.session_state.language))
                    st.caption(
                        get_text('period_caption', st.session_state.language,
                                 start_date=selected_start_date.strftime('%d.%m.%Y'),
                                 end_date=selected_end_date.strftime('%d.%m.%Y'))
                    )

                    # Create two columns for export options
                    export_col1, export_col2 = st.columns(2)

                    with export_col1:
                        st.subheader(get_text('export_order_data', st.session_state.language))
                        export_format = st.selectbox(
                            get_text('select_export_format', st.session_state.language, data_type='orders'),
                            options=['CSV', 'Excel', 'JSON', 'PDF'],
                            key='orders_export_format')
                        ExportHandler.export_data(df, "orders", export_format)

                    with export_col2:
                        st.subheader(get_text('export_product_data', st.session_state.language))
                        export_format_products = st.selectbox(
                            get_text('select_export_format', st.session_state.language, data_type='products'),
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