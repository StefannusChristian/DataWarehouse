from ui import GUI
from db import Database
import streamlit as st


if __name__ == "__main__":
    host = "localhost"
    user = "root"
    password = ""
    database = "gd_uas"

    mydatabase = Database(
        host=host,
        user=user,
        password=password,
        database=database
    )

    # Create Tables and Insert Dummy Datas
    mydatabase.initialize()

    gui = GUI(mydatabase)

