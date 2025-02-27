import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

class DataProcessor:
    @staticmethod
    def calculate_metrics(df):
        """
        Calculate key metrics from the DataFrame
        """
        if df.empty:
            return {
                'total_revenue': 0,
                'average_daily_revenue': 0,
                'total_orders': 0,
                'total_shipping': 0,
                'total_tax': 0
            }

        metrics = {
            'total_revenue': df['total'].sum(),
            'average_daily_revenue': df['total'].mean(),
            'total_shipping': df['shipping_total'].sum(),
            'total_tax': df['tax_total'].sum()
        }
        
        return metrics

    @staticmethod
    def create_daily_revenue_chart(df):
        """
        Create a line chart for daily revenue
        """
        if df.empty:
            return None

        fig = px.line(
            df,
            x='date',
            y='total',
            title='Daily Revenue',
            labels={'total': 'Revenue', 'date': 'Date'},
            template='plotly_white'
        )
        
        fig.update_layout(
            height=400,
            hovermode='x unified',
            showlegend=False
        )
        
        return fig

    @staticmethod
    def create_revenue_breakdown_chart(df):
        """
        Create a stacked bar chart showing revenue breakdown
        """
        if df.empty:
            return None

        fig = go.Figure()
        
        # Add traces for different components
        fig.add_trace(go.Bar(
            name='Subtotal',
            x=df['date'],
            y=df['subtotal'],
            marker_color='#2E86C1'
        ))
        
        fig.add_trace(go.Bar(
            name='Shipping',
            x=df['date'],
            y=df['shipping_total'],
            marker_color='#28B463'
        ))
        
        fig.add_trace(go.Bar(
            name='Tax',
            x=df['date'],
            y=df['tax_total'],
            marker_color='#CB4335'
        ))

        fig.update_layout(
            barmode='stack',
            title='Daily Revenue Breakdown',
            height=400,
            template='plotly_white',
            hovermode='x unified'
        )

        return fig
