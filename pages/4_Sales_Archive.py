import streamlit as st
import pandas as pd
import psycopg2

def get_connection():
    return psycopg2.connect(st.secrets["DB_URL"])

st.set_page_config(page_title="Sales Archive", layout="wide")
st.title("📈 Historical Sales & Archive")

conn = get_connection()
cur = conn.cursor()

# --- SECTION 1: SEARCH & FILTER ---
st.subheader("Search Past Orders")
search_col1, search_col2 = st.columns(2)

with search_col1:
    search_term = st.text_input("Search by Customer Name", placeholder="e.g. John Smith")
with search_col2:
    status_filter = st.selectbox("Filter by Status", ["All", "Completed", "Pending", "Cancelled"])

# Build the Query
query = """
    SELECT o.id, o.customer_name, o.status, o.order_date,
           SUM(oli.quantity * m.price) as order_total
    FROM orders o
    LEFT JOIN order_line_items oli ON o.id = oli.order_id
    LEFT JOIN menu_items m ON oli.item_id = m.id
"""

# Apply Filters
conditions = []
params = []

if search_term:
    conditions.append("o.customer_name ILIKE %s")
    params.append(f"%{search_term}%")

if status_filter != "All":
    conditions.append("o.status = %s")
    params.append(status_filter)

if conditions:
    query += " WHERE " + " AND ".join(conditions)

query += " GROUP BY o.id ORDER BY o.order_date DESC"

# Execute and Display
df = pd.read_sql_query(query, conn, params=params)

if df.empty:
    st.info("No orders found matching those criteria.")
else:
    # Formatting for the UI
    df['order_total'] = df['order_total'].fillna(0).map("${:,.2f}".format)
    st.dataframe(df, use_container_width=True, hide_index=True)

st.divider()

# --- SECTION 2: LIFETIME STATS ---
st.subheader("Lifetime Statistics")
cur.execute("""
    SELECT 
        COUNT(id) as total_orders,
        (SELECT SUM(oli.quantity * m.price) FROM order_line_items oli JOIN menu_items m ON oli.item_id = m.id JOIN orders o ON o.id = oli.order_id WHERE o.status = 'Completed') as total_revenue
    FROM orders
""")
stats = cur.fetchone()

s_col1, s_col2 = st.columns(2)
s_col1.metric("Lifetime Orders", stats[0])
s_col2.metric("Lifetime Revenue", f"${(stats[1] or 0):,.2f}")

cur.close()
conn.close()