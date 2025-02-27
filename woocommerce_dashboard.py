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
    st.title("📊 WooCommerce Sales Analytics Dashboard")

    # Debug mode toggle
    debug_mode = st.sidebar.checkbox("Debug Mode", value=True)
    if debug_mode:
        st.sidebar.info("Debug mode is enabled. You will see detailed API responses and error messages.")

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

    # Set fixed date range for testing (known working dates)
    default_start = datetime(2024, 2, 20).date()  # Fixed start date
    default_end = datetime(2024, 2, 27).date()    # Fixed end date

    with st.columns(2)[0]:
        start_date = st.date_input(
            "Start Date",
            value=default_start,
            min_value=default_start,
            max_value=default_end,
            help="Select start date (February 20-27, 2024)"
        )

    with st.columns(2)[1]:
        end_date = st.date_input(
            "End Date",
            value=default_end,
            min_value=start_date,
            max_value=default_end,
            help="Select end date (February 20-27, 2024)"
        )

    # Validate date range
    if start_date > end_date:
        st.error("Error: End date must be after start date")
        return

    if start_date < default_start or end_date > default_end:
        st.error("Error: Please select dates between February 20-27, 2024")
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

    # Convert view_period to lowercase for processing
    period = view_period.lower()

    # Calculate metrics
    metrics = DataProcessor.calculate_metrics(df, period)

    # Display metrics in columns
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(
            "Total Revenue",
            f"kr {metrics['total_revenue']:,.2f}"
        )
    with col2:
        st.metric(
            f"Average {view_period} Revenue",
            f"kr {metrics['average_revenue']:,.2f}"
        )
    with col3:
        st.metric(
            "Total Shipping",
            f"kr {metrics['total_shipping']:,.2f}"
        )
    with col4:
        st.metric(
            "Total Tax",
            f"kr {metrics['total_tax']:,.2f}"
        )

    # Charts
    st.subheader(f"Revenue Trends ({view_period})")

    # Revenue chart
    revenue_chart = DataProcessor.create_revenue_chart(df, period)
    if revenue_chart:
        st.plotly_chart(revenue_chart, use_container_width=True)

    # Revenue breakdown chart
    st.subheader(f"Revenue Breakdown ({view_period})")
    breakdown_chart = DataProcessor.create_revenue_breakdown_chart(df, period)
    if breakdown_chart:
        st.plotly_chart(breakdown_chart, use_container_width=True)

    # Raw data table
    with st.expander("View Raw Data"):
        st.dataframe(
            df.style.format({
                'total': 'kr {:,.2f}',
                'subtotal': 'kr {:,.2f}',
                'shipping_total': 'kr {:,.2f}',
                'tax_total': 'kr {:,.2f}'
            })
        )

if __name__ == "__main__":
    main()