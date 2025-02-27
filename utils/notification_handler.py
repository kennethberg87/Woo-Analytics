import streamlit as st
from datetime import datetime, timedelta
import time

class NotificationHandler:
    def __init__(self):
        # Initialize notification state in session
        if 'notifications' not in st.session_state:
            st.session_state.notifications = set()
        if 'last_check_time' not in st.session_state:
            st.session_state.last_check_time = datetime.now()

    def check_new_orders(self, orders):
        """Check for new orders since last check"""
        new_orders = []
        current_time = datetime.now()

        for order in orders:
            order_id = str(order.get('id'))
            date_created = order.get('date_created')

            # Skip if we've already notified about this order
            if order_id in st.session_state.notifications:
                continue

            # Check if this is a new order
            try:
                order_date = datetime.fromisoformat(date_created.replace('Z', '+00:00'))
                if order_date > st.session_state.last_check_time:
                    new_orders.append(order)
                    st.session_state.notifications.add(order_id)
                    st.sidebar.info(f"Found new order: #{order_id} at {order_date}")
            except Exception as e:
                st.sidebar.error(f"Error processing order date: {e}")

        st.session_state.last_check_time = current_time
        return new_orders

    def display_notification(self, order):
        """Display a desktop notification for a new order"""
        try:
            # Extract order details
            order_id = order.get('id')
            total = float(order.get('total', 0))
            currency = order.get('currency', 'NOK')
            customer_name = f"{order.get('billing', {}).get('first_name', '')} {order.get('billing', {}).get('last_name', '')}"

            # Create notification message with more details
            message = f"""🛍️ New Order Alert! #{order_id}
Customer: {customer_name}
Total: {currency} {total:,.2f}
Time: {datetime.now().strftime('%H:%M:%S')}"""

            # Display notification using Streamlit
            st.toast(message, icon='🛍️')

            # Also show in sidebar for better visibility
            st.sidebar.success(message)

        except Exception as e:
            st.sidebar.error(f"Error displaying notification: {e}")

    def monitor_orders(self, woo_client, check_interval=30):
        """Monitor for new orders and display notifications"""
        try:
            # Get current time
            current_time = datetime.now()

            # Fetch recent orders
            orders = woo_client.get_orders(
                start_date=(current_time - timedelta(minutes=check_interval)).date(),
                end_date=current_time.date()
            )

            # Check for new orders
            new_orders = self.check_new_orders(orders)

            # Display notifications for new orders
            for order in new_orders:
                self.display_notification(order)

            return True  # Return True to indicate monitoring is active

        except Exception as e:
            st.sidebar.error(f"Error monitoring orders: {e}")
            return False