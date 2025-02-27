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
        df['date'] = pd.to_datetime(df['date'])

        # Calculate totals
        total_cost = df_products['cost'].sum() if 'cost' in df_products.columns else 0
        shipping_base = df['shipping_base'].sum()  # Base shipping excluding VAT
        shipping_tax = df['shipping_tax'].sum()  # Shipping VAT
        total_tax = df['tax_total'].sum()  # Total VAT (including shipping VAT)

        # Count orders excluding pending status
        order_count = len(df[df['status'] != 'pending'])  # Filter out pending orders

        # Calculate revenues (excluding shipping)
        total_revenue_incl_vat = df['total'].sum() - df['shipping_total'].sum()  # Total revenue excluding shipping
        total_revenue_excl_vat = total_revenue_incl_vat - (total_tax - shipping_tax)  # Revenue excluding VAT and shipping

        # Calculate profit (using revenue excluding VAT)
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
            'total_cogs': total_cost,
            'order_count': order_count
        }

        return metrics

    @staticmethod
    def get_top_products(df_products, limit=10):
        """Get top products by quantity sold within the selected date range"""
        if df_products.empty:
            return pd.DataFrame()

        # Ensure date is in datetime format
        df_products['date'] = pd.to_datetime(df_products['date'])

        # Group by product name and sum quantities
        top_products = df_products.groupby('name')['quantity'].sum().reset_index()
        top_products = top_products.sort_values('quantity', ascending=False).head(limit)
        top_products = top_products.reset_index(drop=True)
        top_products.index = top_products.index + 1  # Start index from 1

        # Add total quantity column
        top_products.rename(columns={'quantity': 'Total Quantity'}, inplace=True)

        # Debug information
        st.sidebar.write("\nTop Products Analysis:")
        st.sidebar.write(f"Date range: {df_products['date'].min()} to {df_products['date'].max()}")
        st.sidebar.write(f"Number of products found: {len(top_products)}")

        return top_products

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
            grouped = df.groupby('period').agg({
                'total': 'sum'
            }).reset_index()
            x_title = 'Week'
        elif period == 'monthly':
            df['period'] = df['date'].dt.strftime('%Y-%m')
            grouped = df.groupby('period').agg({
                'total': 'sum'
            }).reset_index()
            x_title = 'Month'
        else:  # daily
            grouped = df.copy()
            grouped['period'] = grouped['date']
            x_title = 'Date'

        fig = px.line(
            grouped,
            x='period',
            y='total',
            title=f'{period.capitalize()} Revenue',
            labels={'total': 'Revenue (NOK)', 'period': x_title},
            template='plotly_white'
        )

        fig.update_layout(
            height=400,
            hovermode='x unified',
            showlegend=False,
            yaxis_tickprefix='kr ',
            yaxis_tickformat=',.2f'
        )

        return fig

    @staticmethod
    def create_revenue_breakdown_chart(df, period='daily'):
        """Create a stacked bar chart showing revenue breakdown with different time periods"""
        if df.empty:
            return None

        # Ensure date column is datetime
        df['date'] = pd.to_datetime(df['date'])

        # Group by selected time period
        if period == 'weekly':
            df['period'] = df['date'].dt.strftime('%Y-W%U')
            x_title = 'Week'
        elif period == 'monthly':
            df['period'] = df['date'].dt.strftime('%Y-%m')
            x_title = 'Month'
        else:  # daily
            df['period'] = df['date']
            x_title = 'Date'

        grouped = df.groupby('period').agg({
            'subtotal': 'sum',
            'shipping_total': 'sum',
            'tax_total': 'sum'
        }).reset_index()

        fig = go.Figure()

        # Add traces for different components
        fig.add_trace(go.Bar(
            name='Subtotal',
            x=grouped['period'],
            y=grouped['subtotal'],
            marker_color='#2E86C1'
        ))

        fig.add_trace(go.Bar(
            name='Shipping',
            x=grouped['period'],
            y=grouped['shipping_total'],
            marker_color='#28B463'
        ))

        fig.add_trace(go.Bar(
            name='Tax',
            x=grouped['period'],
            y=grouped['tax_total'],
            marker_color='#CB4335'
        ))

        fig.update_layout(
            barmode='stack',
            title=f'{period.capitalize()} Revenue Breakdown',
            height=400,
            template='plotly_white',
            hovermode='x unified',
            xaxis_title=x_title,
            yaxis_title='Amount (NOK)',
            yaxis_tickprefix='kr ',
            yaxis_tickformat=',.2f'
        )

        return fig

    @staticmethod
    def create_product_quantity_chart(df_products):
        """Create a pie chart showing quantity sold by product"""
        if df_products.empty:
            return None

        # Group by product and calculate total quantity
        product_quantities = df_products.groupby('name')['quantity'].sum().reset_index()

        fig = px.pie(
            product_quantities,
            values='quantity',
            names='name',
            title='Product Sales Distribution (by Quantity)'
        )

        fig.update_layout(
            height=400,
            template='plotly_white'
        )

        return fig