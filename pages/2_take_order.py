import streamlit as st
import pandas as pd
import psycopg2

def get_connection():
    return psycopg2.connect(st.secrets["DB_URL"])

st.title("🌮 The Taco Shack - Order Now")

if 'cart' not in st.session_state:
    st.session_state.cart = []

conn = get_connection()
cur = conn.cursor()

st.subheader("Add Items to Your Cart")

# --- TWO-STEP FILTERED DROPDOWN ---
col_filter, col_item, col_qty = st.columns([1, 2, 1])

with col_filter:
    # 1. Select the Category
    category_choice = st.selectbox("Step 1: Category", ["Tacos", "Burritos", "Quesadillas", "Drinks", "Sides"])

# 2. Pull only items matching that category
cur.execute("SELECT id, name, price FROM menu_items WHERE is_active = true AND category = %s ORDER BY name", (category_choice,))
filtered_menu = cur.fetchall()
item_options = {f"{row[1]} (${row[2]:.2f})": {"id": row[0], "name": row[1], "price": float(row[2])} for row in filtered_menu}

with col_item:
    # 3. Select the Item (Options change based on Step 1)
    if item_options:
        selected_label = st.selectbox("Step 2: Select Item", options=list(item_options.keys()))
    else:
        st.warning(f"No {category_choice} available.")
        selected_label = None

with col_qty:
    quantity = st.number_input("Quantity", min_value=1, value=1)

if st.button("Add to Cart 🛒") and selected_label:
    item_details = item_options[selected_label]
    st.session_state.cart.append({
        "id": item_details["id"],
        "name": item_details["name"],
        "quantity": quantity,
        "price": item_details["price"],
        "subtotal": item_details["price"] * quantity
    })
    st.toast(f"Added {item_details['name']}!")

# Rest of the Cart and Checkout logic remains the same...
# [View Cart and Submit Order code goes here]

cur.close()
conn.close()