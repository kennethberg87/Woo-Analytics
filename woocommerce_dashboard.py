import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from utils.woocommerce_client import WooCommerceClient
from utils.data_processor import DataProcessor

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

def main():
    # Header
    st.title("📊 WooCommerce Daily Turnover Dashboard")

    # Debug mode toggle
    debug_mode = st.sidebar.checkbox("Debug Mode", value=True)
    if debug_mode:
        st.sidebar.info("Debug mode is enabled. You will see detailed API responses and error messages.")

    # Date range selector
    st.sidebar.subheader("Date Range Selection")

    # Calculate default dates - Use 2024 as base year for querying real data
    base_date = datetime(2024, 2, 27).date()  # Use a past date as reference
    default_end = base_date
    default_start = default_end - timedelta(days=7)

    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input(
            "Start Date",
            value=default_start,
            max_value=default_end,
            help="Select start date (defaults to 7 days before end date)"
        )

    with col2:
        end_date = st.date_input(
            "End Date",
            value=default_end,
            min_value=start_date,
            max_value=base_date,
            help="Select end date (up to February 27, 2024)"
        )

    # Validate date range
    if start_date > end_date:
        st.error("Error: End date must be after start date")
        return

    if start_date > base_date or end_date > base_date:
        st.error("Error: Please select dates before February 27, 2024")
        return

    st.info(f"Fetching orders from {start_date} to {end_date}")

    # Fetch and process data
    try:
        with st.spinner("Fetching data from WooCommerce..."):
            orders = st.session_state.woo_client.get_orders(start_date, end_date)

            if debug_mode:
                st.sidebar.write("Raw order count:", len(orders))
                if len(orders) > 0:
                    st.sidebar.write("Sample order data:", orders[0])

            df = st.session_state.woo_client.process_orders_to_df(orders)

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

    # Calculate metrics
    metrics = DataProcessor.calculate_metrics(df)

    # Display metrics in columns
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(
            "Total Revenue",
            f"${metrics['total_revenue']:,.2f}"
        )
    with col2:
        st.metric(
            "Average Daily Revenue",
            f"${metrics['average_daily_revenue']:,.2f}"
        )
    with col3:
        st.metric(
            "Total Shipping",
            f"${metrics['total_shipping']:,.2f}"
        )
    with col4:
        st.metric(
            "Total Tax",
            f"${metrics['total_tax']:,.2f}"
        )

    # Charts
    st.subheader("Revenue Trends")

    # Daily revenue chart
    revenue_chart = DataProcessor.create_daily_revenue_chart(df)
    if revenue_chart:
        st.plotly_chart(revenue_chart, use_container_width=True)

    # Revenue breakdown chart
    st.subheader("Revenue Breakdown")
    breakdown_chart = DataProcessor.create_revenue_breakdown_chart(df)
    if breakdown_chart:
        st.plotly_chart(breakdown_chart, use_container_width=True)

    # Raw data table
    with st.expander("View Raw Data"):
        st.dataframe(
            df.style.format({
                'total': '${:,.2f}',
                'subtotal': '${:,.2f}',
                'shipping_total': '${:,.2f}',
                'tax_total': '${:,.2f}'
            })
        )

if __name__ == "__main__":
    main()