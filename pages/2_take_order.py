import streamlit as st
import pandas as pd
import psycopg2

# 1. REMOVED @st.cache_resource to prevent 'stale' connection errors
def get_connection():
    return psycopg2.connect(st.secrets["DB_URL"])

st.set_page_config(page_title="Place Order", layout="wide")
st.title("🌮 The Taco Shack - Order Now")

# Initialize cart in session state
if 'cart' not in st.session_state:
    st.session_state.cart = []

# --- DATABASE CONNECTION ---
# We open the connection at the start of the run
try:
    conn = get_connection()
except Exception as e:
    st.error("Could not connect to database. Check your Streamlit Secrets!")
    st.stop()

# --- SECTION 1: ADD TO CART ---
st.subheader("Add Items to Your Cart")
col_filter, col_item, col_qty = st.columns([1, 2, 1])

with col_filter:
    category_choice = st.selectbox("Step 1: Category", ["Tacos", "Burritos", "Quesadillas", "Drinks", "Sides"])

# 2. Use a 'try' block for the cursor to handle any interface errors gracefully
try:
    with conn.cursor() as cur:
        cur.execute("SELECT id, name, price FROM menu_items WHERE is_active = true AND category = %s ORDER BY name", (category_choice,))
        filtered_menu = cur.fetchall()
except psycopg2.InterfaceError:
    # If the connection died, reconnect once
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute("SELECT id, name, price FROM menu_items WHERE is_active = true AND category = %s ORDER BY name", (category_choice,))
        filtered_menu = cur.fetchall()

item_options = {f"{row[1]} (${row[2]:.2f})": {"id": row[0], "name": row[1], "price": float(row[2])} for row in filtered_menu}

# ... [The rest of your code for item selection and Add to Cart button] ...

# --- AT THE VERY END OF YOUR SCRIPT ---
# It is good practice to close the connection so you don't leak resources
conn.close()

    #