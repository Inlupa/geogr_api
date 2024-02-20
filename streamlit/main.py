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
    "postgresql+psycopg2",
    username="postgres",
    password="postgres",  # plain (unescaped) text
    host="postgres",
    database="postgres",
)

# создаем подключение к базе
engine = create_engine(url_object)

# Читаем данные из базы для нужной нам таблице, в данном случае это таблица site
site_table = pd.read_sql('SELECT * FROM meta.site ', engine)
unique_site = site_table.nunique()
unique_site = pd.DataFrame(unique_site, columns=[' '])

labels = list(unique_site.T)
values = unique_site.T.values.tolist()

fig = go.Figure(data=[go.Bar(x = labels, y = values[0])])

# Уникальное кол-во значений в таблице site
st.title("Статистики по таблице site")
st.subheader("Количество уникальных значений каждого столбца")
st.plotly_chart(fig, use_container_width=True)

###########################################################################

# Количство переменных по типу
id_len = len(site_table['id'])
code_len = len(site_table['code'])
name_len = len(site_table['name'])
site_type_id_len = len(site_table['site_type_id'])
owner_id_len = len(site_table['owner_id'])
addr_id_len = len(site_table['addr_id'])
geom_latlon_len = len(site_table['geom_latlon'])
description_len = len(site_table['description'])
parent_id_len = len(site_table['parent_id'])
name_eng_len = len(site_table['name_eng'])
lon_len = len(site_table['lon'])
lat_len = len(site_table['lat'])

int_len = id_len + site_type_id_len + owner_id_len + addr_id_len
string_len = code_len + name_len + description_len + name_eng_len
geo_len = geom_latlon_len
float_len = lon_len + lat_len


fig1 = go.Figure()
fig1.add_trace(go.Pie(values=[int_len, string_len, geo_len, float_len], labels=["int4", 'string', 'geometry', 'float'], hole=0.9))

fig1.update_layout(
    annotations=[dict(text='Количество<br>переменных<br>по типу', x=0.5, y=0.5, font_size=20, showarrow=False)])
st.subheader("Типы переменных")
st.plotly_chart(fig1, use_container_width=True)

###################################################################################

st.subheader("Статистические параметры числовых значений")
st.dataframe(data = site_table.describe(), use_container_width = True)

###################################################################################

st.subheader("Распределение данных по площади")

fig2 = go.Figure(go.Scattermapbox(lat=site_table["lat"], lon=site_table["lon"], text=site_table["name"]))
map_center = go.layout.mapbox.Center(lat=58.38, 
                                     lon=97.45)
fig2.update_layout(mapbox_style="open-street-map",
                  mapbox=dict(center=map_center, zoom=2), 
                    height=1000,)

st.plotly_chart(fig2, use_container_width=True)


