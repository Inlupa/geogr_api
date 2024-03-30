import streamlit as st
import json
import requests
import pandas as pd
from streamlit_feedback import streamlit_feedback
from streamlit_option_menu import option_menu
import plotly.graph_objects as go
import os

# нужно пересобрать попробовать контейнеры и должно быть 'http://web:8004/

# конфиг странички
st.set_page_config(
    page_title = "Dashboard",
    layout = 'wide',
    page_icon = "🛢️", 
    initial_sidebar_state = "auto", 
)



def create_map(map_df: "pd.DataFrame") -> "pd.DataFrame":
    """ Создание карты с набором сайтов

    Args:
        map_df (pd.DataFrame): датафрейм для постороения карты 

    Returns:
        _type_: карта plotly с построенными точками 
    """
    # настройка изображения 
    layout = go.Layout(
        autosize=False,
        width=1250,
        height=1000,
        xaxis=go.layout.XAxis(linecolor="black", linewidth=1, mirror=True),
        yaxis=go.layout.YAxis(linecolor="black", linewidth=1, mirror=True),
        margin=go.layout.Margin(l=50, r=50, b=100, t=100, pad=4),
    )

    # структура карты 
    fig = go.Figure(go.Scattermapbox(lat=map_df["lat"],
                                    lon=map_df["lon"], 
                                    text= map_df["name_map"],
                                    marker=dict(colorbar=dict(title="Количество измерений"),
                                                color=map_df['value_amount'],
                                                )
                                    ), 
                    layout=layout)
    map_center = go.layout.mapbox.Center(lat=58.38, 
                                        lon=97.45)
    fig.update_layout(mapbox_style="open-street-map",
                    mapbox=dict(center=map_center, zoom=2))
    return fig
    
    
 
def stats_brush(df: "pd.DataFrame") -> "pd.DataFrame":
    """ Функция которую надо будет перенести 
        в создание итогового датафрейма дабы не захломлять стримлит лишними расчетами

    Args:
        df(pd.DataFrame): датафрейм с статистикой по перменной с набором всех сайтов
    """
    # кусок кода который надо будет перенести 
    # в создание итогового датафрейма дабы не захломлять стримлит лишними расчетами
    
    # удаление лишней колонки которая вылезла из-за нескольких операций по скливанию датафреймов
    # (может поправить в основном коде, но не критично ) 
    df.drop(df.columns[[0]], axis= 1, inplace= True)
    
    # несколько операций по смене даты на более читабельный формат 
    df['date_loc_min'] = pd.to_datetime(df['date_loc_min'])
    df['date_loc_min'] = df['date_loc_min'].dt.strftime('%Y-%m-%d')
    
    df['date_loc_max'] = pd.to_datetime(df['date_loc_max'])
    df['date_loc_max'] = df['date_loc_max'].dt.strftime('%Y-%m-%d') 
    
    df.rename(columns={"site_code": "Уникальный нормер сайта",
                       "site_name": "Название сайта",
                       "value_mean": "Среднее",
                       "value_min": "Минималльное",
                       "value_max": "Максимальное",
                       "value_amount": "Кол-во измерений",
                       "date_loc_min": "Минимальная дата наблюдения",
                       "date_loc_max": "Максмальная дата наблюдения"},
              inplace=True)
       
# ######################
# # sidebar
# ######################
with st.sidebar:
    choose = option_menu(None, ["Главная", "---", "Максимальная температура", "Минимальная температура", "Средняя температура", "Отностительная влажность", "Дефицит упругости водяного пара", "Осадки"],
                         default_index=0,
                         styles={
        "container": {"padding": "5!important", "background-color": "#262730", "width":"500px"},
        "menu-title": {"font-size": "18px"},
        "icon": {"color": "#1E90FF", "font-size": "20px"},
        "nav-link": {"font-size": "18px", "text-align": "left", "--hover-color": "black"},
        "nav-link-selected": {"background-color": "#1E90FF", "color": "black", "font-size": "18px"},
    }
    )

# ######################
# # start
# ######################

# page Главная
if choose == "Главная":
    st.title("на табах данного приложения представлена статистика по таблицы amur")
    
if choose == "Максимальная температура":
   
    st.title("Данные по максимальной температуре")
    stats = pd.read_csv(f"{os.getcwd()}/full_stat_максимальная температура.csv", encoding = "windows-1251", sep = ";")
    mapping = pd.read_csv(f"{os.getcwd()}/map_максимальная температура.csv", encoding = "windows-1251", sep = ";")

    # дообработка датафрейма с данными
    stats_brush(stats)

   # вывод карты и таблицы на страницу
    st.dataframe(data = stats, use_container_width = True)
    st.plotly_chart(create_map(mapping), use_container_width=True)


if choose == "Минимальная температура":
    st.title("Статистики по минимальной температуре")
    
    stats = pd.read_csv(f"{os.getcwd()}/full_stat_минимальная температура.csv", encoding = "windows-1251", sep = ";")
    mapping = pd.read_csv(f"{os.getcwd()}/map_минимальная температура.csv", encoding = "windows-1251", sep = ";") 
      
    # дообработка датафрейма с данными
    stats_brush(stats)

    # вывод карты и таблицы на страницу
    st.dataframe(data = stats, use_container_width = True)
    st.plotly_chart(create_map(mapping), use_container_width=True)


if choose == "Средняя температура":
    st.title("Статистики по средней температуре")
    stats = pd.read_csv(f"{os.getcwd()}/full_stat_минимальная температура.csv", encoding = "windows-1251", sep = ";")
    mapping = pd.read_csv(f"{os.getcwd()}/map_температура.csv", encoding = "windows-1251", sep = ";")  
     
    # дообработка датафрейма с данными
    stats_brush(stats)

    # вывод карты и таблицы на страницу
    st.dataframe(data = stats, use_container_width = True)
    st.plotly_chart(create_map(mapping), use_container_width=True)
    
    

if choose == "Отностительная влажность":
    st.title("Статистики по относительной влажности")
    stats = pd.read_csv(f"{os.getcwd()}/full_stat_отн_влажность.csv", encoding = "windows-1251", sep = ";")
    mapping = pd.read_csv(f"{os.getcwd()}/map_отн_влажность.csv", encoding = "windows-1251", sep = ";")   
    
    # дообработка датафрейма с данными
    stats_brush(stats)
    
    # вывод карты и таблицы на страницу
    st.dataframe(data = stats, use_container_width = True)
    st.plotly_chart(create_map(mapping), use_container_width=True)
    
    

if choose == "Дефицит упругости водяного пара":
    st.title("Статистики по дефициту упругости водяного пара")
    stats = pd.read_csv(f"{os.getcwd()}/full_stat_дефицит упругости водяного пара.csv", encoding = "windows-1251", sep = ";")
    mapping = pd.read_csv(f"{os.getcwd()}/map_дефицит упругости водяного пара.csv", encoding = "windows-1251", sep = ";")   
    # дообработка датафрейма с данными
    stats_brush(stats)
    
    # вывод карты и таблицы на страницу
    st.dataframe(data = stats, use_container_width = True)
    st.plotly_chart(create_map(mapping), use_container_width=True)
    
    

if choose == "Осадки":
    st.title("Статистики по осадкам")
    stats = pd.read_csv(f"{os.getcwd()}/full_stat_осадки.csv", encoding = "windows-1251", sep = ";")
    mapping = pd.read_csv(f"{os.getcwd()}/map_осадки.csv", encoding = "windows-1251", sep = ";") 
      
    # дообработка датафрейма с данными
    stats_brush(stats)

    # вывод карты и таблицы на страницу
    st.dataframe(data = stats, use_container_width = True)
    st.plotly_chart(create_map(mapping), use_container_width=True)    


    
