import pandas as pd
import streamlit as st
from repo import Repository

class Service:
    def __init__(self, repository: Repository):
        self.repo = repository

    def get_data_and_query(self, dimension_1: str, dimension_2: str, fact: str, repo_method):
        data, query = repo_method
        df = pd.DataFrame(data, columns=[dimension_1, dimension_2, fact])

        # Convert to numeric types
        df[dimension_2] = pd.to_numeric(df[dimension_2], errors='coerce')
        df[fact] = pd.to_numeric(df[fact], errors='coerce')

        # Explicitly set the data types
        df[dimension_2] = df[dimension_2].astype('float64')
        df[fact] = df[fact].astype('float64')

        return df, query

    def get_selectbox_values(self, column_name: str, table_name: str):
        return self.repo.select_box_values(column_name, table_name)

    # Fact Per Dimension 1 and 2 Service
    def get_total_sales_amount_fact_per_branch_per_year(self, branch_name):
        return self.get_data_and_query("branch_name", "calendar_year", "total_sales_amount", self.repo.total_sales_amount_fact_per_branch_per_year_query(branch_name))

    # Derived Fact Per Dimension 1 and 2 Service
    def get_total_profit_per_product_category_per_year(self, category):
        return self.get_data_and_query("category", "calendar_year", "total_profit", self.repo.total_profit_per_product_category_per_year(category))

    # Quantity (Grain) Service
    def get_quantity_grain_data(self):
        data, query = self.repo.quantity_grain()
        columns = ["Order ID","Date","Branch","Customer Name","Total Amount"]
        df = pd.DataFrame(data, columns=columns)
        df['Date'] = pd.to_datetime(df['Date'], format='%Y%m%d').dt.strftime('%A, %d-%m-%Y')
        return df, query

    # Additive Fact Per Dimension 1,2 and 3 Service
    def get_total_profit_per_product_category_per_branch_per_year(self, category: str, branch: str):
        data, query = self.repo.total_profit_per_product_category_per_branch_per_year(category, branch)
        columns = ["Category","Year","Branch Name","Total Profit"]
        df = pd.DataFrame(data, columns=columns)
        df["Year"] = pd.to_numeric(df["Year"], errors="coerce")
        df["Total Profit"] = pd.to_numeric(df["Total Profit"], errors="coerce")
        return df,query

    # Non-Additive Fact Per Dimension 1 and 2 Service
    def get_average_unit_price_per_product_per_year(self, product):
        return self.get_data_and_query("product", "calendar_year", "average_unit_price", self.repo.average_unit_price_per_product_per_year(product))

    def get_average_units_sold_per_transaction_per_branch_per_year(self, branch):
        return self.get_data_and_query("branch", "calendar_year", "average_units_sold_per_transaction", self.repo.average_units_sold_per_transaction_per_branch_per_year(branch))

    # Date Dimension Service
    def get_date_dimension(self):
        data, query = self.repo.date_dimension_query()
        columns = self.get_all_table_column_names()["date_dimension"]
        df = pd.DataFrame(data, columns=columns)
        df['full_date'] = pd.to_datetime(df['full_date'], format='%Y%m%d').dt.strftime('%A, %d-%m-%Y')
        df = df.astype({"date_id" : "string"})
        return df, query

    # Accumulation Fact Service
    def get_top_5_quantity_of_products_bought_per_customer_per_product_category(self, category: str):
        data, query = self.repo.top_5_quantity_of_products_bought_per_customer_per_product_category(category)
        columns = ["Customer Name","Product Category","Total Quantity Bought"]
        df = pd.DataFrame(data, columns=columns)
        return df, query

    # Factless Fact Service
    def get_factless_fact_data(self, product, branch):
        data, query = self.repo.list_of_customers_who_never_bought_a_product_per_branch(product, branch)
        columns = ["YYYY MM DD", "Branch name", "Customer name"]
        df = pd.DataFrame(data, columns=columns)
        # df = pd.DataFrame(data)
        return df, query

    @st.cache_data(show_spinner=False)
    def split_frame(_self, df, rows):
        df = [df.loc[i : i + rows - 1, :] for i in range(0, len(df), rows)]
        return df

    def paginate_df(self, df: pd.DataFrame):
        pagination = st.container()
        bottom_menu = st.columns((4, 1, 1))
        with bottom_menu[2]:
            batch_size = st.selectbox("Page Size", options=[10, 25, 50, 100])
        with bottom_menu[1]:
            total_pages = (
                int(len(df) / batch_size) if int(len(df) / batch_size) > 0 else 1
            )
            current_page = st.number_input(
                "Page", min_value=1, max_value=total_pages, step=1
            )
        with bottom_menu[0]:
            st.markdown(f"Page **{current_page}** of **{total_pages}** ")

        pages = self.split_frame(df, batch_size)
        height = (len(pages[current_page - 1]) + 1) * 35
        return pagination,pages,current_page,height

    def get_all_table_column_names(self) -> dict:
        """
        Sample output:
        {
            "table_name_1": [col1, col2, col3, ...],
            "table_name_2": [col1, col2, col3, ...],
            "table_name_3": [col1, col2, col3, ...],
            ...
        }
        """

        table_names = self.repo.get_all_table_names()[0]
        result = {_: None for _ in table_names}

        for tname in table_names:
            result[tname] = self.repo.get_column_name(tname)[0]

        return result

    # Victor
    def retrive_all_data_from_all_tables(self) -> dict:
        """
        Sample output:
        {
            "table_name_1": [
                (x11, x12, x13, ...),
                (x21, x22, x23, ...),
                (x31, x32, x33, ...),
                ...
            ],
            "table_name_2": [
                (x11, x12, x13, ...),
                (x21, x22, x23, ...),
                (x31, x32, x33, ...),
                ...
            ],
            "table_name_3": [
                (x11, x12, x13, ...),
                (x21, x22, x23, ...),
                (x31, x32, x33, ...),
                ...
            ],
            ...
        }
        """

        table_names = self.repo.get_all_table_names()[0]  # [table_name1, table_name2, ...]
        column_names = self.get_all_table_column_names()
        result = {_: None for _ in table_names}   # {table_name1: None, table_name1: None, ...}
        df = {_: None for _ in table_names}   # {table_name1: None, table_name1: None, ...}

        for tname in table_names:
            data = self.repo.select_all_from(tname)[0]

            result[tname] = data
            df[tname] = pd.DataFrame(data, columns=column_names[tname])

        return result, df

