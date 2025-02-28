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

        # Cash register sound effect (base64 encoded WAV)
        self.sound_data = base64.b64decode("""
        UklGRiQEAABXQVZFZm10IBAAAAABAAEAIlYAAESsAAACABAAZGF0YQAEAADpAHwBtAKcA0cExwKMAhQCeAKNAp
        UCpwKjApMCgQJvAlkCKgIDAuUBwgGfAXsBWQFBASwBGQEIAfcA5gDWAMQAswCiAJIAgwB0AGUAVwBHADkAKwAeABEA
        BQD5/+7/4//Y/87/w/+6/7D/p/+f/5b/j/+I/4D/ef9y/2z/Zv9g/1r/VP9P/0r/Rf9B/z3/Of82/zP/MP8t/yr/KP8m
        /yT/Iv8g/x//Hv8d/xz/HP8b/xr/Gv8Z/xr/Gv8b/xv/HP8c/x3/Hv8f/yD/If8i/yT/Jf8n/yn/K/8t/y//Mf80/zf/O
        v89/0D/Q/9H/0v/T/9T/1j/XP9h/2b/a/9w/3X/e/+B/4f/jf+U/5r/of+o/6//tv+9/8X/zf/V/93/5v/u//f/AAAJABIA
        GwAkAC0ANgA/AEkAUwBdAGYAcAB7AIUAjwCaAKQArgC5AMMAzgDZAOQA7wD6AAUBEAEbASYBMQE7AUYBUQFcAWcBcgF8AY
        cBkQGcAaYBsQG7AcUBzwHZAeMB7QH3AQECCgITAhwCJQIuAjcCQAJJAlECWgJiAmoCcwJ7AoMCiwKTApoCogKqArECuAK/A
        sYCzQLUAtoCpgKSAn4CagJWAkECLQIYAgQC7wHaAcUBsAGbAYUBcAFaAUUBLwEZAQMB7QDXAMEAqwCVAH4AaABSADwAJgAQA
        PoA4wDNALYAoACJAHMATgBfAHAAggCTAKUAtgDIANoA6wD9AA8BIAEyAUMBVQFmAXgBiQGbAawBvQHPAeAB8QEDAhQCJgI3A
        kgCWQJqAnsCjAKdAq4CvQLOAt8C7gIAAxEDIgMzA0QDVQNmA3YDhwOYA6gDuQPJA9oD6gP7AyYEFwQIBPkD6gPaA8sDuwOsA
        5wDjQN9A24DXgNPAz8DMAMgAxEDAgPyAuMC0wLEArUCpQKWAocCVwKXArYC1QL0AhMDMQNQA28DjQOrA8kD6AMGBB8EPQRbB
        HkElwS2BNMEhwR7BG4EYgRVBEkEPQQwBCQEGAQKBP4D8gPmA9kDzQPBA7UDqAOcA5ADgwN3A2oDXgNRA0UDOAMsAx8DEwMGA
        /kC7QLgAtMCxwK6Aq0CoAKUAocCewJuAmICVQJJAjwCMAIjAhcCCgL+AfEB5QHYAcwBvwGyAaYBmQGMAYABcwFnAVoBTgFBA
        TUBKAEcAQ8BAwH2AOoA3QDRAMUAuACsAKAAkwCHAHsAbgBiAFYASgA9ADEAJQAZAAwAAAAA9P/n/9v/z/+9/7L/pv+a/47/g
        v92/2r/X/9T/0f/PP8w/yX/Gf8O/wL/9/7s/uD+1f7K/r/+tP6p/p7+lP6J/n/+dP5q/mD+Vv5M/kL+OP4u/iX+HP4S/gn+A
        P73/e795P3b/dP9yv3C/br9sv2q/aP9m/2U/Y39hv1//Xj9cv1r/WX9X/1Z/VP9Tf1I/UP9Pv05/TX9MP0s/Sj9JP0g/Rz9G
        P0V/RH9Dv0L/Qj9Bf0D/QD9/vz8/Pr8+Pz3/PX89Pzz/PL88fzw/PD87/zv/O/87/zv/O/88Pzw/PH88vz0/PX89vz4/Pr8/
        Pz+/AD9Av0E/Qf9Cf0M/Q/9Ev0V/Rj9HP0f/SL9Jv0p/S39MP00/Tj9PP1A/UT9SP1N/VH9Vv1a/V/9Y/1o/W39cv13/Xz9g
        P2F/Yr9j/2U/Zn9nv2j/aj9rf2y/bf9vP3B/cf9zP3R/db92/3h/eb96/3w/fb9+/0A/gX+C/4Q/hX+G/4g/ib+K/4x/jb+P
        P5B/kf+Tf5S/lj+Xv5j/mn+b/51/nr+gP6G/oz+kf6X/p3+o/6p/q/+tP66/sD+xv7M/tL+1/7d/uP+6f7v/vX++v4A/wb/D
        P8S/xj/Hv8j/yn/L/81/zr/QP9G/0z/Uf9X/13/Y/9o/27/dP95/3//hf+K/5D/lv+b/6H/p/+s/7L/t/+9/8P/yP/O/9P/2
        f/e/+T/6f/v//T/+v8AABAACAANABMAGAAeACMAKQAuADQAOQA/AEQASgBPAFUAWgBgAGUAawBwAHUAewCAAIYAiwCRAJYAn
        ACgAKYAqwCxALYAvADBAMYAzADRANYA3ADhAOYA7ADxAPYA+wABAQYBCwEQARUBGwEgASUBKgEvATQBOQE+AUMBSAFNAVIBVwF
        cAWABZQFqAW8BdAF4AX0BggGHAYsBkAGVAZkBngGiAacBrAGwAbUBuQG+AcIBxgHLAc8B0wHYAdwB4AHkAegB7AHwAfQB+AH8
        AQACACQD
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