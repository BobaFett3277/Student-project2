import streamlit as st

st.set_page_config(page_title="Taco Shack", page_icon="🌮", layout="centered")

st.title("🌮 Welcome to Taco Shack")
st.write("")

col1, col2 = st.columns(2)

with col1:
    with st.container(border=True):
        st.subheader("Place an order")
        st.write("Browse the menu and place your order.")
        st.page_link("pages/2_take_order.py", label="Order now →", use_container_width=True)

with col2:
    with st.container(border=True):
        st.subheader("Staff area")
        st.write("Menu management, kitchen display, and sales.")
        st.page_link("pages/1_Manage_Menu.py", label="Manage menu →", use_container_width=True)
        st.page_link("pages/3_Kitchen_and_Revenue.py", label="Kitchen & revenue →", use_container_width=True)
        st.page_link("pages/4_Sales_Archive.py", label="Sales archive →", use_container_width=True)
