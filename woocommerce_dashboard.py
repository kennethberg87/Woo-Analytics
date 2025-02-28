import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import logging
from utils.woocommerce_client import WooCommerceClient
from utils.data_processor import DataProcessor
from utils.export_handler import ExportHandler
from utils.notification_handler import NotificationHandler

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Initialize theme state if not exists
if 'theme' not in st.session_state:
    st.session_state.theme = "light"

# Theme selection
theme_mapping = {
    "Lys": "light",
    "Mørk": "dark"
}

# Page configuration with theme
st.set_page_config(
    page_title="WooCommerce Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': None,
        'Report a bug': None,
        'About': None
    }
)

# Theme toggle in sidebar
selected_theme = st.sidebar.radio(
    "Tema",
    options=["Lys", "Mørk"],
    index=0 if st.session_state.theme == "light" else 1,
    key="theme_selector"
)

# Update theme state and apply theme
if theme_mapping[selected_theme] != st.session_state.theme:
    logging.debug(f"Theme changed from {st.session_state.theme} to {theme_mapping[selected_theme]}")
    st.session_state.theme = theme_mapping[selected_theme]
    if selected_theme == "Mørk":
        st.markdown("""
            <style>
                /* Main app background */
                .stApp {
                    background-color: #0E1117 !important;
                    color: #FAFAFA !important;
                }

                /* Sidebar */
                .css-1d391kg {
                    background-color: #262730 !important;
                }

                /* Text elements */
                .stMarkdown, .stText, .stTitle, h1, h2, h3, h4, h5, h6, p {
                    color: #FAFAFA !important;
                }

                /* Metric cards */
                [data-testid="stMetricValue"] {
                    color: #FAFAFA !important;
                }

                /* DataTable styles */
                .stDataFrame {
                    background-color: #262730 !important;
                }

                /* Inputs and widgets */
                .stSelectbox, .stDateInput {
                    background-color: #262730 !important;
                    color: #FAFAFA !important;
                }

                /* Charts */
                .js-plotly-plot .plotly {
                    background-color: #262730 !important;
                }

                /* Alerts and messages */
                .stAlert {
                    background-color: #262730 !important;
                    color: #FAFAFA !important;
                }
            </style>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
            <style>
                /* Main app background */
                .stApp {
                    background-color: #FFFFFF !important;
                    color: #262730 !important;
                }

                /* Sidebar */
                .css-1d391kg {
                    background-color: #F0F2F6 !important;
                }

                /* Text elements */
                .stMarkdown, .stText, .stTitle, h1, h2, h3, h4, h5, h6, p {
                    color: #262730 !important;
                }

                /* DataTable styles */
                .stDataFrame {
                    background-color: #FFFFFF !important;
                }

                /* Charts */
                .js-plotly-plot .plotly {
                    background-color: #FFFFFF !important;
                }
            </style>
        """, unsafe_allow_html=True)
    st.rerun()


# Initialize session state
if 'woo_client' not in st.session_state:
    try:
        st.session_state.woo_client = WooCommerceClient()
        st.success("Koblet til WooCommerce API")
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


def render_invoice_section(df, selected_start_date, selected_end_date):
    """Render the invoice section in a separate tab"""
    st.header("Fakturaer")
    st.caption(
        f"For perioden: {selected_start_date.strftime('%d.%m.%Y')} til {selected_end_date.strftime('%d.%m.%Y')}"
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
                                 "Fakturanummer",
                             "Ordrenummer":
                                 "Ordrenummer",
                             "Fakturadato":
                                 st.column_config.DatetimeColumn(
                                     "Fakturadato", format="DD.MM.YYYY HH:mm"),
                             "Status":
                                 "Status",
                             "Total":
                                 "Total",
                         },
                         hide_index=True)

            # Add download section with improved styling
            st.subheader("Last ned fakturaer")
            st.info("""
            💡 Klikk på lenkene under for å laste ned PDF-fakturaer direkte. 
            Fakturaene vil lastes ned automatisk når du klikker på linken.
            """)

            # Create columns for better layout of download links
            cols = st.columns(3)
            for idx, invoice in enumerate(invoice_data):
                col_idx = idx % 3
                if invoice['URL']:
                    cols[col_idx].markdown(
                        f"📄 [{invoice['Fakturanummer']} - {invoice['Ordrenummer']}]({invoice['URL']})"
                    )
        else:
            st.info("Ingen fakturaer funnet for valgt periode")
    else:
        st.warning("Ingen ordredata tilgjengelig for valgt periode")


def main():
    # Header
    st.title("📊 Salgsstatistikk nettbutikk")

    # Debug mode toggle
    debug_mode = st.sidebar.checkbox("Debug Mode", value=True)
    if debug_mode:
        st.sidebar.info(
            "Debug mode is enabled. API responses and error messages are being logged to woocommerce_api.log"
        )

    # Real-time notifications toggle
    notifications_enabled = st.sidebar.checkbox("Aktiver sanntidsvarsler",
                                                value=True)

    # Add sound toggle if notifications are enabled
    if notifications_enabled:
        st.session_state.sound_enabled = st.sidebar.checkbox(
            "🔔 Aktiver lydvarsling",
            value=st.session_state.get('sound_enabled', True),
            help="Spiller av Ca-Ching lyd når en ny ordre er mottatt.")

        # Add a placeholder for notifications
        notification_placeholder = st.empty()

        # Check for new orders every 30 seconds
        if st.session_state.notification_handler.monitor_orders(
                st.session_state.woo_client):
            notification_placeholder.success(
                "✨ Aktivert varsler - Du får beskjed når det kommer inn en ny bestilling!"
            )

    # View period selector (before date range)
    view_period = st.selectbox("Velg visningsperiode",
                               options=['Daglig', 'Ukentlig', 'Månedlig'],
                               index=0,
                               help="Velg hvordan dataene skal aggregeres")

    # Calculate date range based on view period
    start_date, end_date = get_date_range(view_period)

    # Date range selector with calculated defaults
    st.subheader("Valg av ordreperiode")

    # Create two columns for date pickers
    col1, col2 = st.columns(2)

    with col1:
        selected_start_date = st.date_input(
            "Startdato",
            value=start_date,
            help=f"Startdato (standard: {start_date.strftime('%d.%m.%Y')})",
            format="DD.MM.YYYY")

    with col2:
        selected_end_date = st.date_input(
            "Sluttdato",
            value=end_date,
            help=f"Sluttdato (standard: {end_date.strftime('%d.%m.%Y')})",
            format="DD.MM.YYYY")

    # Validate date range
    if selected_start_date > selected_end_date:
        st.error("Error: End date must be after start date")
        return

    st.info(
        f"Basert på ordre fra {selected_start_date.strftime('%d.%m.%Y')} til {selected_end_date.strftime('%d.%m.%Y')}"
    )

    # Fetch and process data
    try:
        with st.spinner("Henter bestillinger fra nettbutikken..."):
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
        st.error(f"Error: {str(e)}")
        if debug_mode:
            logging.error(f"Detailed error: {str(e)}")
        return

    if df.empty:
        st.warning(
            f"Ingen ordre funnet fra perioden {selected_start_date} and {selected_end_date}"
        )
        return

    # Create tabs
    tab1, tab2, tab3 = st.tabs(["📊 Dashboard", "🧾 Fakturaer", "📤 Eksporter"])

    with tab1:
        # Convert view_period to lowercase for processing
        period = view_period.lower()

        # Calculate metrics including profit
        metrics = DataProcessor.calculate_metrics(df, df_products, period)

        # Display metrics in columns
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric(
                "Total omsetning (ink. MVA)",
                f"kr {metrics['total_revenue_incl_vat']:,.2f}",
                help="Total revenue including VAT, excluding shipping costs")
        with col2:
            st.metric("Total omsetning (eks. MVA)",
                      f"kr {metrics['total_revenue_excl_vat']:,.2f}",
                      help="Total revenue excluding VAT and shipping costs")
        with col3:
            st.metric(
                "Total fortjeneste",
                f"kr {metrics['total_profit']:,.2f}",
                help=
                "Profit calculated using revenue (excl. VAT) minus product costs"
            )
        with col4:
            pass

        # Add second row of metrics
        col5, col6, col7, col8 = st.columns(4)
        with col5:
            st.metric("Total MVA",
                      f"kr {metrics['total_tax']:,.2f}",
                      help="Total VAT collected (including shipping VAT)")
        with col6:
            st.metric("Fortjenestemargin",
                      f"{metrics['profit_margin']:.1f}%",
                      help="Profit as percentage of revenue (excl. VAT)")
        with col7:
            st.metric("Kostnad for solgte varer",
                      f"kr {metrics['total_cogs']:,.2f}",
                      help="Total cost of products sold (excl. VAT)")
        with col8:
            st.metric("Antall ordrer",
                      f"{metrics['order_count']}",
                      help="Total number of orders in selected period")

        # Add explanation about calculations
        st.info("""
        💡 Kalkulasjon av omsetning og profit:
        - Total omsetning (ink. MVA): Totalt produktsalg inkludert MVA, eks. frakt
        - Total omsetning (eks. MVA): Total omsetning eks. MVA og frakt.
        - Fraktkostnader vises ekskl. mva
        - Kostnad: Total varekostnad (eks. MVA)
        """)

        # Display Top 10 Products
        st.header("10 mest solgte produkter basert på antall")
        st.caption(
            f"For perioden: {selected_start_date.strftime('%d.%m.%Y')} til {selected_end_date.strftime('%d.%m.%Y')}"
        )

        top_products = DataProcessor.get_top_products(df_products)
        if not top_products.empty:
            st.dataframe(
                top_products,
                column_config={
                    "name":
                        "Produktnavn",
                    "product_id":
                        st.column_config.NumberColumn(
                            "Produkt ID",
                            help="Unik identifikator for produktet",
                            format="%d"  # Format as plain integer without commas
                        ),
                    "Total Quantity":
                        st.column_config.NumberColumn(
                            "Antall solgt",
                            help=
                            "Totalt antall solgt av dette produkter innenfor valg periode"
                        ),
                    "Stock Quantity":
                        st.column_config.NumberColumn(
                            "På lager", help="Nåværende lagerbeholdning")
                },
                hide_index=False,
                use_container_width=True)
        else:
            st.warning("No product data available for the selected date range")

        # Revenue Trends
        st.subheader(f"Omsetning ({view_period})")
        revenue_chart = DataProcessor.create_revenue_chart(df, period)
        if revenue_chart:
            st.plotly_chart(revenue_chart, use_container_width=True)

        # Customer List
        st.header("Ovesikt over kunder")
        st.caption(
            f"For perioden: {selected_start_date.strftime('%d.%m.%Y')} til {selected_end_date.strftime('%d.%m.%Y')}"
        )

        customers_df = DataProcessor.get_customer_list(df)
        if not customers_df.empty:
            st.dataframe(
                customers_df,
                column_config={
                    "Name":
                        "Navn på kunde",
                    "Email":
                        "E-postadresse",
                    "Order Date":
                        st.column_config.DatetimeColumn("Ordre utført",
                                                        format="DD.MM.YYYY HH:mm"),
                    "Payment Method":
                        "Betalingsmetode",
                    "Shipping Method":
                        "Fraktmetode",
                    "Total Orders":
                        st.column_config.NumberColumn("Ordretotal",
                                                      help="Totalsum for ordren",
                                                      format="kr %.2f")
                },
                hide_index=True,
                use_container_width=True)
        else:
            st.warning(
                "No customer data available for the selected date range")

        # Product Distribution
        st.subheader("Product Distribution")
        quantity_chart = DataProcessor.create_product_quantity_chart(
            df_products)
        if quantity_chart:
            st.plotly_chart(quantity_chart, use_container_width=True)

    with tab2:
        # Render invoice section in the second tab
        render_invoice_section(df, selected_start_date, selected_end_date)

    with tab3:
        # Export Section
        st.header("Eksporter data")
        st.caption(
            f"For perioden: {selected_start_date.strftime('%d.%m.%Y')} til {selected_end_date.strftime('%d.%m.%Y')}"
        )

        # Create two columns for export options
        export_col1, export_col2 = st.columns(2)

        with export_col1:
            st.subheader("Eksporter ordredata")
            export_format = st.selectbox(
                "Velg filformat for eksport av ordredata",
                options=['CSV', 'Excel', 'JSON', 'PDF'],
                key='orders_export_format')
            ExportHandler.export_data(df, "orders", export_format)

        with export_col2:
            st.subheader("Eksporter produktdata")
            export_format_products = st.selectbox(
                "Velg filformat for eksport av produktdata",
                options=['CSV', 'Excel', 'JSON', 'PDF'],
                key='products_export_format')
            ExportHandler.export_data(df_products, "products",
                                      export_format_products)

        # Raw data tables (moved from Dashboard tab)
        with st.expander("Vis ordredata"):
            st.header("Rådata tabeller")

            # Order data table
            st.subheader("Ordredata")
            # Create a display copy of the DataFrame without unwanted columns
            display_df = df.drop(columns=[
                'shipping_base', 'subtotal', 'shipping_tax',
                'revenue_no_shipping', 'tax_total', 'order_id', 'meta_data'
            ])

            # Add customer name column
            display_df['customer_name'] = display_df['billing'].apply(
                lambda x: f"{x.get('first_name', '')} {x.get('last_name', '')}".
                strip())

            # Fill empty invoice values with friendly text
            display_df['invoice_number'] = display_df['invoice_number'].fillna("Ikke fakturert")
            display_df['invoice_date'] = display_df['invoice_date'].fillna("Ikke tilgjengelig")

            # Remove the original billing column and reorder
            display_df = display_df.drop(columns=['billing'])

            st.dataframe(display_df.style.format({
                'total': 'kr {:,.2f}',
                'shipping_total': 'kr {:,.2f}'
            }),
                        column_config={
                            "date": st.column_config.DatetimeColumn(
                                "Dato",
                                format="DD.MM.YYYY HH:mm"
                            ),
                            "order_number": "Ordrenummer",
                            "status": "Status",
                            "customer_name": "Kundenavn",
                            "total": "Totalt",
                            "shipping_total": "Frakt (inkl. MVA)",
                            "dintero_payment_method": "Betalingsmetode",
                            "shipping_method": "Leveringsmetode",
                            "invoice_number": "Fakturanummer",
                            "invoice_date": "Fakturadato"
                        },
                        hide_index=True)

            # Product data table
            st.subheader("Produktdata")
            if not df_products.empty:
                # Create a display copy of the DataFrame without subtotal and tax columns
                display_products_df = df_products.drop(columns=['subtotal', 'tax', 'product_id'])  # Remove product_id from display
                st.dataframe(display_products_df.style.format({
                    'total': 'kr {:,.2f}',
                    'cost': 'kr {:,.2f}'
                }),
                            column_config={
                                "date": st.column_config.DatetimeColumn(
                                    "Dato",
                                    format="DD.MM.YYYY HH:mm"
                                ),
                                "sku": "Varenummer",
                                "name": "Produktnavn",
                                "quantity": "Antall",
                                "total": "Totalt",
                                "cost": "Kostnad"
                            },
                            hide_index=True)


if __name__ == "__main__":
    main()