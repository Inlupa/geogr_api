import streamlit as st
from sqlalchemy import create_engine
import requests
import pandas as pd
import plotly.graph_objects as go  # type: ignore


dict_data = {1333: 1, 3: 2, 1327: 3, 2: 4}
engine = create_engine("postgresql+psycopg2://postgres:qq@192.168.5.219/amur22_non_iwp")
conn = engine.connect()


def check_empty(df):
    return df.empty


def get_date_value(
    date_s: str, date_f: str, site_code: str, variable_id: int, types: tuple
) -> pd.DataFrame:
    variable_id = int(variable_id)
    sql_get_data_for_code = f"""
            select date_loc, value, source_id from ((select date_loc, value, site_id,\
                source_id from data.data_value as value left join \
                                (select * from data."catalog" as c left join \
                                (SELECT distinct "variable"."id" as new_id FROM meta.variable) \
                                    as var on c.variable_id  = var.new_id) as foo \
                                 on value.catalog_id =foo.id \
                                where (new_id = {variable_id}) and (date_loc >= '{date_s}') \
                                    and  (date_loc <= '{date_f}' )) as foo2 \
                                left join meta.site as site on foo2.site_id = site.id) \
                                 where (site.code = '{site_code}') and site_type_id in {types}
            """
    date_and_value = pd.read_sql(sql_get_data_for_code, engine)
    date_and_value = date_and_value.sort_values("date_loc").reset_index(drop=True)
    return date_and_value


def create_map(map_df: "pd.DataFrame") -> "pd.DataFrame":
    """Создание карты с набором сайтов

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
    fig = go.Figure(
        go.Scattermapbox(
            lat=map_df["lat"],
            lon=map_df["lon"],
            text=map_df["name_map"],
            marker=dict(
                colorbar=dict(title="Количество измерений"),
                color=map_df["value_amount"],
                autocolorscale=False,
                colorscale=[[0, "red"], [1, "#2EFF00"]],
                size=8,
            ),
        ),
        layout=layout,
    )
    map_center = go.layout.mapbox.Center(lat=58.38, lon=97.45)
    fig.update_layout(
        mapbox_style="open-street-map", mapbox=dict(center=map_center, zoom=2)
    )
    return fig


def stats_brush(df: "pd.DataFrame") -> "pd.DataFrame":
    """Функция которую надо будет перенести
        в создание итогового датафрейма дабы не захломлять стримлит лишними расчетами

    Args:
        df(pd.DataFrame): датафрейм с статистикой по перменной с набором всех сайтов
    """
    # кусок кода который надо будет перенести
    # в создание итогового датафрейма дабы не захломлять стримлит лишними расчетами

    # удаление лишней колонки которая вылезла из-за нескольких операций по скливанию датафреймов
    # (может поправить в основном коде, но не критично )
    df.drop(df.columns[[0]], axis=1, inplace=True)

    # несколько операций по смене даты на более читабельный формат
    df["date_loc_min"] = pd.to_datetime(df["date_loc_min"])
    df["date_loc_min"] = df["date_loc_min"].dt.strftime("%Y-%m-%d")

    df["date_loc_max"] = pd.to_datetime(df["date_loc_max"])
    df["date_loc_max"] = df["date_loc_max"].dt.strftime("%Y-%m-%d")
    df["site_code"] = df["site_code"].astype(str)

    df.rename(
        columns={
            "site_code": "Индекс",
            "site_name": "Название",
            "value_mean": "Среднее значение",
            "value_min": "Минимум",
            "value_max": "Максимум",
            "value_amount": "Кол-во измерений",
            "date_loc_min": "Начало",
            "date_loc_max": "Конец",
        },
        inplace=True,
    )


def upload_catalog(site_id_load: int, variable_id_load: int):
    """функция для добавления записи нового каталога если его не существует

    Args:
        site_id (int): айди сайта в из набора загруженного пользователем данных
        variable_id (int): айди переменной котрая загружается

    Returns:
        _type_: возвращает обновленный каталог с уже вставленным сайтом
    """

    site_id_load = int(site_id_load)
    variable_id_load = int(variable_id_load)

    catalog = requests.post(
        url="http://192.168.5.215:5003/Catalog/GetByQuery",
        json={"siteIds": [site_id_load], "variableIds": [variable_id_load]},
    )
    catalog = catalog.json()

    if not catalog:
        catalog_send = {
            "siteId": site_id_load,
            "variableId": variable_id_load,
            "methodId": 0,
            "sourceId": 1333,
            "offsetTypeId": 102,
            "valueTypeId": 2,
            "deviceId": 100,
            "offsetTypeIdAdd": 3,
        }

        r = requests.post(url="http://192.168.5.215:5003/Catalog", json=catalog_send)
        # обновляем каталог после того как вставили недостающие строки
        catalog = requests.post(
            url="http://192.168.5.215:5003/Catalog/GetByQuery",
            json={"siteIds": [site_id_load], "variableIds": [variable_id_load]},
        )
        catalog = catalog.json()
    return catalog


def load_values(date_loc, value: "float", catalog_id: "int"):
    """функция по проверки и наличию записи значения переменной в таблицу бд

    Args:
        date_loc (timestamp): дата для подачи в бд
        value (int): значения наблюдения
        catalog_id (int): айди каталога по этой переменной и сайту
    """
    catalog_id = int(catalog_id)
    value = float(value)

    get_value = {
        "dateS": date_loc,
        "dateF": date_loc,
        "isDateLoc": True,
        "qclGE": 0,
        "catalogIds": [catalog_id],
    }
    value_exist = requests.post(
        url="http://192.168.5.215:5003/DataValue/GetByQuery", json=get_value
    )
    value_exist = value_exist.json()
    if not value_exist:
        if value is not None:
            put_value = [
                {
                    "catalogId": catalog_id,
                    "value": value,
                    "dateLOC": date_loc,
                    "dateUTC": date_loc,
                    "offsetValue": 0,
                    "offsetValueAdd": 0,
                    "qcl": 0,
                }
            ]
            value_add = requests.post(
                url="http://192.168.5.215:5003/DataValue/DataValueList", json=put_value
            )


def load_meteo_to_db(df: pd.DataFrame, variable_id: int, variable_name: str):
    """
    loading data to db

    Args:
        df (pd.DataFrame): dataframe of meteodata
        value_id (str): variable_id in db to for function to
            understand where to load data from df
    """
    sql = """ select id, code from meta.site s
     where site_type_id in (1, 20, 3, 163, 139, 5, 140, 158, 150, 159, 145, 157)
    """
    df["year"] = df["date"].dt.year
    years = df["year"].unique()
    # текст для отображения в прогресс баре
    progress_text = f"Загрузка данных по параметру {variable_name}"
    # инициализация прогресс бара
    my_bar = st.progress(0, text=progress_text)
    # счетчик количества кодов по которым нужно загрузить данные
    code_amount = 0
    for year in years:
        df_year = df[df["year"] == year].dropna(how="all", axis=1)
        code_amount = code_amount + len(df_year[df_year.columns[1:-1]].columns)
    # процент того на сколько должен двигаться прогресс бар в зависимости от кодов 
    percent = 1/code_amount
    count = 1
    for year in years:
        # удаляем столбец если все значения в нем нулл
        df_year = df[df["year"] == year].dropna(how="all", axis=1)
        # продолжнине счетчика учитывающее сколько кодов за год уже загрузилось
        for code in df_year[df_year.columns[1:-1]]:
            my_bar.progress(percent*count,
                            text=progress_text)
            dict_code_exist = pd.read_sql(sql, engine)
            dict_code_exist = dict_code_exist.set_index("code")["id"].to_dict()
            site_id = dict_code_exist.get(code)
            if site_id is None:
                # пропустить столбец с отсутсвующим столбцом по коду если его нету
                st.warning(
                    f"Метеоданных для поста с кодом:{code} не существует, \
                        он не будет записан в базу данных"
                )
                continue

            catalog = upload_catalog(dict_code_exist.get(code), variable_id)
            for date_loc, value in df_year[["date", code]].values:
                if value is not None:
                    catalog_id = catalog[0].get("id", None)
                    value = float(value)
                    date_loc = date_loc.isoformat() + ".000"
                    load_values(date_loc, value, catalog_id)
            count = count + 1
    conn.close()


def get_index(df, dict_data) -> pd.DataFrame:
    data = df["source_id"].unique()[0]
    df["source_id"] = dict_data[data]
    return df


def rid_duplicates(var_name, parameters, var_id, site_types):
    date_start, date_end, code_download = parameters
    df = get_date_value(date_start, date_end, code_download, var_id, site_types)
    df = df.rename(columns={"value": var_name})
    df = (
        df.groupby("source_id")
        .apply(get_index, dict_data=dict_data)
        .reset_index(drop=True)
    )
    df = df.sort_values(by=["date_loc", "source_id"]).drop_duplicates(
        subset=["date_loc"]
    )
    df.drop(columns=["source_id"], inplace=True)
    return df
