import pandas as pd
import numpy as np
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
    def calculate_cac_metrics(df, ad_cost_per_order=30, use_ga_data=False, previous_period_data=None):
        """
        Calculate Customer Acquisition Cost (CAC) vs. Revenue metrics
        
        Args:
            df: Order DataFrame with billing information
            ad_cost_per_order: Advertising cost per order in NOK (used if GA data unavailable)
            use_ga_data: Whether to use Google Analytics data for ad costs
            previous_period_data: Optional data from previous period for comparison
            
        Returns:
            Dictionary of CAC metrics and time-series data
        """
        if df.empty:
            return {
                'cac': 0,
                'cac_to_ltv_ratio': 0,
                'roi': 0,
                'breakeven_point': 0,
                'new_customers_count': 0,
                'repeat_customers_count': 0,
                'total_ad_spend': 0,
                'total_revenue': 0,
                'revenue_per_customer': 0,
                'campaign_data': pd.DataFrame(),
                'cac_trend_data': pd.DataFrame(),
                'roi_trend_data': pd.DataFrame(),
                'using_ga_data': False
            }
            
        # Extract unique customers and calculate counts
        customer_data = []
        
        for _, order in df.iterrows():
            if 'billing' in order and isinstance(order['billing'], dict):
                email = order['billing'].get('email', '')
                customer = {
                    'Email': email,
                    'Order Date': pd.to_datetime(order['date']),
                    'Order Total': float(order['total']),
                    'Order ID': order['order_id']
                }
                customer_data.append(customer)
                
        if not customer_data:
            return {
                'cac': 0,
                'cac_to_ltv_ratio': 0,
                'roi': 0,
                'breakeven_point': 0,
                'new_customers_count': 0,
                'repeat_customers_count': 0,
                'total_ad_spend': 0,
                'total_revenue': 0,
                'revenue_per_customer': 0,
                'campaign_data': pd.DataFrame(),
                'cac_trend_data': pd.DataFrame(),
                'roi_trend_data': pd.DataFrame(),
                'using_ga_data': False
            }
            
        # Create DataFrame from customer data
        customers_df = pd.DataFrame(customer_data)
        
        # Calculate customer order frequency
        customer_orders = customers_df.groupby('Email').size().reset_index(name='order_count')
        
        # Identify new vs. repeat customers
        new_customers = customer_orders[customer_orders['order_count'] == 1]
        repeat_customers = customer_orders[customer_orders['order_count'] > 1]
        
        # Calculate metrics
        new_customers_count = len(new_customers)
        repeat_customers_count = len(repeat_customers)
        total_customers = new_customers_count + repeat_customers_count
        
        # Calculate total revenue
        total_revenue = customers_df['Order Total'].sum()
        
        # Get date range for potential GA data
        try:
            min_date = customers_df['Order Date'].min().date()
            max_date = customers_df['Order Date'].max().date()
        except:
            min_date = None
            max_date = None
        
        # Try to get ad cost data from Google Analytics if requested
        campaign_data = pd.DataFrame()
        using_ga_data = False
        
        if use_ga_data and min_date and max_date:
            try:
                # Import the Google Analytics client
                from utils.google_analytics_client import GoogleAnalyticsClient
                
                # Create client and get ad cost data
                ga_client = GoogleAnalyticsClient()
                ad_spend_data = ga_client.calculate_total_ad_spend(min_date, max_date)
                campaign_data = ga_client.calculate_campaign_performance(min_date, max_date)
                
                # Use GA data if available
                if ad_spend_data['has_data']:
                    total_ad_spend = ad_spend_data['total_spend']
                    using_ga_data = True
                    
                    # Create daily spend data for trend analysis
                    daily_spend = pd.DataFrame([
                        {'Date': date, 'Ad_Spend': spend}
                        for date, spend in ad_spend_data['spend_by_date'].items()
                    ])
                else:
                    # Fall back to the fixed cost approach
                    total_ad_spend = len(customers_df) * ad_cost_per_order
            except Exception as e:
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Error getting Google Analytics data: {str(e)}", exc_info=True)
                
                # Fall back to the fixed cost approach
                total_ad_spend = len(customers_df) * ad_cost_per_order
        else:
            # Use fixed cost per order if not using GA data
            total_ad_spend = len(customers_df) * ad_cost_per_order
        
        # Calculate CAC (Customer Acquisition Cost)
        # We'll only count acquisition cost for new customers
        cac = total_ad_spend / new_customers_count if new_customers_count > 0 else 0
        
        # Calculate average revenue per customer
        revenue_per_customer = total_revenue / total_customers if total_customers > 0 else 0
        
        # Calculate customer lifetime value (LTV) - simplified version
        # Using the average total value of orders per customer
        customer_lifetime_value = customers_df.groupby('Email')['Order Total'].sum().mean() if total_customers > 0 else 0
        
        # Calculate CAC to LTV ratio
        cac_to_ltv_ratio = customer_lifetime_value / cac if cac > 0 else 0
        
        # Calculate ROI
        roi = ((total_revenue - total_ad_spend) / total_ad_spend * 100) if total_ad_spend > 0 else 0
        
        # Calculate breakeven point (number of orders needed to cover CAC)
        avg_order_value = customers_df['Order Total'].mean() if len(customers_df) > 0 else 0
        breakeven_point = cac / avg_order_value if avg_order_value > 0 else 0
        
        # Create time series data for CAC trend analysis
        if len(customers_df) > 0:
            # Sort by date for time series analysis
            customers_df = customers_df.sort_values('Order Date')
            
            # Group by date
            customers_df['Date'] = customers_df['Order Date'].dt.date
            daily_data = customers_df.groupby('Date').agg({
                'Order Total': 'sum',
                'Email': pd.Series.nunique,
                'Order ID': 'count'
            }).reset_index()
            
            daily_data.columns = ['Date', 'Revenue', 'Unique_Customers', 'Order_Count']
            
            # If using GA data and we have daily spend data, merge it
            if using_ga_data and 'daily_spend' in locals() and not daily_spend.empty:
                # Merge GA spend data with daily order data
                daily_data = pd.merge(daily_data, daily_spend, on='Date', how='left')
                # Fill missing spend data with 0
                daily_data['Ad_Spend'].fillna(0, inplace=True)
            else:
                # Calculate ad spend based on order count
                daily_data['Ad_Spend'] = daily_data['Order_Count'] * ad_cost_per_order
            
            # Calculate daily CAC and ROI
            daily_data['Daily_CAC'] = daily_data.apply(
                lambda x: x['Ad_Spend'] / x['Unique_Customers'] if x['Unique_Customers'] > 0 else 0,
                axis=1
            )
            daily_data['Daily_ROI'] = daily_data.apply(
                lambda x: (x['Revenue'] - x['Ad_Spend']) / x['Ad_Spend'] * 100 if x['Ad_Spend'] > 0 else 0,
                axis=1
            )
            
            # Handle division by zero
            daily_data['Daily_CAC'] = daily_data['Daily_CAC'].replace([np.inf, -np.inf], 0)
            daily_data['Daily_ROI'] = daily_data['Daily_ROI'].replace([np.inf, -np.inf], 0)
            
            # Fill NaN values
            daily_data = daily_data.fillna(0)
            
            # Calculate rolling averages for smoother trend lines
            daily_data['CAC_7day_avg'] = daily_data['Daily_CAC'].rolling(window=7, min_periods=1).mean()
            daily_data['ROI_7day_avg'] = daily_data['Daily_ROI'].rolling(window=7, min_periods=1).mean()
            
            cac_trend_data = daily_data[['Date', 'Daily_CAC', 'CAC_7day_avg']]
            roi_trend_data = daily_data[['Date', 'Daily_ROI', 'ROI_7day_avg']]
        else:
            cac_trend_data = pd.DataFrame()
            roi_trend_data = pd.DataFrame()
        
        # Return computed metrics
        return {
            'cac': cac,
            'cac_to_ltv_ratio': cac_to_ltv_ratio,
            'roi': roi,
            'breakeven_point': breakeven_point,
            'new_customers_count': new_customers_count,
            'repeat_customers_count': repeat_customers_count,
            'total_ad_spend': total_ad_spend,
            'total_revenue': total_revenue,
            'revenue_per_customer': revenue_per_customer,
            'campaign_data': campaign_data,
            'cac_trend_data': cac_trend_data,
            'roi_trend_data': roi_trend_data,
            'using_ga_data': using_ga_data
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
    def create_cac_trend_chart(cac_data):
        """Create a trend chart for Customer Acquisition Cost"""
        if cac_data.empty:
            return None
            
        fig = go.Figure()
        
        # Add daily CAC
        fig.add_trace(go.Scatter(
            x=cac_data['Date'],
            y=cac_data['Daily_CAC'],
            name='Daily CAC',
            mode='markers',
            marker=dict(color='rgba(135, 206, 250, 0.5)', size=8),
            hovertemplate='Date: %{x}<br>CAC: kr %{y:.2f}'
        ))
        
        # Add 7-day rolling average
        fig.add_trace(go.Scatter(
            x=cac_data['Date'],
            y=cac_data['CAC_7day_avg'],
            name='7-day rolling avg',
            mode='lines',
            line=dict(color='#0072B2', width=3),
            hovertemplate='Date: %{x}<br>7-day avg CAC: kr %{y:.2f}'
        ))
        
        # Update layout
        fig.update_layout(
            title='Customer Acquisition Cost (CAC) Trend',
            xaxis_title='Date',
            yaxis_title='Cost (NOK)',
            yaxis_tickprefix='kr ',
            yaxis_tickformat=',.2f',
            height=400,
            margin=dict(l=20, r=20, t=50, b=20),
            hovermode='closest',
            template='plotly_white',
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5)
        )
        
        return fig
        
    @staticmethod
    def create_roi_trend_chart(roi_data):
        """Create a trend chart for Return on Investment (ROI)"""
        if roi_data.empty:
            return None
            
        fig = go.Figure()
        
        # Add daily ROI
        fig.add_trace(go.Scatter(
            x=roi_data['Date'],
            y=roi_data['Daily_ROI'],
            name='Daily ROI',
            mode='markers',
            marker=dict(color='rgba(255, 128, 0, 0.5)', size=8),
            hovertemplate='Date: %{x}<br>ROI: %{y:.1f}%'
        ))
        
        # Add 7-day rolling average
        fig.add_trace(go.Scatter(
            x=roi_data['Date'],
            y=roi_data['ROI_7day_avg'],
            name='7-day rolling avg',
            mode='lines',
            line=dict(color='#D55E00', width=3),
            hovertemplate='Date: %{x}<br>7-day avg ROI: %{y:.1f}%'
        ))
        
        # Add breakeven line at 0%
        fig.add_shape(
            type="line",
            x0=roi_data['Date'].min(),
            y0=0,
            x1=roi_data['Date'].max(),
            y1=0,
            line=dict(
                color="green",
                width=2,
                dash="dash",
            )
        )
        
        # Update layout
        fig.update_layout(
            title='Marketing ROI Trend',
            xaxis_title='Date',
            yaxis_title='ROI (%)',
            yaxis_ticksuffix='%',
            height=400,
            margin=dict(l=20, r=20, t=50, b=20),
            hovermode='closest',
            template='plotly_white',
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5)
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