import streamlit as st
from sqlalchemy import create_engine
import pandas as pd
from functions import (
    upload_catalog,
    load_values,
)

engine = create_engine("postgresql+psycopg2://postgres:qq@192.168.5.219/amur22_non_iwp")
conn = engine.connect()


def export_hydro():
    site_name = pd.read_sql(
        """select id, code, name from meta.site where site_type_id in (2, 106, 6)""", engine
    )
    site_name["code"] = site_name["code"].apply(lambda x: "(" + x + ") ")
    site_name["select"] = site_name["code"] + site_name["name"]
    site_name_select = st.selectbox(
        label="Выберите пост",
        options=site_name["select"].values,
        index=None,
        placeholder="Поиск",
    )

    upload_hydro = st.file_uploader(
        "Выберите файлы с расходами", accept_multiple_files=True, key=3
    )
    try:
        if upload_hydro:
            hydro_data = pd.DataFrame()
            for file in upload_hydro:
                hydro_data_temp = pd.read_csv(
                    file, sep="\t|\s+",  # type: ignore # noqa: W605
                    skiprows=3, encoding="windows-1251", header=None
                )
                del hydro_data_temp[0]
                hydro_data_temp.rename(columns={1: "Дата", 2: "Расход"}, inplace=True)

                hydro_data_temp["Дата"] = hydro_data_temp["Дата"].apply(
                    lambda x: str(x)
                )
                # Проверяем на наличие неправильного формата в данных(наличие дня
                # номер 90 в записи в обычном и високосном)

                if (
                    "90" in hydro_data_temp.loc[220, "Дата"]
                    or "90" in hydro_data_temp.loc[221, "Дата"]
                ):
                    if "90" in hydro_data_temp.loc[220, "Дата"]:
                        hydro_data_temp.loc[220:229, "Дата"] = hydro_data_temp.iloc[
                            220:230
                        ]["Дата"].apply(lambda x: x.replace("99", "81"))
                        hydro_data_temp["Дата"] = pd.to_datetime(
                            hydro_data_temp["Дата"]
                        )
                    else:
                        hydro_data_temp.loc[221:230, "Дата"] = hydro_data_temp.iloc[
                            221:231
                        ]["Дата"].apply(lambda x: x.replace("99", "81"))
                        hydro_data_temp["Дата"] = pd.to_datetime(
                            hydro_data_temp["Дата"]
                        )
                else:
                    hydro_data_temp["Дата"] = pd.to_datetime(hydro_data_temp["Дата"])

                hydro_data = pd.concat([hydro_data, hydro_data_temp], axis=0)
    except Exception as e:
        st.warning(f"Неправильный формат входных данных(проверьте даты в файле). Ошибка: {e}")
    if site_name_select and upload_hydro:
        if st.button(label="Загрузить данные", key=5):
            with st.spinner("Данные загружаются, подождите..."):
                start = site_name_select.find(")") + 2
                site_name_select = site_name_select[start:]
                site_id_hydro = site_name[site_name["name"] == site_name_select][
                    "id"
                ].iloc[0]
                progress_text = f"Загрузка данных по посту {site_name_select}"
                my_bar = st.progress(0, text=progress_text)
                percent = 1/len(hydro_data[["Дата", "Расход"]].values)
                count = 1
                catalog_for_hydro = upload_catalog(site_id_hydro, variable_id_load=48)
                catalog_for_hydro_id = catalog_for_hydro[0].get("id", None)
                # тут осталось дописать код для загрузки данных в бд
                # есть готовая функция load_values
                for date_hydro, value_hydro in hydro_data[["Дата", "Расход"]].values:
                    date_hydro = date_hydro.isoformat() + ".000"
                    my_bar.progress(percent*count,
                                    text=progress_text)
                    if value_hydro != -99:
                        load_values(date_hydro, value_hydro, catalog_for_hydro_id)
                    count = count + 1
            st.success("Новые данные были загружены")
