import streamlit as st
import altair as alt
import pandas as pd
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
                    default_index=2,
                )

            if selected_option == "Display Data":
                self.title_header()
                self.show_tables_content()

            elif selected_option == "Quantity (Grain)":
                self.show_quantity_grain_content()

            elif selected_option == "Total Sales Fact":
                self.show_total_sales_fact_content()

            elif selected_option == "Derived Fact":
                self.show_derived_fact_content()

            elif selected_option == "Additive Fact":
                self.show_additive_fact_content()

            elif selected_option == "Non Additive Fact":
                self.show_non_additive_fact_content()

            elif selected_option == "Factless Fact":
                self.show_factless_fact_content()

            elif selected_option == "Snapshot Fact":
                self.show_snapshot_fact_content()

            elif selected_option == "Accumulation Fact":
                self.show_accumulation_fact_content()

            elif selected_option == "Date Dimension":
                self.show_date_dimension_content()

            elif selected_option == "Matrix Bus":
                self.show_matrix_bus_content()

        except AssertionError:
            st.error(f"Cannot Show Sidebar!  \nOptions Length ({options_length}) != Icons Length ({icons_length})")

    def show_total_sales_fact_content(self):
        filtered_data, fig,query = self.service.get_total_sales_amount_fact_per_branch_per_year()
        self.line_chart_bar_chart_and_table_content(filtered_data, fig, 'calendar_year', 'total_sales_amount','Year','Total Sales',query)

    def show_derived_fact_content(self):
        filtered_data, fig,query = self.service.get_total_profit_per_product_category_per_year()
        self.line_chart_bar_chart_and_table_content(filtered_data, fig, 'calendar_year', 'total_profit','Year','Total Profit',query)

    def line_chart_bar_chart_and_table_content(self, filtered_data, fig, x_column:str, y_column:str, x_label:str, y_label:str,query:str):
        col1, col2 = st.columns(2)
        with col1:
            st.code(query)
        with col2:
            st.dataframe(filtered_data, hide_index=True)

        col3, col4 = st.columns(2)
        with col3:
            line_chart = alt.Chart(filtered_data).mark_line(point=True).encode(
                x=alt.X(f'{x_column}:O', title=x_label),
                y=alt.Y(y_column, title=y_label),
            ).properties(width=self.fig_size, height=self.fig_size)
            st.altair_chart(line_chart, use_container_width=True)
        with col4:
            st.pyplot(fig)

    def show_tables_content(self):
        st.header("Display data")

        # p = self.db.get_all_table_names()
        a, b = self.service.retrive_all_data_from_all_tables_to_dataframe()
        # p = self.service.repo.retrive_all_data_from_all_tables_to_dataframe()["customer"]

        st.text(a)
        st.text(b)
        st.dataframe(pd.DataFrame(a, columns=b),hide_index=True)

        # st.text(type(p))

    def show_quantity_grain_content(self):
        st.header("Quality (Grain)")

    def show_additive_fact_content(self):
        st.write("This is the content for Additive Fact")

    def show_non_additive_fact_content(self):
        st.write("This is the content for Non Additive Fact")

    def show_factless_fact_content(self):
        st.write("This is the content for Factless Fact")

    def show_snapshot_fact_content(self):
        st.write("This is the content for Snapshot Fact")

    def show_accumulation_fact_content(self):
        st.write("This is the content for Accumulation Fact")

    def show_date_dimension_content(self):
        pagination,pages,current_page = self.service.get_date_dimension()
        pagination.dataframe(data=pages[current_page - 1], use_container_width=True)

    def show_matrix_bus_content(self):
        st.write("This is the content for Matrix Bus")
