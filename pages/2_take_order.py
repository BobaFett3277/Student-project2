import streamlit as st
import pandas as pd
import psycopg2

# 1. Use cache_resource so we don't spam the DB with new connections on every click
@st.cache_resource
def get_connection():
    return psycopg2.connect(st.secrets["DB_URL"])

st.set_page_config(page_title="Place Order", layout="wide")
st.title("🌮 The Taco Shack - Order Now")

# Initialize cart in session state
if 'cart' not in st.session_state:
    st.session_state.cart = []

# --- DATABASE SETUP ---
try:
    conn = get_connection()
except Exception as e:
    st.error("Could not connect to the database. Check your Secrets!")
    st.stop()

# --- SECTION 1: ADD TO CART ---
st.subheader("Add Items to Your Cart")
col_filter, col_item, col_qty = st.columns([1, 2, 1])

with col_filter:
    category_choice = st.selectbox("Step 1: Category", ["Tacos", "Burritos", "Quesadillas", "Drinks", "Sides"])

# Pull filtered items from DB
with conn.cursor() as cur:
    cur.execute("SELECT id, name, price FROM menu_items WHERE is_active = true AND category = %s ORDER BY name", (category_choice,))
    filtered_menu = cur.fetchall()

item_options = {f"{row[1]} (${row[2]:.2f})": {"id": row[0], "name": row[1], "price": float(row[2])} for row in filtered_menu}

with col_item:
    if item_options:
        selected_label = st.selectbox("Step 2: Select Item", options=list(item_options.keys()))
    else:
        st.warning(f"No {category_choice} currently available.")
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
    st.toast(f"Added {item_details['name']} to cart!")
    st.rerun() # Refresh to show the table immediately

st.divider()

# --- SECTION 2: VIEW ORDER & TOTALS ---
st.subheader("Your Current Order")

if not st.session_state.cart:
    st.info("Your cart is empty. Pick a category and item above to start your order.")
else:
    df_cart = pd.DataFrame(st.session_state.cart)
    display_df = df_cart[["name", "quantity", "price", "subtotal"]].copy()
    display_df.columns = ["Item", "Qty", "Price Each", "Subtotal"]
    
    st.table(display_df)
    
    grand_total = df_cart["subtotal"].sum()
    st.markdown(f"## **Total Amount Due: ${grand_total:.2f}**")

    #