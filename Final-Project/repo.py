import mysql.connector
import os
import random
import pandas as pd
from datetime import datetime, timedelta

class Repository:
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

        start_date = datetime(2021, 1, 1)
        end_date = datetime(2023, 12, 31)
        self.insert_ordered_dates_to_database(start_date, end_date)
        self.insert_order_data(num_rows)
        self.update_order_fact_total_amount()
        # self.insert_stock_fact_data(num_rows)

    def get_product_price(self, product_id):
        query = f"SELECT price FROM product WHERE product_id = {product_id};"
        result = self.execute_query(query)
        if result:
            return result[0][0]
        else:
            return 0

    def insert_order_data(self, num_orders: int):
        try:
            for order_id in range(1, num_orders + 1):
                date_id = self.get_random_existing_id('date_dimension', 'date_id')
                branch_id = self.get_random_existing_id('branch', 'branch_id')
                customer_id = self.get_random_existing_id('customer', 'customer_id')

                # Insert order into order_fact
                order_query = f"""
                    INSERT INTO order_fact (order_id, date_id, branch_id, customer_id)
                    VALUES ({order_id}, {date_id}, {branch_id}, {customer_id});
                """
                self.execute_query(order_query)

                # Insert random products into order_details for the current order
                num_products = random.randint(1, 50)
                for _ in range(num_products):
                    product_id = self.get_random_existing_id('product', 'product_id')
                    quantity = random.randint(1, 10)  # Assuming a maximum quantity of 10
                    product_price = self.get_product_price(product_id)

                    total_amount = quantity * product_price

                    # Insert product details into order_details
                    order_details_query = f"""
                        INSERT INTO order_details (order_id, product_id, quantity, total_amount)
                        VALUES ({order_id}, {product_id}, {quantity}, {total_amount});
                    """
                    self.execute_query(order_details_query)

            print("Dummy data inserted successfully.")
        except Exception as e:
            print(f"Error inserting dummy data: {e}")

    def update_order_fact_total_amount(self):
        try:
            # Calculate total_amount for each order and update order_fact
            update_query = """
                UPDATE order_fact of
                SET total_amount = (
                    SELECT SUM(od.total_amount)
                    FROM order_details od
                    WHERE od.order_id = of.order_id
                );
            """
            self.execute_query(update_query)

            print("Total Amount in order_fact updated successfully.")
        except Exception as e:
            print(f"Error updating total amount in order_fact: {e}")

    def execute_sql_file(self, file_path):
        try:
            with open(file_path, 'r') as sql_file:
                sql_script = sql_file.read()
                queries = sql_script.split(';')

                for query in queries:
                    if query.strip():
                        self.cursor.execute(query)
                self.commit()

                print(f"SQL script in {file_path} executed successfully.")

        except Exception as e:
            print(f"Error executing SQL script: {e}")

    def execute_query(self, query):
        self.cursor.execute(query)
        result = None

        if any(keyword in query.upper() for keyword in ["SELECT", "SHOW"]):
            result = self.cursor.fetchall()

        self.commit()
        return result

    def generate_ordered_dates(self, start_date, end_date):
        current_date = start_date
        date_list = []

        while current_date <= end_date:
            date_list.append(current_date)
            current_date += timedelta(days=1)

        return date_list

    def insert_ordered_dates_to_database(self, start_date, end_date):
        try:
            dates = self.generate_ordered_dates(start_date, end_date)

            for date in dates:
                calendar_month = date.strftime('%B')
                calendar_quarter = f'Q{((date.month - 1) // 3) + 1}'

                query = f"""
                INSERT INTO date_dimension (date_id, full_date, day_of_week, calendar_month, calendar_quarter, calendar_year)
                VALUES
                    ({date.strftime('%Y%m%d')}, '{date.strftime('%Y-%m-%d')}', '{date.strftime('%A')}', '{calendar_month}', '{calendar_quarter}', {date.year});
                """
                result = self.execute_query(query)

            print("Ordered dates inserted successfully.")
        except Exception as e:
            print(f"Error inserting ordered dates: {e}")

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

    def total_profit_per_branch_per_quarter_year(self):
        query = """
                SELECT
                    b.branch_name,
                    d.calendar_quarter,
                    SUM(od.quantity * (p.price - p.cost_price)) AS total_profit
                FROM order_fact of
                JOIN branch b ON of.branch_id = b.branch_id
                JOIN date_dimension d ON of.date_id = d.date_id
                JOIN order_details od ON of.order_id = od.order_id
                JOIN product p ON od.product_id = p.product_id
                GROUP BY b.branch_name, d.calendar_quarter;
                """
        result = self.execute_query(query)
        return result

    def get_date_dimension(self):
        query = """
                SELECT * FROM date_dimension;
                """
        result = self.execute_query(query)
        return result

    def get_all_table_names(self) -> list[str]:
        return [item[0] for item in self.execute_query("SHOW TABLES;")]

    def get_table_column_name(self, table_name: str, database: str = "gd_uas") -> list[str]:
        column_query = f"""
            SELECT column_name
            FROM information_schema.columns
            WHERE table_schema = '{database}'
            AND table_name = '{table_name}';
        """
        return [item[0] for item in self.execute_query(column_query)]

    def get_all_table_column_names(self) -> dict:
        table_names = self.get_all_table_names()
        result = {_: None for _ in table_names}

        for tname in table_names:
            result[tname] = self.get_table_column_name(tname)

        return result

    def retrive_all_data_from_all_tables(self) -> dict:
        table_names = self.get_all_table_names()
        result = {_: None for _ in table_names}

        for tname in table_names:
            query = f"SELECT * FROM {tname};"
            result[tname] = self.execute_query(query)

        return result

    def retrive_all_data_from_all_tables_to_dataframe(self) -> dict[pd.DataFrame]:
        table_names = self.get_all_table_names()
        column_names = self.get_all_table_column_names()
        result = self.retrive_all_data_from_all_tables()

        for tname in table_names:
            result[tname] = pd.DataFrame(result[tname], column_names[tname])

        return result

    def initialize(self):
        """
        NOTE:
        This function only execute it on `init_db.py`
        """

        self.create_tables()
        self.insert_dummy_datas(500)
