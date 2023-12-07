import streamlit as st
import matplotlib.pyplot as plt
from db import Database
import pandas as pd


# Page Config
st.set_page_config(page_title="Gudang Data", page_icon="bar_chart", initial_sidebar_state="auto")

host = "localhost"
user = "root"
password = ""
database = "gd_uas"
mydb = Database(
    host=host,
    user=user,
    password=password,
    database=database
)


# TITLE HEADER
st.markdown("<h1 style='text-align: center;'>IBDA4011 - Gudang Data</h1>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align: center;'>1. Dominique Huang - 202000338</h3>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align: center;'>2. Stefannus Christian - 202000138</h3>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align: center;'>3. Victor Chendra - 202000338</h3>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align: center;'>4. Wira Yudha - 202000338</h3>", unsafe_allow_html=True)
st.divider()



st.subheader("No 01. Quantity (Grain) [Poin 1]")
st.subheader("No 02. Fact 1 per dimension 1, 2 [Poin 2]")
st.subheader("No 03. Derived Fact 1 per dimension 1, 2 [Poin 4]")
st.subheader("No 04. Additive fact 2 per dimension 1, 2, and 3 [Poin 7]")
st.subheader("No 05. Non additive fact per dimension 1 and 2 [Poin 8]")
st.subheader("No 06. Factless fact per dimension 1 and 2 [Poin 10]")
st.subheader("No 07. Date dimension table [Poin 11]")
st.subheader("No 08. Snapshot fact per dimension 1 and 2 [Poin 12]")
st.subheader("No 09. Accumulation fact per dimension 1 and 2  [Poin 13]")
