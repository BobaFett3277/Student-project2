import psycopg2
import streamlit as st

def get_connection():
    """Returns a connection using the URL stored in Streamlit Secrets."""
    return psycopg2.connect(st.secrets["DB_URL"])