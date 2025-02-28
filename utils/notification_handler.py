import streamlit as st
from datetime import datetime, timedelta
import time
import base64


class NotificationHandler:

    def __init__(self):
        # Initialize notification state in session
        if 'notifications' not in st.session_state:
            st.session_state.notifications = {
            }  # Changed to dict to store timestamps
        if 'last_check_time' not in st.session_state:
            st.session_state.last_check_time = datetime.now()
        if 'sound_enabled' not in st.session_state:
            st.session_state.sound_enabled = True

    def play_notification_sound(self):
        """Play notification sound if enabled"""
        if st.session_state.sound_enabled:
            js_code = """
                <script>
                function playSound() {
                    var audio = new Audio('attached_assets/cash-register.mp3');
                    audio.volume = 1.0;  // Set volume to maximum
                    audio.play().catch(function(error) {
                        console.log("Error playing sound:", error);
                    });
                }
                playSound();
                </script>
            """
            st.components.v1.html(js_code, height=0)

    def clean_old_notifications(self):
        """Remove notifications older than 60 minutes"""
        current_time = datetime.now()
        expired_notifications = []

        for order_id, timestamp in st.session_state.notifications.items():
            if (current_time - timestamp) > timedelta(minutes=60):
                expired_notifications.append(order_id)

        for order_id in expired_notifications:
            del st.session_state.notifications[order_id]

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
                order_date = datetime.fromisoformat(
                    date_created.replace('Z', '+00:00'))
                if order_date > st.session_state.last_check_time:
                    new_orders.append(order)
                    st.session_state.notifications[
                        order_id] = current_time  # Store timestamp
            except Exception as e:
                st.error(f"Error processing order date: {e}")

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
            message = f"""🛍️ Ny ordre mottatt!
Ordrenummer: {order_id}
Kunde: {customer_name}
Totalbeløp: {currency} {total:,.2f}
Fullført: {datetime.now().strftime('%H:%M:%S')}"""

            # Display notification using Streamlit
            st.toast(message, icon='🛍️')

            # Play notification sound
            self.play_notification_sound()

            # Display in sidebar if notification is less than 60 minutes old
            if (datetime.now() - st.session_state.notifications.get(
                    str(order_id), datetime.now())) < timedelta(minutes=60):
                st.sidebar.success(message)

        except Exception as e:
            st.error(f"Error displaying notification: {e}")

    def monitor_orders(self, woo_client, check_interval=30):
        """Monitor for new orders and display notifications"""
        try:
            # Clean up old notifications first
            self.clean_old_notifications()

            # Get current time
            current_time = datetime.now()

            # Fetch recent orders
            orders = woo_client.get_orders(
                start_date=(current_time -
                            timedelta(minutes=check_interval)).date(),
                end_date=current_time.date())

            # Check for new orders
            new_orders = self.check_new_orders(orders)

            # Display notifications for new orders
            for order in new_orders:
                self.display_notification(order)

            return True  # Return True to indicate monitoring is active

        except Exception as e:
            st.error(f"Error monitoring orders: {e}")
            return False
