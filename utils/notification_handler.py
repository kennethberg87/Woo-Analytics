import streamlit as st
from datetime import datetime, timedelta
import time
import base64

class NotificationHandler:
    def __init__(self):
        # Initialize notification state in session
        if 'notifications' not in st.session_state:
            st.session_state.notifications = set()
        if 'last_check_time' not in st.session_state:
            st.session_state.last_check_time = datetime.now()
        if 'sound_enabled' not in st.session_state:
            st.session_state.sound_enabled = True

        # Ca-ching sound effect (base64 encoded WAV)
        self.sound_data = base64.b64decode("""
        UklGRvQFAABXQVZFZm10IBAAAAABAAEAgD4AAAB9AAACABAAZGF0YdAFAACBhYqFbF5NODAyPVBh
        eJO2ydLOyMrS1Mnj7vP89fv8/Pz9/v79/Pz7+vj39PPx7u3q6efl4+Lh4ODg4uXp6+/z9/r8/v7+
        /v79/Pv6+ff18/Dt6+nm5OLh4ODh4+Xn6+3x9Pf6/P3+/v79/Pv5+Pb08e/s6ufl4+Lh4OHi5Ofp
        7O/z9vn7/f7+/v38+/n39PLv7Orn5OPi4eHi4+Xo6u3x8/b5+/39/v79/Pr49vTy7+zp5+Ti4eDh
        4uTm6evt8PP19/n7/P39/fz7+ff18/Dua1tLLyIjLz9Na36UsMfTzMvP1dLK5O/z/Pb8/f39/v7+
        /fz7+vn39fPx7uzp5+Xj4uHg4OHj5unr7/P2+fv9/v7+/v38+/n39PPw7evp5uTi4eHh4uTm6Ovt
        8PP1+Pr8/f7+/v38+vj29PHu6+nm5OLh4OHi4+Xn6uzv8vX3+vz9/v79/Pv5+PXz8O3r6Obl4uHh
        4ePl5+ns7/Hz9ff5+/z9/f38+vj29PLv7Orn5OPi4eHi4+Xn6ezv8vT2+fr8/f39/Pv5+PXz8O7r
        Z1dHLR4dJzM8SWB0kKzF0czM0tfUzOXw9Pz3/P39/f7+/v38+/r49vTy8O3r6Obl4+Lh4eLj5ujr
        7vH09vn7/P39/f38+vn39PPw7evo5ePi4eHi4+Xn6ezv8fP19/n6/P39/fz6+ff18/Dv7Ojm5OPi
        4eHj5Ofp7O7x8/X3+fr8/f39/Pr49vTx7+xoWEgtHhwlLzdDWm+Lp8DPys3T2dbO5/H0/Pf8/f39
        /v7+/fz7+vj29PLw7evo5uTj4uHi4+Xn6u3w8/X3+vv8/f39/Pv5+PXz8e7s6efk4+Li4+Tm6Ort
        8PL09vj6+/z9/f38+vn39fLw7evo5uTj4uHi4+Xn6ezv8fP19/n6/Pz9/fz7+fj18/Dv7Onm5OPi
        4eLj5efq7O/x8/X3+fr7/P39/Pr59/Xy8O7r6efk4+Li4+Tm6Ort7/Hz9ff5+vv8/f38+/n39fLw
        7utqWkwwIR4mMDhDWGuHorzLyc7V2tjQ6PL1/Pj8/f39/v7+/fz7+vj29PLw7uro5uTj4uLj5Obo
        6+7x8/X3+fr8/P39/Pv5+Pb08e/s6efm5OPi4uPl5+ns7u/x8/X3+fr8/P39/Pr59/Xy8O7s6ef
        m5OPj4+Tl5+ns7u/x8/T19/j5+vv7/Pv6+Pf18/Hw
        """)

    def play_notification_sound(self):
        """Play notification sound if enabled"""
        if st.session_state.sound_enabled:
            # Create an HTML audio element with the base64-encoded WAV file
            audio_html = f"""
                <audio autoplay>
                    <source src="data:audio/wav;base64,{base64.b64encode(self.sound_data).decode()}" type="audio/wav">
                </audio>
                """
            st.write(audio_html, unsafe_allow_html=True)

    def check_new_orders(self, orders):
        """Check for new orders since last check"""
        new_orders = []
        current_time = datetime.now()

        for order in orders:
            order_id = str(order.get('id'))
            date_created = order.get('date_created')
            status = order.get('status')

            # Skip if we've already notified about this order
            if order_id in st.session_state.notifications:
                continue

            # Only process orders with status "on-hold"
            if status != "on-hold":
                continue

            # Check if this is a new order
            try:
                order_date = datetime.fromisoformat(date_created.replace('Z', '+00:00'))
                if order_date > st.session_state.last_check_time:
                    new_orders.append(order)
                    st.session_state.notifications.add(order_id)
                    st.sidebar.info(f"Found new on-hold order: #{order_id} at {order_date}")
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
            message = f"""🛍️ New On-Hold Order! #{order_id}
Customer: {customer_name}
Total: {currency} {total:,.2f}
Time: {datetime.now().strftime('%H:%M:%S')}"""

            # Display notification using Streamlit
            st.toast(message, icon='🛍️')

            # Play notification sound
            self.play_notification_sound()

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