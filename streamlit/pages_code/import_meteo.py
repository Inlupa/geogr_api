import streamlit as st
from sqlalchemy import create_engine
import tempfile
import zipfile
import pandas as pd
from streamlit_extras.stylable_container import stylable_container  # type: ignore
import os
from datetime import date

from functions import (
    check_empty,
    rid_duplicates,
)

engine = create_engine("postgresql+psycopg2://postgres:qq@192.168.5.219/amur22_non_iwp")
conn = engine.connect()
site_type_ids = (1, 20, 3, 163, 139, 5, 140, 158, 150, 159, 145, 157)


def import_meteo():
    # начальная и конечная дата
    with stylable_container(
        "datepicker",
        """
                        input {
                            color: white;
                            }
                        div[role="presentation"] div{
                        color: white;
                        }

                        div[role="gridcell"] div{
                            color:#4169E1;
                            };

                        """,
    ):
        date_start = st.date_input(
            "Введите начальную дату",
            date.fromisoformat("2024-01-01"),
            min_value=date.fromisoformat("1950-01-01"),
        )
        date_start = date_start.strftime("%Y-%m-%d")
        date_end = st.date_input(
            "Введите конечную дату",
            date.fromisoformat("2024-01-01"),
            min_value=date.fromisoformat("1950-01-01"),
        )
        date_end = date_end.strftime("%Y-%m-%d")

    if date_start > date_end:
        st.warning("Начальная дата больше чем конечная дата")

    upload_meteodata = st.file_uploader(
        "Выберите файл с перечнем метеостанций (MeteoStation.bas)", key=2
    )
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
        meteo_from_bas = meteo.rename(columns={0: "code", 4: "name"})
        meteo_from_bas["code"] = meteo_from_bas["code"].apply(lambda x: str(x))

    # список кодов и имен из файла метеобас
    if "refresh" in st.session_state.download:
        if upload_meteodata and date_start and date_end:
            if st.button(
                label="Скачать данные из базы",
            ):
                with st.spinner("Данные загружаются, подождите..."):
                    with tempfile.TemporaryDirectory() as tmpdirname:
                        count = 0
                        # count_bar = 1
                        # my_bar = st.progress(0)
                        # percent = 1/len(meteo_from_bas[["code", "name"]].values)
                        for code_download, name_download in meteo_from_bas[
                            ["code", "name"]
                        ].values:
                            # my_bar.progress(percent*count)
                            parameters = (date_start, date_end, code_download)
                            temp_df_csv = rid_duplicates(
                                "Temp", parameters, 1000,
                                site_type_ids)
                            def_df_csv = rid_duplicates(
                                "Def", parameters, 1021,
                                site_type_ids)
                            pre_df_csv = rid_duplicates(
                                "Prec", parameters, 23,
                                site_type_ids)

                            df_csv = pd.concat(
                                [
                                    pre_df_csv.set_index("date_loc"),
                                    temp_df_csv.set_index("date_loc"),
                                    def_df_csv.set_index("date_loc"),
                                ],
                                axis=1,
                            ).reset_index()

                            if check_empty(df_csv) is False:
                                date_range = pd.date_range(
                                    date_start, date_end, freq="D"
                                )
                                # Create a DataFrame with the dates as the index
                                date_range_df = pd.DataFrame(index=date_range)
                                df_csv = pd.concat(
                                    [date_range_df, df_csv.set_index("date_loc")],
                                    axis=1,
                                ).reset_index()
                                df_csv = df_csv.fillna(-99)
                                try:
                                    df_csv["index"] = df_csv["index"].dt.strftime(
                                        "%Y%m%d"
                                    )
                                except Exception as e:
                                    print(e)
                                    pass

                                df_csv["zeros"] = 0
                                df_csv.to_csv(
                                    f"{tmpdirname}/{code_download}.csv",
                                    index=None,
                                    encoding="cp1251",
                                    header=False,
                                    lineterminator='\r\n',
                                )
                            else:
                                count += 1
                            # count_bar += 1

                        if count == len(meteo_from_bas["code"]):
                            st.warning(
                                "По введенным сайтам на эти даты данные отсутсвуют"
                            )
                        else:
                            # Create a zip archive
                            with zipfile.ZipFile("Meteo.zip", "w") as zip_file:
                                # Iterate over all the files in the directory
                                for file in os.listdir(f"{tmpdirname}"):
                                    # Write the file to the zip archive
                                    zip_file.write(os.path.join(f"{tmpdirname}", file))

                            def small():
                                os.remove("Meteo.zip")

                            st.info("Данные были загружены, теперь их можно скачать")
                            dbutton = st.download_button(
                                label="Скачать архив данных",
                                data=open("Meteo.zip", "rb").read(),
                                file_name="Meteo.zip",
                                mime="application/x-zip",
                                on_click=small(),
                            )
                            if dbutton:
                                st.query_params(download="true")
