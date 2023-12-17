import streamlit as st
import altair as alt
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from streamlit_option_menu import option_menu
from service import Service

class GUI:
    def __init__(self, service: Service):
        self.service = service
        self.fig_size = 400
        self.set_page_config()
        self.navbar()

    # Page Config
    def set_page_config(self):
        st.set_page_config(page_title="Gudang Data Final Project", page_icon="bar_chart", initial_sidebar_state="auto", layout="wide")

    # TITLE HEADER
    def title_header(self):
        st.markdown("<h3 style='text-align: center;'>IBDA4011 - Gudang Data Final Project</h3>", unsafe_allow_html=True)
        st.markdown(
            """
            <div style='display: flex; justify-content: center; align-items: center;'>
                <div style='text-align:center;'>
                    <h5>Dominique Huang</h5>
                    <h5>202000216</h5>
                </div>
                <div style='text-align:center;'>
                    <h5>Stefannus Christian</h5>
                    <h5>202000138</h5>
                </div>
                <div style='text-align:center;'>
                    <h5>Victor Chendra</h5>
                    <h5>202000338</h5>
                </div>
                <div style='text-align:center;'>
                    <h5>Wira Yudha</h5>
                    <h5>202000536</h5>
                </div style='text-align:center;'>
            </div>
            """,
            unsafe_allow_html=True
    )
        st.divider()

    def navbar(self):
        options = [
            "Display Data",
            "Quantity (Grain)",
            "Total Sales Fact",
            "Derived Fact",
            "Additive Fact",
            "Non Additive Fact",
            "Factless Fact",
            "Snapshot Fact",
            "Accumulation Fact",
            "Date Dimension",
            "Matrix Bus"
        ]
        icons = [
            "ui-checks",
            "diamond-fill",
            "piggy-bank-fill",
            "arrow-right-square-fill",
            "plus-square-fill",
            "dash-square-fill",
            "file-earmark-code-fill",
            "camera-reels-fill",
            "collection-fill",
            "calendar-event-fill",
            "table"
        ]

        options_length = len(options)
        icons_length = len(icons)

        try:
            assert options_length == icons_length
            with st.sidebar:
                selected_option = option_menu(
                    menu_title=None,
                    options=options,
                    icons=icons,
                    menu_icon="cast",
                    default_index=0,
                )

            if selected_option == "Display Data":
                self.title_header()
                self.show_tables_content()

            elif selected_option == "Quantity (Grain)":
                title = "Quantity (Grain) - Order Fac"
                self.show_quantity_grain_content(title)

            elif selected_option == "Total Sales Fact":
                title = "Total Sales Amount Fact Per Branch Per Year"
                self.show_total_sales_fact_content(title)

            elif selected_option == "Derived Fact":
                title = "Total Profit Per Product Category Per Year"
                self.show_derived_fact_content(title)

            elif selected_option == "Additive Fact":
                title = "Total Profit Per Product Category Per Branch Per Year"
                self.show_additive_fact_content(title)

            elif selected_option == "Non Additive Fact":
                title = "Average Unit Price Per Product Per Year"
                self.show_non_additive_fact_content(title)

            elif selected_option == "Factless Fact":
                title = "Promotion Fact"
                self.show_factless_fact_content(title)

            elif selected_option == "Snapshot Fact":
                title = ""
                self.show_snapshot_fact_content(title)

            elif selected_option == "Accumulation Fact":
                title = ""
                self.show_accumulation_fact_content(title)

            elif selected_option == "Date Dimension":
                title = "Date Dimension"
                self.show_date_dimension_content(title)

            elif selected_option == "Matrix Bus":
                title = ""
                self.show_matrix_bus_content()

        except AssertionError:
            st.error(f"Cannot Show Sidebar!  \nOptions Length ({options_length}) != Icons Length ({icons_length})")

    # Total Sales Amount Fact Per Branch Per Year
    def show_total_sales_fact_content(self, title: str):
        st.header(title)
        selected_branch = st.selectbox("Select Branch", self.service.get_selectbox_values("branch_name","branch"))
        data, query = self.service.get_total_sales_amount_fact_per_branch_per_year(selected_branch)
        self.line_chart_bar_chart_and_table_content(data,'calendar_year', 'total_sales_amount', 'Year', 'Total Sales Amount', query)

    # Total Profit Per Product Category Per Year
    def show_derived_fact_content(self, title: str):
        st.header(title)
        selected_category = st.selectbox("Select Category", self.service.get_selectbox_values("category","product"))
        data, query = self.service.get_total_profit_per_product_category_per_year(selected_category)
        self.line_chart_bar_chart_and_table_content(data, 'calendar_year', 'total_profit','Year','Total Profit',query)

    def line_chart_bar_chart_and_table_content(self, data, x_column:str, y_column:str, x_label:str, y_label:str, query:str):
        col1, col2 = st.columns(2)
        with col1:
            st.code(query)
        with col2:
            st.dataframe(data, hide_index=True, use_container_width=True)

        col3, col4 = st.columns(2)
        with col3:
            self.line_chart(data, x_column, y_column, x_label, y_label)
        with col4:
            self.bar_chart(data, x_column, y_column, x_label, y_label)

    def line_chart(self, data, x_column: str, y_column: str, x_label: str, y_label: str):
        line_chart = alt.Chart(data).mark_line(point=True).encode(
            x=alt.X(f'{x_column}:O', title=x_label),
            y=alt.Y(y_column, title=y_label),
        ).properties(width=self.fig_size, height=self.fig_size)
        st.altair_chart(line_chart, use_container_width=True)

    def bar_chart(self, data, x_column: str, y_column: str, x_label: str, y_label: str):
        fig, ax = plt.subplots()
        color = "#0068C9"

        for value, subset in data.groupby(x_column):
            ax.bar(subset[x_column], subset[y_column], label=value, color=color)

        ax.set_xlabel(x_label)
        ax.set_ylabel(y_label)

        ax.set_xticks(sorted(data[x_column].unique()))
        st.pyplot(fig)

    # Victor
    def show_tables_content(self):
        st.header("Display data")

        df = self.service.retrive_all_data_from_all_tables()[1]
        branch = df["branch"]
        customer = df["customer"]
        date_dimension = df["date_dimension"]
        order_details = df["order_details"]
        order_fact = df["order_fact"]
        product = df["product"]

        col11, col12 = st.columns(2)
        with col11:
            st.markdown("#### :blue[branch]", unsafe_allow_html=False, help=None)
            st.dataframe(branch, hide_index=True, use_container_width=True)
        with col12:
            st.markdown("#### :blue[customer]", unsafe_allow_html=False, help=None)
            st.dataframe(customer, hide_index=True, use_container_width=True)

        col21, col22 = st.columns(2)
        with col21:
            st.markdown("#### :blue[date_dimension]", unsafe_allow_html=False, help=None)
            st.dataframe(date_dimension, hide_index=True, use_container_width=True)
        with col22:
            st.markdown("#### :blue[order_details]", unsafe_allow_html=False, help=None)
            st.dataframe(order_details, hide_index=True, use_container_width=True)

        col31, col32 = st.columns(2)
        with col31:
            st.markdown("#### :blue[order_fact]", unsafe_allow_html=False, help=None)
            st.dataframe(order_fact, hide_index=True, use_container_width=True)
        with col32:
            st.markdown("#### :blue[product]", unsafe_allow_html=False, help=None)
            st.dataframe(product, hide_index=True, use_container_width=True)

        st.header("Database Relationship")
        st.image('./images/db_relationship.png', caption='Database Relationship', width=510)

    def show_pagination_df(self, service_method):
        data,query = service_method
        st.code(query)
        pagination, pages, current_page, height = self.service.paginate_df(data)
        pagination.dataframe(data=pages[current_page - 1], height=height, use_container_width=True, hide_index=True)

    # Order Fact Quantity Grain
    def show_quantity_grain_content(self, title:str):
        st.header(title)
        self.show_pagination_df(self.service.get_quantity_grain_data())

    # Total Profit Per Product Category Per Branch Per Year
    def show_additive_fact_content(self, title: str):
        st.header(title)
        col1,col2 = st.columns(2)
        with col1:
            selected_category = st.selectbox("Select Category", self.service.get_selectbox_values("category","product"))
        with col2:
            selected_branch = st.selectbox("Select Branch", self.service.get_selectbox_values("branch_name","branch"))

        data,query = self.service.get_total_profit_per_product_category_per_branch_per_year(selected_category, selected_branch)

        col3, col4 = st.columns(2)
        with col3:
            st.code(query)
        with col4:
            st.dataframe(data, use_container_width=True, hide_index=True)

        col5, col6 = st.columns(2)
        with col5:
            self.line_chart(data, "Year","Total Profit","Year","Total Profit")
        with col6:
            self.bar_chart(data, "Year","Total Profit","Year","Total Profit")

    # Average Unit Price Per Product Per Year
    def show_non_additive_fact_content(self, title:str):
        st.header(title)
        selected_product = st.selectbox("Select Product", self.service.get_selectbox_values("product_name","product"))
        data, query = self.service.get_average_unit_price_per_product_per_year(selected_product)
        self.line_chart_bar_chart_and_table_content(data, 'calendar_year', 'average_unit_price','Year','Average Unit Price',query)

    def show_factless_fact_content(self, title: str):
        st.header(title)
        self.show_pagination_df(self.service.get_factless_fact_data())

    def show_snapshot_fact_content(self, title: str):
        st.header(title)
        st.write("This is the content for Snapshot Fact")

    def show_accumulation_fact_content(self, title: str):
        st.header(title)
        st.write("This is the content for Accumulation Fact")

    def show_date_dimension_content(self, title):
        st.header(title)
        self.show_pagination_df(self.service.get_date_dimension())

    def show_matrix_bus_content(self, title: str):
        st.header(title)
        st.write("This is the content for Matrix Bus")
