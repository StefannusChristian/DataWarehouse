import pandas as pd
import streamlit as st
from repo import Repository

class Service:
    def __init__(self, repository: Repository):
        self.repo = repository

    def get_total_sales_amount_fact_per_branch_per_quarter(self):
        data = self.repo.total_sales_amount_fact_per_branch_per_quarter_query()

        df = pd.DataFrame(data, columns=["branch_name", "calendar_quarter", "total_sales_amount"])
        df["total_sales_amount"] = pd.to_numeric(df["total_sales_amount"])

        selected_branch = st.selectbox("Select Branch", df["branch_name"].unique())
        filtered_data = df[df["branch_name"] == selected_branch]

        return filtered_data

    def get_total_profit_amount_per_branch_per_quarter(self):
        data = self.repo.total_profit_per_branch_per_quarter_year()

        df = pd.DataFrame(data, columns=["branch_name", "calendar_quarter", "total_profit"])
        df["total_profit"] = pd.to_numeric(df["total_profit"])

        selected_branch = st.selectbox("Select Branch", df["branch_name"].unique())
        filtered_data = df[df["branch_name"] == selected_branch]

        return filtered_data

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
