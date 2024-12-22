import streamlit as st
from sqlalchemy import create_engine
import tempfile
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


def import_hydro():
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

    site_name = pd.read_sql(
        """select id, code, name from meta.site where site_type_id=2""", engine
    )
    site_name["code"] = site_name["code"].apply(lambda x: "(" + x + ") ")
    site_name["select"] = site_name["code"] + site_name["name"]
    site_name_select = st.selectbox(
        label="Выберите пост",
        options=site_name["select"].values,
        index=None,
        placeholder="Поиск",
    )
    # список кодов и имен из файла метеобас
    if site_name_select and date_start and date_end:
        if st.button(
            label="Скачать данные из базы",
        ):
            with st.spinner("Данные загружаются, подождите..."):
                start = site_name_select.find("(") + 1
                end = site_name_select.find(")")
                code_hydro = site_name_select[start:end]
                not_exists = False
                with tempfile.TemporaryDirectory() as tmpdirname:
                    parameters = (date_start, date_end, code_hydro)
                    q_df_csv = rid_duplicates("Q", parameters, 48, (2, 106, 6))
                    if check_empty(q_df_csv) is False:
                        date_range = pd.date_range(date_start, date_end, freq="D")
                        # Create a DataFrame with the dates as the index
                        date_range_df = pd.DataFrame(index=date_range)
                        q_df_csv = pd.concat(
                            [date_range_df, q_df_csv.set_index("date_loc")], axis=1
                        ).reset_index()
                        q_df_csv = q_df_csv.fillna(-99)

                        try:
                            q_df_csv["index"] = q_df_csv["index"].dt.strftime("%Y%m%d")
                        except Exception as ex:
                            print(ex)
                            pass

                        q_df_csv.to_csv(
                            f"{tmpdirname}/{code_hydro}.csv",
                            index=None,
                            encoding="cp1251",
                            header=False,
                            lineterminator='\r\n',
                        )
                    else:
                        not_exists = True

                    if not_exists is True:
                        st.warning("По выбраному сайту на эти даты данные отсутсвуют")
                    else:

                        def small():
                            os.remove(f"{tmpdirname}/{code_hydro}.csv")

                        st.info("Данные были загружены, теперь их можно скачать")
                        dbutton = st.download_button(
                            label="Скачать данные по сайту",
                            data=open(f"{tmpdirname}/{code_hydro}.csv", "rb").read(),
                            file_name=f"{code_hydro}.csv",
                            mime="text/csv",
                            on_click=small(),
                        )
                        if dbutton:
                            st.query_params(download="true")
