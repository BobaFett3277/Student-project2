import streamlit as st
from db import get_connection

st.title("📝 New Order")
conn = get_connection()
cur = conn.cursor()

# Dynamic Dropdown: Pull items from DB
cur.execute("SELECT id, name FROM menu_items WHERE is_active = true")
items = {row[1]: row[0] for row in cur.fetchall()}

with st.form("order_form"):
    cust = st.text_input("Customer Name *")
    choice = st.selectbox("Select Item", options=list(items.keys()))
    qty = st.number_input("Quantity", min_value=1)
    
    if st.form_submit_button("Place Order"):
        if cust:
            # 1. Insert Order
            cur.execute("INSERT INTO orders (customer_name) VALUES (%s) RETURNING id", (cust,))
            order_id = cur.fetchone()[0]
            
            # 2. Insert into Many-to-Many Junction Table
            cur.execute("INSERT INTO order_line_items (order_id, item_id, quantity) VALUES (%s, %s, %s)", 
                        (order_id, items[choice], qty))
            conn.commit()
            st.success(f"Order #{order_id} Created!")

cur.close()
conn.close()