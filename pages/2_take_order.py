import streamlit as st
import pandas as pd
import psycopg2

# Database connection function
def get_connection():
    return psycopg2.connect(st.secrets["DB_URL"])

st.set_page_config(page_title="Place Your Order", layout="wide")
st.title("🌮 The Taco Shack - Order Now")

# Initialize the 'cart' in session state if it doesn't exist
if 'cart' not in st.session_state:
    st.session_state.cart = []

conn = get_connection()
cur = conn.cursor()

# 1. Pull active menu items from the database (Dynamic Dropdown Requirement)
cur.execute("SELECT id, name, price, category FROM menu_items WHERE is_active = true ORDER BY category, name")
menu_data = cur.fetchall()
menu_items = {row[1]: {"id": row[0], "price": float(row[2]), "cat": row[3]} for row in menu_data}

# --- SECTION 1: ADD TO CART ---
st.subheader("Add Items to Your Cart")
col1, col2, col3 = st.columns([2, 1, 1])

with col1:
    item_choice = st.selectbox("Select Item", options=list(menu_items.keys()))
with col2:
    quantity = st.number_input("Quantity", min_value=1, value=1, step=1)
with col3:
    st.write(" ") # Padding
    add_btn = st.button("Add to Cart 🛒", use_container_width=True)

if add_btn:
    item_details = menu_items[item_choice]
    # Add selection to our temporary list
    st.session_state.cart.append({
        "id": item_details["id"],
        "name": item_choice,
        "quantity": quantity,
        "price": item_details["price"],
        "subtotal": item_details["price"] * quantity
    })
    st.toast(f"Added {item_choice}!")

st.divider()

# --- SECTION 2: VIEW CART & TOTALS ---
st.subheader("Your Current Selection")

if not st.session_state.cart:
    st.info("Your cart is empty. Add some tacos!")
else:
    # Convert cart list to a DataFrame for clean display
    df_cart = pd.DataFrame(st.session_state.cart)
    
    # Show the table to the customer
    st.table(df_cart[["name", "quantity", "price", "subtotal"]])
    
    # Calculate Grand Total
    grand_total = df_cart["subtotal"].sum()
    st.markdown(f"### **Grand Total: ${grand_total:.2f}**")

    # --- SECTION 3: CLOSE OUT / CHECKOUT ---
    with st.form("checkout_form"):
        customer_name = st.text_input("Enter Your Name to Confirm Order *")
        notes = st.text_area("Special Requests / Notes")
        submit_order = st.form_submit_button("Submit & Place Order")

        if submit_order:
            if not customer_name.strip():
                st.error("Please enter your name to finalize the order.")
            else:
                try:
                    # 1. Create the master Order record
                    cur.execute(
                        "INSERT INTO orders (customer_name, status) VALUES (%s, 'Pending') RETURNING id",
                        (customer_name,)
                    )
                    order_id = cur.fetchone()[0]

                    # 2. Loop through cart and add each line item (Many-to-Many logic)
                    for item in st.session_state.cart:
                        cur.execute(
                            """INSERT INTO order_line_items (order_id, item_id, quantity, special_requests) 
                               VALUES (%s, %s, %s, %s)""",
                            (order_id, item["id"], item["quantity"], notes)
                        )
                    
                    conn.commit()
                    st.success(f"Success! Order #{order_id} has been placed for {customer_name}.")
                    
                    # 3. Clear the cart after successful checkout
                    st.session_state.cart = []
                    # st.rerun() # Refresh to clear the table
                except Exception as e:
                    conn.rollback()
                    st.error(f"Database error: {e}")

if st.button("Clear Cart 🗑️"):
    st.session_state.cart = []
    st.rerun()

cur.close()
conn.close()