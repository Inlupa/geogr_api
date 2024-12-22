import streamlit as st
from sqlalchemy import create_engine
import pandas as pd

from functions import (
    load_meteo_to_db,
)

engine = create_engine("postgresql+psycopg2://postgres:qq@192.168.5.219/amur22_non_iwp")
conn = engine.connect()


def change_nine(df):
    df = df.sort_values(by=["date"])
    df = df.replace("-99.00", None).replace("-99", None)
    return df


def export_meteo():
    try:
        uploaded_files = st.file_uploader(
            "Выберите файлы с метеоданными", accept_multiple_files=True, key=1
        )
    except Exception as e:
        st.warning(
            f"Извините прошла ошибка при прочтении файлов, пожалуйста проверьте формат данных. \
                Ошибка: {e}"
        )
    df_perc = pd.DataFrame()
    df_temp = pd.DataFrame()
    df_def = pd.DataFrame()
    for file in uploaded_files:
        if ("PRE" in file.name) | ("DEF" in file.name) | ("TEMP" in file.name):
            data = []
            try:
                for line in file:
                    data.append(line.decode())

                headers_site = ["date"] + data[2].split()
                data = data[6:]
                data = list(
                    map(
                        lambda x: x.replace("  ", "_").replace("__", "_").split("_"),
                        data,
                    )
                )
                # тут надо условие на то куда в какой датафрейм класть данные
                df = pd.DataFrame(data, columns=headers_site)
                df["date"] = pd.to_datetime(df["date"])
                if "PRE" in file.name:
                    df_perc = pd.concat([df, df_perc], axis=0)
                if "TEMP" in file.name:
                    df_temp = pd.concat([df, df_temp], axis=0)
                if "DEF" in file.name:
                    df_def = pd.concat([df, df_def], axis=0)
            except Exception as e:
                # st.warning(f"Невозможно докодировать файл: {file.name},
                # проверье что содержимое соответствует стандарту")
                st.warning(f"{e}")
        else:
            st.warning(
                f"Файл {file.name} не входит в перечень метеоданных, \
                    пожалуйста выберите лишь файлы TEMP, PRE и DEF"
            )

    upload_meteodata = st.file_uploader(
        "Выберите файл с перечнем метеостанций (MeteoStation.bas)", key=2
    )
    # meteo_dict = {}
    if upload_meteodata:
        meteo = pd.read_csv(
            upload_meteodata,
            sep=",|\t+",
            skiprows=2,
            on_bad_lines="skip",
            encoding="windows-1251",
            header=None,
        )
        meteo = pd.concat([meteo.iloc[:, 0], meteo.iloc[:, 4]], axis=1)
        meteo = meteo.rename(columns={0: "code", 4: "name"})
        # meteo_dict = meteo.set_index("code")["name"].to_dict()
    # к сожалению лишь через трай эксепт пока что
    if len(df_temp) > 0:
        df_temp = change_nine(df_temp)
    if len(df_perc) > 0:
        df_perc = change_nine(df_perc)
    if len(df_def) > 0:
        df_def = change_nine(df_def)

    if upload_meteodata and uploaded_files:
        if st.button(
            label="Загрузить данные",
        ):
            with st.spinner("Данные загружаются, подождите..."):
                if len(df_temp) > 0:
                    load_meteo_to_db(df_temp, 1000, "температура")
                if len(df_perc) > 0:
                    load_meteo_to_db(df_perc, 23, "осадки")
                if len(df_def) > 0:
                    load_meteo_to_db(df_def, 1021, "дефицит пара")
            st.balloons()
            st.success("Новые данные были загружены")
