import streamlit as st
import pandas as pd
from streamlit_option_menu import option_menu
from service import Service

class GUI:
    def __init__(self, service: Service):
        self.service = service
        self.set_page_config()
        self.title_header()
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
        with st.sidebar:
            selected_option = option_menu(
                menu_title=None,
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
                ],
                icons = [
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
                ],
                menu_icon="cast",
                default_index=0,
            )

        if selected_option == "Display Data":
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


    def show_tables_content(self):
        st.header("Display data")

        # p = self.db.get_all_table_names()
        p = self.db.retrive_all_data_from_all_tables_to_dataframe()["customer"]

        st.dataframe(p)
        st.text(type(p))

    def show_quantity_grain_content(self):
        st.header("Quality (Grain)")

    def show_total_sales_fact_content(self):
        st.header("Total Sales Fact")
        st.subheader("Total Sales Amount per Branch per Quarter")
        filtered_data = self.service.get_total_sales_amount_fact_per_branch_per_quarter()
        st.line_chart(filtered_data.set_index("calendar_quarter")["total_sales_amount"])

    def show_derived_fact_content(self):
        st.header("Total Profit Fact")
        st.subheader("Total Profit Amount per Branch per Quarter")
        filtered_data = self.service.get_total_profit_amount_per_branch_per_quarter()
        st.line_chart(filtered_data.set_index("calendar_quarter")["total_profit"])

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
