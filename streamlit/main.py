import streamlit as st
from sqlalchemy import create_engine
import pandas as pd
from streamlit_option_menu import option_menu  # type: ignore
import os

from functions import (
    create_map,
    stats_brush,
)

from pages_code.import_meteo import import_meteo
from pages_code.import_hydro import import_hydro
from pages_code.export_meteo import export_meteo
from pages_code.export_hydro import export_hydro

engine = create_engine("postgresql+psycopg2://postgres:qq@192.168.5.219/amur22_non_iwp")
conn = engine.connect()

# конфиг странички
st.set_page_config(
    page_title="Dashboard",
    layout="wide",
    page_icon="🛢️",
    initial_sidebar_state="auto",
)


if "download" not in st.session_state:
    st.session_state.download = "refresh"

styles = {
            "container": {
                "display": "flex",
                "align-items": "center",
                "text-align": "center",
                "background-color": "#262730",
            },
            "icon": {
                "color": "lightblue",
                "text-align": "center",
            },
            "nav-link": {
                "display": "flex",
                "margin": "10px",
                "font-size": "25px",
                "text-align": "center",
                "align-items": "center",
                "--hover-color": "black",
            },
            "nav-link-selected": {
                "background-color": "#1E90FF",
                "color": "black",
                "font-size": "25px",
            },
        }

# ######################
# # sidebar
# ######################
with st.sidebar:
    choose = option_menu(
        "Лаборатория Гидроинформатики",
        ["Статистика", "Загрузить данные", "Скачать данные"],
        icons=["pie-chart-fill", "cloud-upload", "download"],
        menu_icon="cast",
        default_index=0,
        styles={
            "container": {
                "padding": "5!important",
                "background-color": "#262730",
                "width": "500px",
            },
            "menu-title": {"font-size": "18px"},
            "nav-link": {
                "font-size": "18px",
                "text-align": "left",
                "--hover-color": "black",
            },
            "nav-link-selected": {
                "background-color": "#1E90FF",
                "color": "black",
                "font-size": "18px",
            },
        },
    )

# ######################
# # start
# ######################

# page Главная
if choose == "Главная":
    st.title(
        """Добро пожаловать на главную страницу нашего сайта с дашбордом\
            по географической базе данных лаборатории Гидроинформатики. \
            Здесь вы можете получить доступ к актуальной информации \
            об основных измеряемых параметрах на территории России, \
            их пространственному распределению, \
            а так же базовым статистическим характеристикам"""
    )

if choose == "Статистика":
    styles_stat = styles.copy()
    styles_stat["nav-link"]["font-size"] = "18px"
    styles_stat["nav-link-selected"]["font-size"] = "18px"
    choose = option_menu(
        None,
        [
            "Максимальная температура",
            "Минимальная температура",
            "Средняя температура",
            "Отностительная влажность",
            "Дефицит упругости водяного пара",
            "Осадки",
            "Уровень",
            "Расход",
        ],
        icons=[
            "thermometer-sun",
            "thermometer-snow",
            "thermometer-half",
            "droplet-fill",
            "cloud-fill",
            "cloud-drizzle-fill",
            "moisture",
            "water",
        ],
        menu_icon="cast",
        default_index=0,
        orientation="horizontal",
        styles=styles_stat,
    )


if choose == "Загрузить данные":
    choose = option_menu(
        None,
        ["Метеоданные", "Гидроданные"],
        icons=[
            "wind",
            "water",
        ],
        menu_icon="cast",
        default_index=0,
        orientation="horizontal",
        styles=styles,
    )
if choose == "Скачать данные":
    choose = option_menu(
        None,
        ["Метеоданные ", "Гидроданные "],
        icons=[
            "wind",
            "water",
        ],
        menu_icon="cast",
        default_index=0,
        orientation="horizontal",
        styles=styles,
    )

#############################
# Данные для загрузки в базу
#############################
if choose == "Метеоданные ":
    import_meteo()

if choose == "Гидроданные ":
    import_hydro()

if choose == "Метеоданные":
    export_meteo()


if choose == "Гидроданные":
    export_hydro()


#############################
# Данные для статистики
#############################
if choose == "Максимальная температура":
    st.title("Данные по максимальной температуре")
    stats = pd.read_csv(
        f"{os.getcwd()}/csv_data/full_stat_максимальная температура.csv",
        encoding="windows-1251",
        sep=";",
    )
    mapping = pd.read_csv(
        f"{os.getcwd()}/csv_data/map_максимальная температура.csv",
        encoding="windows-1251",
        sep=";",
    )

    # дообработка датафрейма с данными
    stats_brush(stats)

    # вывод карты и таблицы на страницу
    st.dataframe(data=stats, use_container_width=True)
    st.plotly_chart(create_map(mapping), use_container_width=True)


if choose == "Минимальная температура":
    st.title("Статистики по минимальной температуре")

    stats = pd.read_csv(
        f"{os.getcwd()}/csv_data/full_stat_минимальная температура.csv",
        encoding="windows-1251",
        sep=";",
    )
    mapping = pd.read_csv(
        f"{os.getcwd()}/csv_data/map_минимальная температура.csv",
        encoding="windows-1251",
        sep=";",
    )

    # дообработка датафрейма с данными
    stats_brush(stats)

    # вывод карты и таблицы на страницу
    st.dataframe(data=stats, use_container_width=True)
    st.plotly_chart(create_map(mapping), use_container_width=True)


if choose == "Средняя температура":
    st.title("Статистики по средней температуре")
    stats = pd.read_csv(
        f"{os.getcwd()}/csv_data/full_stat_минимальная температура.csv",
        encoding="windows-1251",
        sep=";",
    )
    mapping = pd.read_csv(
        f"{os.getcwd()}/csv_data/map_температура.csv", encoding="windows-1251", sep=";"
    )

    # дообработка датафрейма с данными
    stats_brush(stats)

    # вывод карты и таблицы на страницу
    st.dataframe(data=stats, use_container_width=True)
    st.plotly_chart(create_map(mapping), use_container_width=True)


if choose == "Отностительная влажность":
    st.title("Статистики по относительной влажности")
    stats = pd.read_csv(
        f"{os.getcwd()}/csv_data/full_stat_отн_влажность.csv", encoding="windows-1251", sep=";"
    )
    mapping = pd.read_csv(
        f"{os.getcwd()}/csv_data/map_отн_влажность.csv", encoding="windows-1251", sep=";"
    )

    # дообработка датафрейма с данными
    stats_brush(stats)

    # вывод карты и таблицы на страницу
    st.dataframe(data=stats, use_container_width=True)
    st.plotly_chart(create_map(mapping), use_container_width=True)


if choose == "Дефицит упругости водяного пара":
    st.title("Статистики по дефициту упругости водяного пара")
    stats = pd.read_csv(
        f"{os.getcwd()}/csv_data/full_stat_дефицит упругости водяного пара.csv",
        encoding="windows-1251",
        sep=";",
    )
    mapping = pd.read_csv(
        f"{os.getcwd()}/csv_data/map_дефицит упругости водяного пара.csv",
        encoding="windows-1251",
        sep=";",
    )
    # дообработка датафрейма с данными
    stats_brush(stats)

    # вывод карты и таблицы на страницу
    st.dataframe(data=stats, use_container_width=True)
    st.plotly_chart(create_map(mapping), use_container_width=True)


if choose == "Осадки":
    st.title("Статистики по осадкам")
    stats = pd.read_csv(
        f"{os.getcwd()}/csv_data/full_stat_осадки.csv", encoding="windows-1251", sep=";"
    )
    mapping = pd.read_csv(
        f"{os.getcwd()}/csv_data/map_осадки.csv", encoding="windows-1251", sep=";"
    )

    # дообработка датафрейма с данными
    stats_brush(stats)

    # вывод карты и таблицы на страницу
    st.dataframe(data=stats, use_container_width=True)
    st.plotly_chart(create_map(mapping), use_container_width=True)

if choose == "Уровень":
    st.title("Статистики по уровню")
    stats = pd.read_csv(
        f"{os.getcwd()}/csv_data/full_stat_уровень.csv", encoding="windows-1251", sep=";"
    )
    mapping = pd.read_csv(
        f"{os.getcwd()}/csv_data/map_уровень.csv", encoding="windows-1251", sep=";"
    )

    # дообработка датафрейма с данными
    stats_brush(stats)

    # вывод карты и таблицы на страницу
    st.dataframe(data=stats, use_container_width=True)
    st.plotly_chart(create_map(mapping), use_container_width=True)

if choose == "Расход":
    st.title("Статистики по расходу")
    stats = pd.read_csv(
        f"{os.getcwd()}/csv_data/full_stat_расход.csv", encoding="windows-1251", sep=";"
    )
    mapping = pd.read_csv(
        f"{os.getcwd()}/csv_data/map_расход.csv", encoding="windows-1251", sep=";"
    )

    # дообработка датафрейма с данными
    stats_brush(stats)

    # вывод карты и таблицы на страницу
    st.dataframe(data=stats, use_container_width=True)
    st.plotly_chart(create_map(mapping), use_container_width=True)
