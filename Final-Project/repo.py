import mysql.connector
import os
import random
import time
from datetime import datetime, timedelta


class Repository:
    # host = "localhost" | "127.0.0.1"
    def __init__(self, host="localhost", user="root", password="", database="gd_uas"):
        self.host = host
        self.user = user
        self.password = password
        self.database = database

        self.dummy_rows_to_insert = 500
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
        print(F"Creating {self.database} Database...")
        try:
            temp_conn = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password
            )
            temp_cursor = temp_conn.cursor()

            temp_cursor.execute(f"CREATE DATABASE IF NOT EXISTS {self.database}")

            temp_cursor.close()
            temp_conn.close()

            print(f"{self.database} database created successfully!")

        except Exception as e:
            print(f"Error creating database {self.database}: {e}")

        print()

    def create_tables(self):
        create_table_path = "./sql/createtables/"
        for table_name_sql in os.listdir(create_table_path):
            table_path = create_table_path + table_name_sql
            table_name = table_name_sql.split('.sql')[0].split("_")[-1]
            print(f"Creating {table_name} table...")
            self.execute_sql_file(table_path)
            print(f"{table_name} table created successfully!\n")

    def insert_dummy_datas(self, num_rows:int):
        dummy_data_path = "./sql/insertrows/"
        for table_name_sql in os.listdir(dummy_data_path):
            table_name = table_name_sql.split('.sql')[0]
            print(f"Inserting dummy datas to {table_name} dimension...")
            sql_path = dummy_data_path + table_name_sql
            self.execute_sql_file(sql_path)
            print(f"{table_name} dimension inserted successfully!\n")

        start_date = datetime(2020, 1, 1)
        end_date = datetime(2023, 12, 31)
        self.insert_ordered_dates_to_database(start_date, end_date)
        self.insert_order_data(num_rows)
        self.update_order_fact_total_amount()

    def get_product_price(self, product_id):
        query = f"SELECT price FROM product WHERE product_id = {product_id};"
        result = self.execute_query(query)
        if result:
            return result[0][0]
        else:
            return 0

    def insert_order_data(self, num_rows: int):
        print(f"Inserting {num_rows} rows to order_facts...\n")
        time.sleep(2)
        try:
            for order_id in range(1, num_rows + 1):
                date_id = self.get_random_existing_id('date_dimension', 'date_id')
                branch_id = self.get_random_existing_id('branch', 'branch_id')
                customer_id = self.get_random_existing_id('customer', 'customer_id')

                order_query = f"""
                    INSERT INTO order_fact (order_id, date_id, branch_id, customer_id)
                    VALUES ({order_id}, {date_id}, {branch_id}, {customer_id});
                """
                self.execute_query(order_query)

                num_products = random.randint(1, 11)
                print(f"Inserting {num_products} products to order_details for order_id {order_id}...")

                for _ in range(num_products):
                    product_id = self.get_random_existing_id('product', 'product_id')
                    quantity = random.randint(1, 6)
                    print(f"Inserting {quantity} product_id {product_id}")
                    product_price = self.get_product_price(product_id)

                    total_amount = quantity * product_price

                    order_details_query = f"""
                        INSERT INTO order_details (order_id, product_id, quantity, total_amount)
                        VALUES ({order_id}, {product_id}, {quantity}, {total_amount});
                    """
                    self.execute_query(order_details_query)

                print(f"Inserting order_id {order_id} to order_details table successfull!\n")

            print("orders_facts and order_details data inserted successfully!\n")

        except Exception as e:
            print(f"Error inserting order data: {e}")

    def update_order_fact_total_amount(self):
        print("Updating total_amount column in order_facts table...")
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

        print()

    def execute_sql_file(self, file_path):
        try:
            with open(file_path, 'r') as sql_file:
                sql_script = sql_file.read()
                queries = sql_script.split(';')

                for query in queries:
                    if query.strip():
                        self.cursor.execute(query)
                self.commit()

        except Exception as e:
            print(f"Error executing SQL script: {e}\n")

    def execute_query(self, query):
        try:
            self.cursor.execute(query)
            result = None

            if any(keyword in query.upper() for keyword in ["SELECT", "SHOW"]):
                result = self.cursor.fetchall()

            self.commit()

            return result

        except Exception as e:
            print(f"Error executing query: {e}\n")

    def generate_ordered_dates(self, start_date, end_date):
        current_date = start_date
        date_list = []

        while current_date <= end_date:
            date_list.append(current_date)
            current_date += timedelta(days=1)

        return date_list

    def insert_ordered_dates_to_database(self, start_date, end_date):
        print(f'Inserting dummy datas to date dimension...')
        try:
            print(f"Inserting dates from {start_date.year} to {end_date.year}")
            dates = self.generate_ordered_dates(start_date, end_date)

            current_year = None  # To track the current year being processed

            for date in dates:
                # Check if the year has changed
                if current_year != date.year:
                    print(f"Inserting Dates for year {date.year}")
                    current_year = date.year

                calendar_month = date.strftime('%B')
                calendar_quarter = f'Q{((date.month - 1) // 3) + 1}'

                query = f"""
                INSERT INTO date_dimension (date_id, full_date, day_of_week, calendar_month, calendar_quarter, calendar_year)
                VALUES
                    ({date.strftime('%Y%m%d')}, '{date.strftime('%Y-%m-%d')}', '{date.strftime('%A')}', '{calendar_month}', '{calendar_quarter}', {date.year});
                """
                result = self.execute_query(query)

            print(f"Inserting dates from {start_date.year} to {end_date.year} successful!")

        except Exception as e:
            print(f"Error inserting dates: {e}")

        print()

    def get_random_existing_id(self, table_name:str, id_column:int):
        query = f"SELECT {id_column} FROM {table_name} ORDER BY RAND() LIMIT 1;"
        self.cursor.execute(query)
        result = self.cursor.fetchone()
        return result[0] if result else None

    # Fact Per Dimension 1 and 2
    def total_sales_amount_fact_per_branch_per_year_query(self):
        query = """
                SELECT
                    b.branch_name,
                    d.calendar_year,
                    SUM(of.total_amount) AS total_sales_amount
                FROM order_fact of
                JOIN branch b ON of.branch_id = b.branch_id
                JOIN date_dimension d ON of.date_id = d.date_id
                GROUP BY b.branch_name, d.calendar_year;
            """
        result = self.execute_query(query)
        return result,query

    # Derived Fact Per Dimension 1 and 2
    def total_profit_per_product_category_per_year(self):
        query = """
                SELECT
                    p.category,
                    d.calendar_year,
                    SUM(od.total_amount - (p.cost_price * od.quantity)) AS total_profit
                FROM order_details od
                JOIN order_fact of ON od.order_id = of.order_id
                JOIN product p ON od.product_id = p.product_id
                JOIN date_dimension d ON of.date_id = d.date_id
                GROUP BY p.category, d.calendar_year;
                """
        result = self.execute_query(query)
        return result,query

    # Additive Fact Per Dimension 1,2 and 3
    def total_profit_per_product_category_per_branch_per_year(self):
        query = """
                SELECT
                    p.category,
                    d.calendar_month,
                    b.branch_name,
                    SUM((of.total_amount - (p.cost_price * od.quantity))) AS total_profit
                FROM order_details od
                JOIN order_fact of ON od.order_id = of.order_id
                JOIN product p ON od.product_id = p.product_id
                JOIN branch b ON of.branch_id = b.branch_id
                JOIN date_dimension d ON of.date_id = d.date_id
                GROUP BY p.category, d.calendar_year, b.branch_name;
                """
        result = self.execute_query(query)
        return result,query

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

    def retrive_all_data_from_all_tables(self) -> dict:
        table_names = self.get_all_table_names()
        result = {_: None for _ in table_names}

        for tname in table_names:
            query = f"SELECT * FROM {tname};"
            result[tname] = self.execute_query(query)

        return result

    def drop_tables(self):
        self.execute_query("SET foreign_key_checks = 0;")
        for table_name in self.get_all_table_names():
            query = f"DROP TABLE IF EXISTS {table_name};"
            self.execute_query(query)

    def initialize(self):
        """
        NOTE:
        Only execute this function once on `init_db.py`
        """
        self.create_database()
        self.drop_tables()
        self.create_tables()
        self.insert_dummy_datas(self.dummy_rows_to_insert)
