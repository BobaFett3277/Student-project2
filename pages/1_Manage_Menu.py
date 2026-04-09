import streamlit as st
import pandas as pd
import psycopg2

def get_connection():
    return psycopg2.connect(st.secrets["DB_URL"])

st.title("📋 Menu Management")
conn = get_connection()

# --- CREATE FORM ---
with st.form("add_item"):
    st.write("Add New Menu Item")
    name = st.text_input("Name *")
    price = st.number_input("Price", min_value=0.0, step=0.50)
    # Added Quesadillas and Drinks to the options
    cat = st.selectbox("Category", ["Tacos", "Burritos", "Quesadillas", "Drinks", "Sides"])
    if st.form_submit_button("Save Item"):
        if name:
            cur = conn.cursor()
            cur.execute("INSERT INTO menu_items (name, price, category) VALUES (%s, %s, %s)", (name, price, cat))
            conn.commit()
            st.success(f"Added {name} to {cat}!")
            st.rerun()

st.divider()

# --- FILTER FEATURE ---
st.subheader("Filter Menu View")
filter_cat = st.selectbox("View Category:", ["All", "Tacos", "Burritos", "Quesadillas", "Drinks", "Sides"])

# Building the query based on filter
query = "SELECT * FROM menu_items"
params = []

if filter_cat != "All":
    query += " WHERE category = %s"
    params.append(filter_cat)

query += " ORDER BY name ASC"

df = pd.read_sql_query(query, conn, params=params)

# Display Items
for i, row in df.iterrows():
    with st.expander(f"{row['name']} - ${row['price']} ({row['category']})"):
        # Update and Delete logic remains the same...
        new_p = st.number_input("Update Price", value=float(row['price']), key=f"p_{row['id']}")
        if st.button("Update", key=f"u_{row['id']}"):
            cur = conn.cursor()
            cur.execute("UPDATE menu_items SET price = %s WHERE id = %s", (new_p, row['id']))
            conn.commit()
            st.rerun()
conn.close()