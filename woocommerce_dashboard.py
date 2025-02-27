import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from utils.woocommerce_client import WooCommerceClient
from utils.data_processor import DataProcessor
from utils.export_handler import ExportHandler
from utils.notification_handler import NotificationHandler

# Page configuration
st.set_page_config(
    page_title="WooCommerce Dashboard",
    page_icon="📊",
    layout="wide"
)

# Initialize session state
if 'woo_client' not in st.session_state:
    try:
        st.session_state.woo_client = WooCommerceClient()
        st.success("Successfully connected to WooCommerce API")
    except Exception as e:
        st.error(f"Failed to connect to WooCommerce: {str(e)}")
        st.info("""
        Please ensure you have set up the following environment variables:
        - WOOCOMMERCE_URL: Your store URL (e.g., https://your-store.com)
        - WOOCOMMERCE_KEY: Your API consumer key
        - WOOCOMMERCE_SECRET: Your API consumer secret
        """)
        st.stop()

# Initialize notification handler
if 'notification_handler' not in st.session_state:
    st.session_state.notification_handler = NotificationHandler()

def main():
    # Header
    st.title("📊 WooCommerce Sales Analytics Dashboard")

    # Debug mode toggle
    debug_mode = st.sidebar.checkbox("Debug Mode", value=True)
    if debug_mode:
        st.sidebar.info("Debug mode is enabled. You will see detailed API responses and error messages.")

    # Real-time notifications toggle
    notifications_enabled = st.sidebar.checkbox("Enable Real-time Notifications", value=True)

    if notifications_enabled:
        # Add a placeholder for notifications
        notification_placeholder = st.empty()

        # Check for new orders every 30 seconds
        if st.session_state.notification_handler.monitor_orders(st.session_state.woo_client):
            notification_placeholder.success("✨ Notifications are active - you'll be alerted of new orders!")

    # View period selector
    st.sidebar.subheader("View Settings")
    view_period = st.sidebar.selectbox(
        "Select View Period",
        options=['Daily', 'Weekly', 'Monthly'],
        index=0,
        help="Choose how to aggregate the data"
    )

    # Date range selector
    st.sidebar.subheader("Date Range Selection")

    # Get today's date
    today = datetime.now().date()

    with st.columns(2)[0]:
        start_date = st.date_input(
            "Start Date",
            value=today,
            help="Select start date (defaults to today)"
        )

    with st.columns(2)[1]:
        end_date = st.date_input(
            "End Date",
            value=today,
            help="Select end date (defaults to today)"
        )

    # Validate date range
    if start_date > end_date:
        st.error("Error: End date must be after start date")
        return

    st.info(f"Fetching orders from {start_date} to {end_date}")

    # Fetch and process data
    try:
        with st.spinner("Fetching data from WooCommerce..."):
            orders = st.session_state.woo_client.get_orders(start_date, end_date)

            if debug_mode:
                st.sidebar.write("Raw order count:", len(orders))
                if len(orders) > 0:
                    st.sidebar.write("Sample order data:", {k: v for k, v in orders[0].items() if k in ['id', 'status', 'date_created', 'total']})

            df, df_products = st.session_state.woo_client.process_orders_to_df(orders)

            if debug_mode and not df.empty:
                st.sidebar.write("Processed data shape:", df.shape)

    except Exception as e:
        st.error(f"Error: {str(e)}")
        if debug_mode:
            st.sidebar.error(f"Detailed error: {str(e)}")
        return

    if df.empty:
        st.warning(f"No orders found between {start_date} and {end_date}")
        return

    # Convert view_period to lowercase for processing
    period = view_period.lower()

    # Calculate metrics including profit
    metrics = DataProcessor.calculate_metrics(df, df_products, period)

    # Display metrics in columns
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(
            "Total Revenue (incl. VAT)",
            f"kr {metrics['total_revenue_incl_vat']:,.2f}",
            help="Total revenue including VAT, excluding shipping costs"
        )
    with col2:
        st.metric(
            "Total Revenue (excl. VAT)",
            f"kr {metrics['total_revenue_excl_vat']:,.2f}",
            help="Total revenue excluding VAT and shipping costs"
        )
    with col3:
        st.metric(
            "Total Profit",
            f"kr {metrics['total_profit']:,.2f}",
            help="Profit calculated using revenue (excl. VAT) minus product costs"
        )
    with col4:
        st.metric(
            "Total Shipping (excl. VAT)",
            f"kr {metrics['shipping_base']:,.2f}",
            help="Total shipping costs excluding VAT"
        )

    # Add second row of metrics
    col5, col6, col7, col8 = st.columns(4)
    with col5:
        st.metric(
            "Total Tax",
            f"kr {metrics['total_tax']:,.2f}",
            help="Total VAT collected (including shipping VAT)"
        )
    with col6:
        st.metric(
            "Profit Margin",
            f"{metrics['profit_margin']:.1f}%",
            help="Profit as percentage of revenue (excl. VAT)"
        )
    with col7:
        st.metric(
            "Cost of Goods Sold",
            f"kr {metrics['total_cogs']:,.2f}",
            help="Total cost of products sold (excl. VAT)"
        )


    # Add explanation about calculations
    st.info("""
    💡 Revenue and Profit Calculation Details:
    - Revenue (incl. VAT): Total product sales including VAT, excluding shipping
    - Revenue (excl. VAT): Product revenue after removing VAT
    - Shipping costs are shown excluding VAT
    - COGS: Total cost of products sold (excl. VAT)
    - Profit: Revenue (excl. VAT) - COGS
    - Product costs are already VAT-exclusive
    """)

    # Add Profit Analysis Section
    st.header("Profit Analysis")
    profit_chart = DataProcessor.create_profit_analysis_chart(df_products)
    if profit_chart:
        st.plotly_chart(profit_chart, use_container_width=True)
    else:
        st.warning("No profit data available. Please check if product costs are properly configured in WooCommerce.")

    # Revenue Trends
    st.subheader(f"Revenue Trends ({view_period})")
    revenue_chart = DataProcessor.create_revenue_chart(df, period)
    if revenue_chart:
        st.plotly_chart(revenue_chart, use_container_width=True)

    # Revenue Breakdown
    st.subheader(f"Revenue Breakdown ({view_period})")
    breakdown_chart = DataProcessor.create_revenue_breakdown_chart(df, period)
    if breakdown_chart:
        st.plotly_chart(breakdown_chart, use_container_width=True)

    # Product Analysis Section
    st.header("Product Analysis")

    # Product Sales Breakdown
    product_sales_chart = DataProcessor.create_product_sales_chart(df_products)
    if product_sales_chart:
        st.plotly_chart(product_sales_chart, use_container_width=True)

    # Product Quantity Distribution
    product_quantity_chart = DataProcessor.create_product_quantity_chart(df_products)
    if product_quantity_chart:
        st.plotly_chart(product_quantity_chart, use_container_width=True)

    # Export Section
    st.header("Export Data")

    # Create two columns for export options
    export_col1, export_col2 = st.columns(2)

    with export_col1:
        st.subheader("Export Orders Data")
        export_format = st.selectbox(
            "Select Export Format for Orders",
            options=['CSV', 'Excel', 'JSON'],
            key='orders_export_format'
        )
        ExportHandler.export_data(df, "orders", export_format)

    with export_col2:
        st.subheader("Export Products Data")
        export_format_products = st.selectbox(
            "Select Export Format for Products",
            options=['CSV', 'Excel', 'JSON'],
            key='products_export_format'
        )
        ExportHandler.export_data(df_products, "products", export_format_products)

    # Raw data tables
    with st.expander("View Raw Data"):
        st.subheader("Order Data")
        st.dataframe(
            df.style.format({
                'total': 'kr {:,.2f}',
                'subtotal': 'kr {:,.2f}',
                'shipping_total': 'kr {:,.2f}',
                'tax_total': 'kr {:,.2f}'
            })
        )

        st.subheader("Product Data")
        if not df_products.empty:
            st.dataframe(
                df_products.style.format({
                    'total': 'kr {:,.2f}',
                    'subtotal': 'kr {:,.2f}',
                    'tax': 'kr {:,.2f}'
                })
            )

if __name__ == "__main__":
    main()