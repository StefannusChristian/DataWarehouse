import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
from repo import Repository

class Service:
    def __init__(self, repository: Repository):
        self.repo = repository

    def get_filtered_data_and_figure(self, data:list[tuple], dimension_1:str, dimension_2:str, fact:str, title:str, x_label:str, y_label:str, select_box_content:str,query:str):
        st.header(title)

        df = pd.DataFrame(data, columns=[dimension_1, dimension_2, fact])
        df[dimension_2] = df[dimension_2].astype(str)
        df[fact] = pd.to_numeric(df[fact])
        pd.options.display.float_format = '{:,.2f}'.format

        selected_value = st.selectbox(select_box_content, df[dimension_1].unique())
        filtered_data = df[df[dimension_1] == selected_value]

        values = filtered_data[dimension_1].unique()

        value_data = {value: filtered_data[filtered_data[dimension_1] == value] for value in values}

        fig, ax = plt.subplots()
        for value, data in value_data.items():
            ax.bar(data[dimension_2], data[fact], label=value)

        ax.set_xlabel(x_label)
        ax.set_ylabel(y_label)

        return filtered_data, fig,query

    def get_total_sales_amount_fact_per_branch_per_year(self):
        data,query = self.repo.total_sales_amount_fact_per_branch_per_year_query()
        return self.get_filtered_data_and_figure(
            data, "branch_name", "calendar_year", "total_sales_amount",
            "Total Sales per Branch per Year", "Year", "Total Sales Amount", "Select Branch"
        ,query)

    def get_total_profit_per_product_category_per_year(self):
        data,query = self.repo.total_profit_per_product_category_per_year()
        return self.get_filtered_data_and_figure(data, "category", "calendar_year", "total_profit","Total Profit per Product Category per Year", "Year", "Total Profit", "Select Product Category",query)

    def get_date_dimension(self):
        @st.cache_data(show_spinner=False)
        def split_frame(input_df, rows):
            df = [input_df.loc[i : i + rows - 1, :] for i in range(0, len(input_df), rows)]
            return df

        data = self.repo.get_date_dimension()
        dataset = pd.DataFrame(data, columns=["Date ID", "Date", "Day of Week", "Calendar Month", "Calendar Quarter", "Calendar Year"])

        pagination = st.container()
        bottom_menu = st.columns((4, 1, 1))
        with bottom_menu[2]:
            batch_size = st.selectbox("Page Size", options=[25, 50, 100])
        with bottom_menu[1]:
            total_pages = (
                int(len(dataset) / batch_size) if int(len(dataset) / batch_size) > 0 else 1
            )
            current_page = st.number_input(
                "Page", min_value=1, max_value=total_pages, step=1
            )
        with bottom_menu[0]:
            st.markdown(f"Page **{current_page}** of **{total_pages}** ")

        pages = split_frame(dataset, batch_size)
        return pagination,pages,current_page

    def get_all_table_column_names(self) -> dict:
        table_names = self.repo.get_all_table_names()
        result = {_: None for _ in table_names}

        for tname in table_names:
            result[tname] = self.repo.get_table_column_name(tname)

        return result

    def retrive_all_data_from_all_tables_to_dataframe(self) -> dict[pd.DataFrame]:
        table_names = self.repo.get_all_table_names()
        column_names = self.get_all_table_column_names()
        result = self.repo.retrive_all_data_from_all_tables()

        for tname in table_names:
            return result[tname], column_names[tname]
        return