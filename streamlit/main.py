import streamlit as st
import json
import requests
from streamlit_feedback import streamlit_feedback
from streamlit_option_menu import option_menu
# нужно пересобрать попробовать контейнеры и должно быть 'http://web:8004/

from streamlit_modal import Modal

st.set_page_config(
    page_title = "Document Chat",
    layout = 'wide',
    page_icon = "🛢️", 
    initial_sidebar_state = "auto", 
)
st.title("Таблица Site")

conn = st.connection("postgresql", type="sql")

# Perform query.
df = conn.query('SELECT * FROM meta.site ', ttl="10m")

st.table(df)