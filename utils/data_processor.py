import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

class DataProcessor:

    @staticmethod
    def calculate_metrics(df, df_products, period='daily'):
        """Calculate key metrics including profit calculations, adjusting for VAT"""
        if df.empty:
            return {
                'total_revenue_incl_vat': 0,
                'total_revenue_excl_vat': 0,
                'average_revenue': 0,
                'shipping_base': 0,
                'total_tax': 0,
                'total_profit': 0,
                'profit_margin': 0,
                'total_cogs': 0,
                'order_count': 0
            }

        # Ensure date column is datetime
        if 'date' in df.columns:  # Check if 'date' column exists
            df['date'] = pd.to_datetime(df['date'])
        else:
            st.error("Date column not found in DataFrame")
            return {
                'total_revenue_incl_vat': 0,
                'total_revenue_excl_vat': 0,
                'average_revenue': 0,
                'shipping_base': 0,
                'total_tax': 0,
                'total_profit': 0,
                'profit_margin': 0,
                'total_cogs': 0,
                'order_count': 0
            }

        # Calculate totals
        total_cost = df_products['cost'].sum() if 'cost' in df_products.columns else 0  # Cost is now excluding VAT
        shipping_base = df['shipping_base'].sum()  # Base shipping excluding VAT
        shipping_tax = df['shipping_tax'].sum()  # Shipping VAT
        total_tax = df['tax_total'].sum()  # Total VAT (including shipping VAT)

        # Count orders excluding pending status
        order_count = len(df[df['status'] != 'pending'])  # Filter out pending orders

        # Calculate revenues (excluding shipping)
        total_revenue_incl_vat = df['total'].sum() - df['shipping_total'].sum()  # Total revenue excluding shipping
        total_revenue_excl_vat = total_revenue_incl_vat - (total_tax - shipping_tax)  # Revenue excluding VAT and shipping

        # Calculate profit using revenue and cost excluding VAT
        total_profit = total_revenue_excl_vat - total_cost
        profit_margin = (total_profit / total_revenue_excl_vat * 100) if total_revenue_excl_vat > 0 else 0

        # Calculate average revenue based on period
        df['revenue_no_shipping'] = df['total'] - df['shipping_total']
        if period == 'weekly':
            df['period'] = df['date'].dt.strftime('%Y-W%U')
            avg_revenue = df.groupby('period')['revenue_no_shipping'].sum().mean()
        elif period == 'monthly':
            df['period'] = df['date'].dt.strftime('%Y-%m')
            avg_revenue = df.groupby('period')['revenue_no_shipping'].sum().mean()
        else:  # daily
            avg_revenue = df.groupby('date')['revenue_no_shipping'].sum().mean()

        metrics = {
            'total_revenue_incl_vat': total_revenue_incl_vat,
            'total_revenue_excl_vat': total_revenue_excl_vat,
            'average_revenue': float(avg_revenue),
            'shipping_base': shipping_base,
            'total_tax': total_tax,
            'total_profit': total_profit,
            'profit_margin': profit_margin,
            'total_cogs': total_cost,  # Now represents cost excluding VAT
            'order_count': order_count
        }

        return metrics

    @staticmethod
    def get_top_products(df_products, limit=10):
        """Get top products by quantity sold within the selected date range"""
        if df_products.empty:
            return pd.DataFrame()

        # Ensure date is in datetime format
        if 'date' in df_products.columns:
            df_products['date'] = pd.to_datetime(df_products['date'])

        # Group by product and aggregate data
        top_products = df_products.groupby(['name', 'product_id']).agg({
            'quantity': 'sum',
            'stock_quantity': 'last'  # Take the most recent stock quantity
        }).reset_index()

        # Sort by quantity sold and get top products
        top_products = top_products.sort_values('quantity', ascending=False).head(limit)
        top_products = top_products.reset_index(drop=True)
        top_products.index = top_products.index + 1  # Start index from 1

        # Rename columns for display
        top_products.rename(columns={
            'quantity': 'Total Quantity',
            'stock_quantity': 'Stock Quantity'
        }, inplace=True)

        return top_products

    @staticmethod
    def get_customer_list(df):
        """Get list of customers with their order totals"""
        if df.empty:
            return pd.DataFrame()

        # Create customer list with order totals
        customer_data = []
        for _, order in df.iterrows():
            if 'billing' in order and isinstance(order['billing'], dict):
                first_name = order['billing'].get('first_name', '')
                last_name = order['billing'].get('last_name', '')
                customer = {
                    'Name': f"{first_name} {last_name}".strip(),
                    'Email': order['billing'].get('email', ''),
                    'Order Date': order['date'],
                    'Total Orders': order['total'],
                    'Payment Method': order.get('dintero_payment_method', ''),
                    'Shipping Method': order.get('shipping_method', '')
                }
                customer_data.append(customer)

        if not customer_data:
            return pd.DataFrame()

        # Create DataFrame from customer data
        customers_df = pd.DataFrame(customer_data)

        # Group by customer details and sum their orders
        customers_df = customers_df.groupby(['Name', 'Email', 'Payment Method', 'Shipping Method', 'Order Date'])['Total Orders'].sum().reset_index()

        # Sort by date descending (most recent first)
        customers_df = customers_df.sort_values('Order Date', ascending=False)

        return customers_df

    @staticmethod
    def create_revenue_chart(df, period='daily'):
        """Create a line chart for revenue with different time periods"""
        if df.empty:
            return None

        # Ensure date column is datetime
        df['date'] = pd.to_datetime(df['date'])

        # Group by selected time period
        if period == 'weekly':
            df['period'] = df['date'].dt.strftime('%Y-W%U')
            grouped = df.groupby('period').agg({'total': 'sum'}).reset_index()
            x_title = 'Week'
        elif period == 'monthly':
            df['period'] = df['date'].dt.strftime('%Y-%m')
            grouped = df.groupby('period').agg({'total': 'sum'}).reset_index()
            x_title = 'Month'
        else:  # daily
            grouped = df.copy()
            grouped['period'] = grouped['date']
            x_title = 'Date'

        fig = px.line(grouped,
                     x='period',
                     y='total',
                     title=f'{period.capitalize()} omsetning',
                     labels={
                         'total': 'Omsetning (NOK)',
                         'period': x_title
                     },
                     template='plotly_white')

        fig.update_layout(height=400,
                         hovermode='x unified',
                         showlegend=False,
                         yaxis_tickprefix='kr ',
                         yaxis_tickformat=',.2f')

        return fig