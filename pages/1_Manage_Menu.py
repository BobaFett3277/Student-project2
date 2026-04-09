import streamlit as st
import pandas as pd
from db import get_connection

st.title("📋 Menu Management")
conn = get_connection()

# CREATE Form
with st.form("add_item"):
    st.write("Add New Menu Item")
    name = st.text_input("Name *")
    price = st.number_input("Price", min_value=0.0)
    cat = st.selectbox("Category", ["Tacos", "Burritos", "Sides"])
    if st.form_submit_button("Save Item"):
        if name: # Simple validation
            cur = conn.cursor()
            cur.execute("INSERT INTO menu_items (name, price, category) VALUES (%s, %s, %s)", (name, price, cat))
            conn.commit()
            st.success("Item Added!")
            st.rerun()

# READ, UPDATE, DELETE
df = pd.read_sql_query("SELECT * FROM menu_items", conn)
for i, row in df.iterrows():
    with st.expander(f"{row['name']} (${row['price']})"):
        # Update
        new_p = st.number_input("Update Price", value=float(row['price']), key=f"p_{row['id']}")
        if st.button("Update", key=f"u_{row['id']}"):
            cur = conn.cursor()
            cur.execute("UPDATE menu_items SET price = %s WHERE id = %s", (new_p, row['id']))
            conn.commit()
            st.rerun()
        
        # Delete with Confirmation
        if st.button("🗑️ Delete", key=f"d_{row['id']}"):
            st.session_state[f"confirm_{row['id']}"] = True
        
        if st.session_state.get(f"confirm_{row['id']}"):
            st.error("Are you sure?")
            if st.button("Confirm Delete", key=f"c_{row['id']}"):
                cur = conn.cursor()
                cur.execute("DELETE FROM menu_items WHERE id = %s", (row['id'],))
                conn.commit()
                st.rerun()
conn.close()