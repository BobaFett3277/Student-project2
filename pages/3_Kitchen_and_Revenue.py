import streamlit as st
import pandas as pd
import psycopg2
from datetime import datetime

# Database connection function
def get_connection():
    return psycopg2.connect(st.secrets["DB_URL"])

st.set_page_config(page_title="Kitchen & Revenue", layout="wide")

conn = get_connection()
cur = conn.cursor()

# --- HEADER SECTION ---
st.title("🍳 Kitchen Display & Sales Tracker")

# --- REVENUE TRACKING (Calculated from 'Completed' orders) ---
# We calculate total revenue from order_line_items joined with menu_items
cur.execute("""
    SELECT SUM(oli.quantity * m.price) 
    FROM order_line_items oli
    JOIN menu_items m ON oli.item_id = m.id
    JOIN orders o ON oli.order_id = o.id
    WHERE o.status = 'Completed'
""")
total_made = cur.fetchone()[0] or 0.0

st.metric("Total Revenue (Completed Orders)", f"${total_made:.2f}")

if st.button("Reset Daily Total"):
    st.warning("Note: In a production app, this would archive the total. For this project, you can simply filter by date in your SQL.")

st.divider()

# --- KITCHEN PILE (PENDING ORDERS) ---
st.subheader("🔥 Current Pending Orders")

# Query to get pending orders and their items
cur.execute("""
    SELECT o.id, o.customer_name, m.name, oli.quantity, oli.special_requests
    FROM orders o
    JOIN order_line_items oli ON o.id = oli.order_id
    JOIN menu_items m ON oli.item_id = m.id
    WHERE o.status = 'Pending'
    ORDER BY o.id ASC
""")
pending_data = cur.fetchall()

if not pending_data:
    st.success("All caught up! No pending orders.")
else:
    # We group items by Order ID so they show up together
    orders_dict = {}
    for row in pending_data:
        oid, name, item, qty, req = row
        if oid not in orders_dict:
            orders_dict[oid] = {"name": name, "items": []}
        orders_dict[oid]["items"].append(f"{qty}x {item} (Notes: {req or 'None'})")

    # Display each order as a "Ticket"
    for oid, details in orders_dict.items():
        with st.container(border=True):
            col_info, col_btn = st.columns([3, 1])
            with col_info:
                st.write(f"### Order #{oid} - {details['name']}")
                for item in details["items"]:
                    st.write(f"- {item}")
            
            with col_btn:
                # The "Done" Button
                if st.button("✅ Mark Done", key=f"done_{oid}"):
                    cur.execute("UPDATE orders SET status = 'Completed' WHERE id = %s", (oid,))
                    conn.commit()
                    st.toast(f"Order #{oid} moved to Completed!")
                    st.rerun()

st.divider()

# --- COMPLETED PILE ---
st.subheader("✅ Recently Completed")
df_completed = pd.read_sql_query("""
    SELECT id, customer_name, order_date 
    FROM orders 
    WHERE status = 'Completed' 
    ORDER BY order_date DESC LIMIT 5
""", conn)
st.dataframe(df_completed, use_container_width=True)

cur.close()
conn.close()