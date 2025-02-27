import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

class DataProcessor:
    @staticmethod
    def calculate_metrics(df, df_products, period='daily'):
        """
        Calculate key metrics including profit calculations
        """
        if df.empty:
            return {
                'total_revenue': 0,
                'average_revenue': 0,
                'total_shipping': 0,
                'total_tax': 0,
                'total_profit': 0,
                'profit_margin': 0
            }

        # Ensure date column is datetime
        df['date'] = pd.to_datetime(df['date'])

        # Calculate total costs from products DataFrame
        total_cost = df_products['cost'].sum() if 'cost' in df_products.columns else 0
        total_revenue = df['total'].sum()

        # Calculate profit
        total_profit = total_revenue - total_cost
        profit_margin = (total_profit / total_revenue * 100) if total_revenue > 0 else 0

        # Group by selected time period
        if period == 'weekly':
            df['period'] = df['date'].dt.strftime('%Y-W%U')
            grouped = df.groupby('period')
        elif period == 'monthly':
            df['period'] = df['date'].dt.strftime('%Y-%m')
            grouped = df.groupby('period')
        else:  # daily
            grouped = df.groupby('date')

        metrics = {
            'total_revenue': total_revenue,
            'average_revenue': grouped['total'].mean(),
            'total_shipping': df['shipping_total'].sum(),
            'total_tax': df['tax_total'].sum(),
            'total_profit': total_profit,
            'profit_margin': profit_margin
        }

        return metrics

    @staticmethod
    def create_profit_analysis_chart(df_products):
        """
        Create a horizontal bar chart showing profit by product
        """
        if df_products.empty or 'cost' not in df_products.columns:
            return None

        # Calculate profit per product
        product_analysis = df_products.groupby('name').agg({
            'quantity': 'sum',
            'total': 'sum',
            'cost': 'sum'
        }).reset_index()

        product_analysis['profit'] = product_analysis['total'] - product_analysis['cost']
        product_analysis['margin'] = (product_analysis['profit'] / product_analysis['total'] * 100).round(2)

        # Sort by profit
        product_analysis = product_analysis.sort_values('profit', ascending=True)

        fig = go.Figure()

        # Add bars for revenue and cost
        fig.add_trace(go.Bar(
            name='Revenue',
            x=product_analysis['total'],
            y=product_analysis['name'],
            orientation='h',
            marker_color='#2E86C1'
        ))

        fig.add_trace(go.Bar(
            name='Cost',
            x=product_analysis['cost'],
            y=product_analysis['name'],
            orientation='h',
            marker_color='#E74C3C'
        ))

        # Add text annotations for profit margin
        for i, row in product_analysis.iterrows():
            fig.add_annotation(
                x=row['total'],
                y=row['name'],
                text=f"Margin: {row['margin']:.1f}%",
                showarrow=False,
                xanchor='left',
                xshift=10,
                font=dict(size=10)
            )

        fig.update_layout(
            title='Product Profit Analysis',
            barmode='overlay',
            height=max(400, len(product_analysis) * 30),
            template='plotly_white',
            yaxis_title='Product',
            xaxis_title='Amount (NOK)',
            xaxis_tickprefix='kr ',
            xaxis_tickformat=',.2f',
            legend=dict(
                orientation='h',
                yanchor='bottom',
                y=1.02,
                xanchor='right',
                x=1
            )
        )

        return fig

    @staticmethod
    def create_revenue_chart(df, period='daily'):
        """
        Create a line chart for revenue with different time periods
        """
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
        """
        Create a stacked bar chart showing revenue breakdown with different time periods
        """
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
    def create_product_sales_chart(df_products, period='daily'):
        """
        Create a bar chart showing sales by product
        """
        if df_products.empty:
            return None

        # Group by product and calculate total sales
        product_sales = df_products.groupby('name').agg({
            'quantity': 'sum',
            'total': 'sum'
        }).reset_index()

        # Sort by total sales
        product_sales = product_sales.sort_values('total', ascending=True)

        fig = go.Figure()

        # Add bar for total revenue
        fig.add_trace(go.Bar(
            x=product_sales['total'],
            y=product_sales['name'],
            orientation='h',
            marker_color='#2E86C1',
            name='Revenue'
        ))

        fig.update_layout(
            title='Product Sales Breakdown',
            height=max(400, len(product_sales) * 30),  # Dynamic height based on number of products
            template='plotly_white',
            yaxis_title='Product',
            xaxis_title='Revenue (NOK)',
            xaxis_tickprefix='kr ',
            xaxis_tickformat=',.2f',
            showlegend=False
        )

        return fig

    @staticmethod
    def create_product_quantity_chart(df_products):
        """
        Create a pie chart showing quantity sold by product
        """
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