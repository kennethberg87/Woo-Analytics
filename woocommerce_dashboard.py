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
    except Exception as e:
        st.error(f"Failed to connect to WooCommerce: {str(e)}")
        st.info("""
        Please ensure you have set up the following environment variables:
        - WOOCOMMERCE_URL: Your store URL
        - WOOCOMMERCE_KEY: Your API consumer key
        - WOOCOMMERCE_SECRET: Your API consumer secret
        """)
        st.stop()

def main():
    # Header
    st.title("📊 WooCommerce Daily Turnover Dashboard")

    # Date range selector
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input(
            "Start Date",
            datetime.now().date() - timedelta(days=30),
            max_value=datetime.now().date()
        )
    with col2:
        end_date = st.date_input(
            "End Date",
            datetime.now().date(),
            max_value=datetime.now().date()
        )

    # Validate date range
    if start_date > end_date:
        st.error("Error: End date must be after start date")
        return

    # Fetch and process data
    try:
        with st.spinner("Fetching data from WooCommerce..."):
            orders = st.session_state.woo_client.get_orders(start_date, end_date)
            df = st.session_state.woo_client.process_orders_to_df(orders)
    except Exception as e:
        st.error(f"Error: {str(e)}")
        return

    if df.empty:
        st.warning("No orders found for the selected date range")
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