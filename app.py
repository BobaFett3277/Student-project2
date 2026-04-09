import streamlit as st
import pandas as pd
from db import get_connection

st.title("🌮 Taco Shack Manager")

conn = get_connection()
cur = conn.cursor()

# Metrics logic
cur.execute("SELECT COUNT(*) FROM orders")
order_count = cur.fetchone()[0]

cur.execute("SELECT COUNT(*) FROM menu_items WHERE is_active = true")
item_count = cur.fetchone()[0]

col1, col2 = st.columns(2)
col1.metric("Total Orders", order_count)
col2.metric("Active Menu Items", item_count)

st.subheader("Recent Activity")
df = pd.read_sql_query("SELECT customer_name, status, order_date FROM orders ORDER BY order_date DESC LIMIT 5", conn)
st.table(df)

cur.close()
conn.close()