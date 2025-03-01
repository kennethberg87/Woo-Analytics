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
                    audio.volume = 1.0;  # Set volume to maximum
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

        # Remove expired notifications
        for order_id in expired_notifications:
            del st.session_state.notifications[order_id]

    def monitor_orders(self, woo_client):
        """Monitor for new orders and show notifications"""
        try:
            # Only check for new orders every 30 seconds
            current_time = datetime.now()
            time_diff = (current_time - st.session_state.last_check_time).total_seconds()

            if time_diff < 30:
                return False

            # Update last check time
            st.session_state.last_check_time = current_time

            # Get today's date
            today = datetime.now().date()

            # Fetch recent orders
            recent_orders = woo_client.get_orders(today, today)

            new_order_count = 0

            for order in recent_orders:
                order_id = order.get('id')

                # Check if this is a new order we haven't notified about
                if order_id and order_id not in st.session_state.notifications:
                    # Add to notifications with current timestamp
                    st.session_state.notifications[order_id] = current_time

                    # Show notification for new order
                    order_total = order.get('total', '0')
                    customer_name = ""
                    if 'billing' in order and order['billing']:
                        first_name = order['billing'].get('first_name', '')
                        last_name = order['billing'].get('last_name', '')
                        customer_name = f"{first_name} {last_name}".strip()

                    st.balloons()
                    st.success(f"🎉 Ny ordre mottatt! Ordre #{order_id} - {customer_name} - kr {order_total}")

                    # Play sound notification
                    self.play_notification_sound()

                    new_order_count += 1

            # Clean up old notifications
            self.clean_old_notifications()

            return new_order_count > 0

        except Exception as e:
            st.error(f"Feil ved sjekk av nye ordrer: {str(e)}")
            return False