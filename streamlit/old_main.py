import streamlit as st
import json
import requests
import pandas as pd
from streamlit_feedback import streamlit_feedback
from streamlit_option_menu import option_menu
from geoalchemy2 import Geometry
from sqlalchemy import create_engine
from sqlalchemy import URL

import plotly.graph_objects as go

# нужно пересобрать попробовать контейнеры и должно быть 'http://web:8004/

# конфиг странички
st.set_page_config(
    page_title = "Dashboard",
    layout = 'wide',
    page_icon = "🛢️", 
    initial_sidebar_state = "auto", 
)

# Тайтл
# параметры подключения к базе
url_object = URL.create(
    "postgresql+psycopg2",streamlit/old_main.py
    username="postgres",
    password="qq",  # plain (unesascaped) text
    host="192.168.5.219",
    database="amur22_non_iwp",
)

# создаем подключение к базе
engine = create_engine(url_object)

# Читаем данные из базы для нужной нам таблице, в данном случае это таблица catalog
catalog_table = pd.read_sql('SELECT * FROM data.catalog', engine)
unique_catalog = catalog_table.nunique()
unique_catalog = pd.DataFrame(unique_catalog, columns=[' '])

labels = list(unique_catalog.T)
values = unique_catalog.T.values.tolist()

fig = go.Figure(data=[go.Bar(x = labels, y = values[0])])

# Уникальное кол-во значений в таблице site
st.title("Статистики по таблице catalog")
st.subheader("Количество уникальных значений каждого столбца")
st.plotly_chart(fig, use_container_width=True)

###################################################################################
data_table = pd.read_sql('SELECT * FROM data.data_value LIMIT 9000000', engine)

unique_data = data_table.nunique()
unique_data = pd.DataFrame(unique_data, columns=[' '])

labels_data = list(unique_data.T)
values_data = unique_data.T.values.tolist()

fig = go.Figure(data=[go.Bar(x = labels_data, y = values_data[0])])

# Уникальное кол-во значений в таблице data_value
st.title("Статистики по таблице data_value")
st.subheader("Количество уникальных значений каждого столбца")
st.plotly_chart(fig, use_container_width=True)

###########################################################################
###########################################################################

st.subheader("Статистические параметры числовых значений таблица catalog")
st.dataframe(data = catalog_table.describe(), use_container_width = True)

###################################################################################

st.subheader("Статистические параметры числовых значений таблица data_value")
st.dataframe(data = data_table.describe(), use_container_width = True)