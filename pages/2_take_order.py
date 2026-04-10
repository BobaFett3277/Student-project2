import streamlit as st
import pandas as pd
import psycopg2

# 1. Use cache_resource to prevent 'too many connections' errors
@st.cache_resource
def get_connection():
    return psycopg2.connect(st.secrets["DB_URL"])

st.set_page_config(page_title="Place Order", layout="wide")
st.title("🌮 The Taco Shack - Order Now")

# Initialize cart in session state
if 'cart' not in st.session_state:
    st.session_state.cart = []

# --- DATABASE CONNECTION ---
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
    st.rerun()

st.divider()

# --- SECTION 2: VIEW ORDER & CHECKOUT ---
col_cart, col_form = st.columns([1, 1])

with col_cart:
    st.subheader("Your Current Order")
    if not st.session_state.cart:
        st.info("Your cart is empty. Add items above!")
        grand_total = 0.0
    else:
        df_cart = pd.DataFrame(st.session_state.cart)
        st.table(df_cart[["name", "quantity", "subtotal"]])
        grand_total = df_cart["subtotal"].sum()
        st.markdown(f"### Total: ${grand_total:.2f}")

with col_form:
    st.subheader("Checkout Details")
    # The form is OUTSIDE the 'if cart' check so the button is always there
    with st.form("checkout_form", clear_on_submit=True):
        customer_name = st.text_input("Customer Name *")
        notes = st.text_area("Special Requests (e.g., no onions)")
        
        # This is your "PLACE ORDER" button
        submit_order = st.form_submit_button("🚀 PLACE ORDER")

        if submit_order:
            if not st.session_state.cart:
                st.error("Your cart is empty! Add some tacos first.")
            elif not customer_name.strip():
                st.error("Please enter your name.")
            else:
                try:
                    # 'with conn' handles the COMMIT automatically
                    with conn:
                        with conn.cursor() as cur:
                            # 1. Create main order record
                            cur.execute("INSERT INTO orders (customer_name, status) VALUES (%s, 'Pending') RETURNING id", (customer_name,))
                            order_id = cur.fetchone()[0]
                            
                            # 2. Insert line items into the junction table
                            for item in st.session_state.cart:
                                cur.execute("""
                                    INSERT INTO order_line_items (order_id, item_id, quantity, special_requests)
                                    VALUES (%s, %s, %s, %s)
                                """, (order_id, item['id'], item['quantity'], notes))
                    
                    # 3. SUCCESS Logic
                    st.session_state.cart = [] # Clear the cart
                    st.success(f"Order #{order_id} sent to the kitchen!")
                    
                    # 4. REDIRECT to Dashboard (Adjust the path below to match your filename)
                    # Use the name of the file in your /pages/ folder
                    st.switch_page("pages/1_Manage_Menu.py") 
                    
                except Exception as e:
                    st.error(f"Database error: {e}")

    #