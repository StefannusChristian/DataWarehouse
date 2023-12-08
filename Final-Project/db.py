import mysql.connector
import os
import random
from datetime import datetime, timedelta
import streamlit as st

class Database:
    def __init__(self, host: str, database: str, user: str="root", password: str=""):
        self.host = host
        self.user = user
        self.password = password
        self.database = database

        self.create_database()
        self.conn = self.connection()
        self.cursor = self.create_cursor()

    def connection(self):
        return mysql.connector.connect(
            host=self.host,
            user=self.user,
            password=self.password,
            database=self.database
        )

    def create_cursor(self):
        return self.conn.cursor()

    def close_connection(self):
        self.conn.close()

    def commit(self):
        self.conn.commit()

    def create_database(self):
        temp_conn = mysql.connector.connect(
            host=self.host,
            user=self.user,
            password=self.password
        )
        temp_cursor = temp_conn.cursor()

        temp_cursor.execute(f"CREATE DATABASE IF NOT EXISTS {self.database}")

        temp_cursor.close()
        temp_conn.close()

    def create_tables(self):
        create_table_path = "./sql/createtables/"
        for table_name_sql in os.listdir(create_table_path):
            table_path = create_table_path + table_name_sql
            self.execute_sql_file(table_path)

    def insert_dummy_datas(self, num_rows:int):
        dummy_data_path = "./sql/insertrows/"
        for table_name_sql in os.listdir(dummy_data_path):
            sql_path = dummy_data_path + table_name_sql
            self.execute_sql_file(sql_path)

        self.insert_dates_to_database()
        self.insert_stock_fact_data(num_rows)
        self.insert_order_fact_data(num_rows)

    def execute_sql_file(self, file_path):
        try:
            with open(file_path, 'r') as sql_file:
                sql_script = sql_file.read()
                queries = sql_script.split(';')

                for query in queries: self.cursor.execute(query)
                self.commit()

                print(f"SQL script in {file_path} executed successfully.")

        except Exception as e:
            print(f"Error executing SQL script: {e}")

    def insert_order_fact_data(self, num_rows: int):
        try:
            for i in range(num_rows):
                date_id = self.get_random_existing_id('date_dimension', 'date_id')
                branch_id = self.get_random_existing_id('branch', 'branch_id')
                customer_id = self.get_random_existing_id('customer', 'customer_id')
                product_id = self.get_random_existing_id('product', 'product_id')
                supplier_id = self.get_random_existing_id('supplier', 'supplier_id')

                quantity = random.randint(1, 50)
                total_amount = round(random.uniform(10.0, 200.0), 2)

                query = f"""
                INSERT INTO order_fact (order_id, date_id, branch_id, customer_id, product_id, supplier_id, quantity, total_amount)
                VALUES
                    ({i}, {date_id}, {branch_id}, {customer_id}, {product_id}, {supplier_id}, {quantity}, {total_amount});
                """
                result = self.execute_query(query)

            print("Order Fact data inserted successfully.")
        except Exception as e:
            print(f"Error inserting Order Fact data: {e}")

    def execute_query(self, query):
        self.cursor.execute(query)
        if "SELECT" in query.upper():
            result = self.cursor.fetchall()
            return result
        else:
            self.commit()

    def generate_random_dates(self, num_dates):
        start_date = datetime(2021, 1, 1)
        end_date = datetime(2023, 12, 31)
        date_list = [start_date + timedelta(days=random.randint(0, (end_date - start_date).days)) for _ in range(num_dates)]
        return date_list

    def insert_dates_to_database(self, num_dates:int=30):
        try:
            dates = self.generate_random_dates(num_dates)

            for date in dates:
                calendar_month = date.strftime('%B')
                calendar_quarter = f'Q{((date.month - 1) // 3) + 1}'

                query = f"""
                INSERT INTO date_dimension (date_id, full_date, day_of_week, calendar_month, calendar_quarter, calendar_year)
                VALUES
                    ({date.strftime('%Y%m%d')}, '{date.strftime('%Y-%m-%d')}', '{date.strftime('%A')}', '{calendar_month}', '{calendar_quarter}', {date.year});
                """
                result = self.execute_query(query)

            print("Dates inserted successfully.")
        except Exception as e:
            print(f"Error inserting dates: {e}")

    def get_random_existing_id(self, table_name:str, id_column:int):
        query = f"SELECT {id_column} FROM {table_name} ORDER BY RAND() LIMIT 1;"
        self.cursor.execute(query)
        result = self.cursor.fetchone()
        return result[0] if result else None

    def insert_stock_fact_data(self, num_rows: int):
        try:
            for i in range(num_rows):
                date_id = self.get_random_existing_id('date_dimension', 'date_id')
                branch_id = self.get_random_existing_id('branch', 'branch_id')
                product_id = self.get_random_existing_id('product', 'product_id')

                opening_stock = random.randint(1, 100)
                quantity_sold = random.randint(1, opening_stock)
                closing_stock = opening_stock - quantity_sold

                query = f"""
                INSERT INTO stock_fact (stock_id, date_id, branch_id, product_id, opening_stock, closing_stock, quantity_sold)
                VALUES
                    ({i}, {date_id}, {branch_id}, {product_id}, {opening_stock}, {closing_stock}, {quantity_sold});
                """
                result = self.execute_query(query)

            print("Stock Fact data inserted successfully.")
        except Exception as e:
            print(f"Error inserting Stock Fact data: {e}")

    def initialize(self):
        self.create_tables()
        self.insert_dummy_datas(500)

    def total_sales_amount_fact_per_branch_per_quarter_query(self):
        query = """
                SELECT
                    b.branch_name,
                    d.calendar_quarter,
                    SUM(of.total_amount) AS total_sales_amount
                FROM order_fact of
                JOIN branch b ON of.branch_id = b.branch_id
                JOIN date_dimension d ON of.date_id = d.date_id
                GROUP BY b.branch_name, d.calendar_quarter;
                """
        result = self.execute_query(query)
        return result
