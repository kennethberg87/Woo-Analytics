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
                'shipping_total': 0,
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
                'shipping_total': 0,
                'total_tax': 0,
                'total_profit': 0,
                'profit_margin': 0,
                'total_cogs': 0,
                'order_count': 0
            }

        # Calculate totals
        total_cost = df_products['cost'].sum() if 'cost' in df_products.columns else 0  # Cost of goods excluding VAT
        shipping_base = df['shipping_base'].sum()  # Base shipping excluding VAT
        shipping_tax = df['shipping_tax'].sum()  # Shipping VAT
        total_tax = df['tax_total'].sum()  # Total VAT (including shipping VAT)
        shipping_total = shipping_base + shipping_tax  # Total shipping including VAT

        # Count orders excluding pending status
        order_count = len(df[df['status'] != 'pending'])  # Filter out pending orders

        # Calculate revenues
        total_revenue_incl_vat = df['total'].sum()  # Total revenue including shipping and VAT

        # Calculate revenue excluding VAT by using subtotal which is already excluding VAT
        total_revenue_excl_vat = df['subtotal'].sum()  # Use subtotal which is already excluding VAT

        # Calculate profit using revenue and cost excluding VAT and shipping
        total_profit = total_revenue_excl_vat - total_cost
        profit_margin = (total_profit / total_revenue_excl_vat * 100) if total_revenue_excl_vat > 0 else 0

        # Calculate average revenue based on period
        df['revenue'] = df['total']  # Include total revenue with shipping
        if period == 'weekly':
            df['period'] = df['date'].dt.strftime('%Y-W%U')
            avg_revenue = df.groupby('period')['revenue'].sum().mean()
        elif period == 'monthly':
            df['period'] = df['date'].dt.strftime('%Y-%m')
            avg_revenue = df.groupby('period')['revenue'].sum().mean()
        else:  # daily
            avg_revenue = df.groupby('date')['revenue'].sum().mean()

        metrics = {
            'total_revenue_incl_vat': total_revenue_incl_vat,
            'total_revenue_excl_vat': total_revenue_excl_vat,
            'average_revenue': float(avg_revenue),
            'shipping_total': shipping_total,  # Total shipping costs including VAT
            'shipping_costs': shipping_base,   # Isolated shipping costs excluding VAT
            'total_tax': total_tax,
            'total_profit': total_profit,
            'profit_margin': profit_margin,
            'total_cogs': total_cost,  # Cost of goods excluding VAT
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
        top_products = df_products.groupby(['name', 'product_id', 'sku']).agg({
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
    def get_customer_insights(df):
        """Calculate enhanced customer insights from order data"""
        if df.empty:
            return {
                'repeat_customers': 0,
                'new_customers': 0,
                'customer_retention': 0,
                'avg_order_value': 0,
                'customer_lifetime_value': 0,
                'top_cities': pd.DataFrame(),
                'payment_distribution': {},
                'shipping_distribution': {}
            }
            
        # Extract customer information
        customer_data = []
        city_data = []
        payment_methods = []
        shipping_methods = []
        
        for _, order in df.iterrows():
            if 'billing' in order and isinstance(order['billing'], dict):
                email = order['billing'].get('email', '')
                first_name = order['billing'].get('first_name', '')
                last_name = order['billing'].get('last_name', '')
                city = order['billing'].get('city', '')
                
                customer = {
                    'Name': f"{first_name} {last_name}".strip(),
                    'Email': email,
                    'Order Date': order['date'],
                    'Order Total': float(order['total']),
                    'Order ID': order['order_id']
                }
                customer_data.append(customer)
                
                # Add city data
                if city:
                    city_data.append({
                        'City': city,
                        'Email': email,
                        'Order ID': order['order_id'],
                        'Order Total': float(order['total'])
                    })
                
                # Add payment and shipping method data
                payment_methods.append(order.get('dintero_payment_method', 'Unknown'))
                shipping_methods.append(order.get('shipping_method', 'Unknown'))
        
        if not customer_data:
            return {
                'repeat_customers': 0,
                'new_customers': 0,
                'customer_retention': 0,
                'avg_order_value': 0,
                'customer_lifetime_value': 0,
                'top_cities': pd.DataFrame(),
                'payment_distribution': {},
                'shipping_distribution': {}
            }
            
        # Create DataFrames
        customers_df = pd.DataFrame(customer_data)
        city_df = pd.DataFrame(city_data) if city_data else pd.DataFrame()
        
        # Calculate metrics
        # 1. Unique customers count
        unique_customers = customers_df['Email'].nunique()
        
        # 2. Customer order frequency
        customer_orders = customers_df.groupby('Email').size().reset_index(name='order_count')
        
        # 3. Repeat customers (more than one order)
        repeat_customers = customer_orders[customer_orders['order_count'] > 1].shape[0]
        
        # 4. New customers (just one order)
        new_customers = customer_orders[customer_orders['order_count'] == 1].shape[0]
        
        # 5. Customer retention rate
        customer_retention = (repeat_customers / unique_customers * 100) if unique_customers > 0 else 0
        
        # 6. Average order value
        avg_order_value = customers_df['Order Total'].mean() if len(customers_df) > 0 else 0
        
        # 7. Customer lifetime value
        customer_value = customers_df.groupby('Email')['Order Total'].sum().mean() if unique_customers > 0 else 0
        
        # 8. Top cities by order count
        if not city_df.empty:
            top_cities = city_df.groupby('City').agg({
                'Order ID': 'nunique', 
                'Email': 'nunique'
            }).reset_index()
            top_cities.columns = ['City', 'Order Count', 'Customer Count']
            top_cities = top_cities.sort_values('Order Count', ascending=False).head(5)
        else:
            top_cities = pd.DataFrame()
        
        # 9. Payment method distribution
        payment_dist = {}
        for method in payment_methods:
            if method in payment_dist:
                payment_dist[method] += 1
            else:
                payment_dist[method] = 1
        
        # 10. Shipping method distribution
        shipping_dist = {}
        for method in shipping_methods:
            if method in shipping_dist:
                shipping_dist[method] += 1
            else:
                shipping_dist[method] = 1
        
        # Return all insights
        return {
            'repeat_customers': repeat_customers,
            'new_customers': new_customers,
            'customer_retention': customer_retention,
            'avg_order_value': avg_order_value,
            'customer_lifetime_value': customer_value,
            'top_cities': top_cities,
            'payment_distribution': payment_dist,
            'shipping_distribution': shipping_dist
        }

    @staticmethod
    def create_distribution_chart(distribution_data, title, color_sequence=None):
        """Create a pie chart for distributions (payment methods, shipping methods, etc.)"""
        if not distribution_data:
            return None
            
        # Convert dictionary to DataFrame
        df = pd.DataFrame(list(distribution_data.items()), columns=['Category', 'Count'])
        
        # Calculate percentages
        total = df['Count'].sum()
        df['Percentage'] = df['Count'] / total * 100
        
        # Create pie chart
        fig = px.pie(
            df, 
            values='Count', 
            names='Category', 
            title=title,
            hover_data=['Percentage'],
            labels={'Percentage': 'Percentage (%)', 'Count': 'Number of Orders'},
            color_discrete_sequence=color_sequence
        )
        
        # Update layout
        fig.update_layout(
            height=400,
            margin=dict(l=20, r=20, t=40, b=20),
            legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5)
        )
        
        # Update trace hover template to show percentages
        fig.update_traces(
            textinfo='percent+label',
            hovertemplate='<b>%{label}</b><br>Count: %{value}<br>Percentage: %{customdata[0]:.1f}%'
        )
        
        return fig
    
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