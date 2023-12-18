import mysql.connector
import os
import random
from datetime import datetime, timedelta
class Repository:
    def __init__(self, host="localhost", user="root", password="", database="gd_uas"):
        self.host = host
        self.user = user
        self.password = password
        self.database = database

        self.categories = [
                "Electronics",
                "Clothing",
                "Home & Garden",
                "Automotive",
                "Toys & Games",
                "Sports",
                "Books",
                "Beauty & Personal Care",
                "Health",
                "Computers",
                "Grocery",
                "Jewelry",
                "Movies",
                "Music",
                "Pet Supplies",
                "Tools & Home Improvement",
                "Office Products",
                "Baby",
                "Industrial & Scientific",
                "Arts & Crafts",
                "Collectibles",
                "Food & Drink",
                "Gourmet",
                "Luggage & Travel Gear",
                "Musical Instruments",
                "Software",
                "Shoes",
                "Watches",
                "Cell Phones & Accessories",
                "Cameras & Photography",
            ]

        self.num_of_order_fact_data_to_insert = 50
        self.num_of_products_to_insert = 20
        self.start_date = datetime(2020, 1, 1)
        self.end_date = datetime(2023, 12, 31)

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
            table_name = " ".join(table_name_sql.split('.sql')[0].split("_")[1:])
            try:
                print(f"Creating {table_name} table...")
                self.execute_sql_file(table_path)
                print(f"{table_name} table created successfully!\n")
            except Exception as e:
                print(f"{table_name} table creation failed!: {e}\n")

    def insert_dummy_datas(self, num_rows:int):
        dummy_data_path = "./sql/insertrows/"
        for table_name_sql in os.listdir(dummy_data_path):
            table_name = table_name_sql.split('.sql')[0]
            print(f"Inserting dummy datas to {table_name} dimension...")
            sql_path = dummy_data_path + table_name_sql
            self.execute_sql_file(sql_path)
            print(f"{table_name} dimension inserted successfully!\n")

        self.insert_product_dimension(self.num_of_products_to_insert)
        self.insert_ordered_dates_to_database(self.start_date, self.end_date)
        self.insert_order_data(num_rows)
        self.update_order_fact_total_amount()
        self.insert_factless_fact()
        self.insert_snapshot_fact()

    def insert_snapshot_fact(self):
        print(f'Inserting snapshot fact yearly_sales_snapshot fact...')
        all_branch_id = self.select_box_values("branch_id", "branch")

        snapshot_id = 1
        for branch_id in all_branch_id:
            # Query to get total_sales and profit
            result, query = self.get_total_sales_and_profit_for_snapshot_fact(branch_id)
            for row in result:
                # Creating date_id for 31 December of the current year
                date_id = int(str(row[0]) + "1231")
                total_sales = row[1]
                profit = row[2]

                # Inserting into yearly_sales_snapshot table
                self.execute_query(f"""
                    INSERT INTO yearly_sales_snapshot (snapshot_id, date_id, branch_id, total_sales, profit)
                    VALUES ({snapshot_id}, {date_id}, {branch_id}, {total_sales}, {profit});
                """)

                snapshot_id += 1

    def get_snapshot_query(self):
        query = """
                SELECT
                    yss.snapshot_id,
                    yss.date_id,
                    yss.branch_id,
                    yss.total_sales,
                    yss.profit,
                    b.branch_name
                FROM
                    yearly_sales_snapshot yss
                JOIN
                    branch b ON yss.branch_id = b.branch_id
                """
        result = self.execute_query(query)
        return result,query

    def get_total_sales_and_profit_for_snapshot_fact(self, branch_id):
        # Query to get total sales and profit for the specified branch and year
        query = f"""
            SELECT
                d.calendar_year,
                SUM(of.total_amount) AS total_sales,
                SUM(of.total_amount - (p.cost_price * od.quantity)) AS profit
            FROM order_fact of
            JOIN order_details od ON of.order_id = od.order_id
            JOIN product p ON od.product_id = p.product_id
            JOIN date_dimension d ON d.date_id = of.date_id
            WHERE of.branch_id = {branch_id}
            GROUP BY d.calendar_year;
        """

        result = self.execute_query(query)
        return result, query

    def insert_factless_fact(self):
        print(f'Inserting factless fact promotion fact...')
        branches = self.select_box_values("branch_id", "branch")
        try:
            for i in range(len(branches)):
                date_id = self.get_random_existing_id('date_dimension', 'date_id')

                query = f"""
                            INSERT INTO promotion_fact (promotion_id, date_id, branch_id)
                            VALUES ({i+1}, {date_id}, {branches[i]});
                        """
                self.execute_query(query)

            print(f"Successfully inserted rows into the 'promotion_fact' table.\n")

        except Exception as e:
            print(f"Error inserting promotion data: {str(e)}\n")

    def insert_product_dimension(self, num_rows: int):
        print(f'Inserting {num_rows} products to product table...')
        try:
            for product_id in range(1, num_rows + 1):
                product_name = f"Product Name {product_id}"
                category = random.choice(self.categories)
                price = round(random.uniform(10, 100), 2)
                cost_price = round(random.uniform(5, 50), 2)

                # Ensure price is higher than cost_price
                while price <= cost_price:
                    price = round(random.uniform(10, 100), 2)

                query = f"""
                        INSERT INTO product (product_id, product_name, category, price, cost_price)
                        VALUES ({product_id}, '{product_name}', '{category}', {price}, {cost_price});
                    """
                self.execute_query(query)

            print(f"Successfully inserted {num_rows} rows into the 'product' table.\n")

        except Exception as e:
            print(f"Error inserting product data: {str(e)}\n")

    def get_promotion_data(self):
        query = """
            SELECT
                pf.promotion_id,
                pf.date_id,
                b.branch_name
            FROM
                promotion_fact pf
                JOIN branch b ON b.branch_id = pf.branch_id
                ;
        """
        result = self.execute_query(query)
        return result, query

    def get_product_price(self, product_id):
        query = f"SELECT price FROM product WHERE product_id = {product_id};"
        result = self.execute_query(query)
        if result:
            return result[0][0]
        else:
            return 0

    def get_random_date(self, start_date, end_date):
        delta = end_date - start_date
        random_days = timedelta(days=random.randint(0, delta.days))
        return start_date + random_days

    def insert_order_data(self, num_rows: int):
        print(f"Inserting {num_rows} rows to order_facts...\n")
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

    # Fact Per Dimension 1 and 2 Repo
    def total_sales_amount_fact_per_branch_per_year_query(self, branch_name):
        query = f"""
                SELECT
                    b.branch_name,
                    d.calendar_year,
                    SUM(of.total_amount) AS total_sales_amount
                FROM order_fact of
                JOIN branch b ON of.branch_id = b.branch_id
                JOIN date_dimension d ON of.date_id = d.date_id
                WHERE b.branch_name = '{branch_name}'
                GROUP BY b.branch_name, d.calendar_year;
            """
        result = self.execute_query(query)
        return result,query

    def select_box_values(self, column_name: str, table_name: str) -> list[str]:
        query = f"SELECT DISTINCT {column_name} FROM {table_name};"
        result = self.execute_query(query)  # [(x1,), (x2,), ...]
        return [row[0] for row in result]  # Extract nested

    # Accumulation Fact Per Dimension 1 and 2 Repo
    def top_5_quantity_of_products_bought_per_customer_per_product_category(self, category: str):
        query = f"""
                SELECT
                    c.customer_name AS customer_name,
                    p.category AS category,
                    SUM(od.quantity) AS total_quantity_sold
                FROM
                    order_fact of
                JOIN
                    order_details od ON of.order_id = od.order_id
                JOIN
                    product p ON od.product_id = p.product_id
                JOIN
                    customer c ON of.customer_id = c.customer_id
                WHERE
                    p.category = '{category}'
                GROUP BY
                    customer_name, category
                ORDER BY
                    total_quantity_sold DESC
                LIMIT 5;
            """
        result = self.execute_query(query)
        return result,query

    # Factless Fact Per Dimension 1 and 2 Repo
    def list_of_customers_who_never_bought_a_product_per_branch(self, product: str, branch: str):
        query = f"""
            SELECT b.branch_name, d.full_date, p.product_name
            FROM branch b
            CROSS JOIN date_dimension d
            CROSS JOIN product p
            LEFT JOIN order_fact o ON b.branch_id = o.branch_id
                                AND d.date_id = o.date_id
            LEFT JOIN order_details od ON o.order_id = od.order_id
                                    AND p.product_id = od.product_id
            WHERE od.order_detail_id IS NULL;
        """

        result = self.execute_query(query)
        return result, query

    # Derived Fact Per Dimension 1 and 2 Repo
    def total_profit_per_product_category_per_year(self, category):
        query = f"""
            SELECT
                p.category,
                d.calendar_year,
                SUM(od.total_amount - (p.cost_price * od.quantity)) AS total_profit
            FROM order_details od
            JOIN order_fact of ON od.order_id = of.order_id
            JOIN product p ON od.product_id = p.product_id
            JOIN date_dimension d ON of.date_id = d.date_id
            WHERE p.category = '{category}'
            GROUP BY p.category, d.calendar_year;
        """ 
        result = self.execute_query(query)
        return result, query

    # Additive Fact Per Dimension 1,2 and 3 Repo
    def total_profit_per_product_category_per_branch_per_year(self, category, branch_name):
        query = f"""
            SELECT
                p.category,
                d.calendar_year,
                b.branch_name,
                SUM((of.total_amount - (p.cost_price * od.quantity))) AS total_profit
            FROM order_details od
            JOIN order_fact of ON od.order_id = of.order_id
            JOIN product p ON od.product_id = p.product_id
            JOIN branch b ON of.branch_id = b.branch_id
            JOIN date_dimension d ON of.date_id = d.date_id
            WHERE p.category = '{category}' AND b.branch_name = '{branch_name}'
            GROUP BY p.category, d.calendar_year, b.branch_name;
            """
        result = self.execute_query(query)
        return result, query

    # Non-Additive Fact Per Dimension 1 and 2 Repo
    def average_unit_price_per_product_per_year(self, product):
        query = f"""
            SELECT
                p.product_name,
                d.calendar_year,
                (SUM(od.total_amount) / SUM(od.quantity)) AS average_unit_price
            FROM
                order_details od
                JOIN order_fact of ON of.order_id = od.order_id
                JOIN product p ON od.product_id = p.product_id
                JOIN date_dimension d ON of.date_id = d.date_id

            WHERE p.product_name = '{product}'
            GROUP BY
                p.product_name, d.calendar_year;
        """

        result = self.execute_query(query)
        return result, query

    def average_units_sold_per_transaction_per_branch_per_year(self, branch):
        query = f"""
            SELECT
                b.branch_name,
                d.calendar_year,
                AVG(od.quantity) AS average_units_sold_per_transaction
            FROM
                order_details od
                JOIN order_fact of ON of.order_id = od.order_id
                JOIN date_dimension d ON of.date_id = d.date_id
                JOIN branch b ON b.branch_id = of.branch_id

            WHERE b.branch_name = '{branch}'
            GROUP BY
                b.branch_name, d.calendar_year;
        """

        result = self.execute_query(query)
        return result, query

    # Quantity (Grain) Repo
    def quantity_grain(self):
        query = """
            SELECT
                of.order_id,
                d.full_date,
                b.branch_name,
                c.customer_name,
                of.total_amount
            FROM order_fact of
            JOIN date_dimension d ON of.date_id = d.date_id
            JOIN branch b ON of.branch_id = b.branch_id
            JOIN customer c ON of.customer_id = c.customer_id
            ORDER BY d.full_date DESC;
        """
        result = self.execute_query(query)
        return result,query

    # Factless Fact Repo
    def factless_fact(self):
        query = """
            SELECT
                pf.promotion_id,
                pd.description AS promotion_description,
                pd.start_date,
                pd.end_date,
                pf.date_id,
                b.branch_name,
                p.product_name
            FROM promotion_fact pf
            JOIN branch b ON pf.branch_id = b.branch_id
            JOIN product p ON pf.product_id = p.product_id
            JOIN promotion_dimension pd ON pf.promotion_id = pd.promotion_id
            ORDER BY pf.date_id DESC;
        """
        result = self.execute_query(query)
        return result, query


    def select_all_from(self, table_name: str):
        """
        Sample output:
        [
            (x11, x12, x13, x14, x15, ...),
            (x21, x22, x23, x24, x25, ...),
            (x31, x32, x33, x34, x35, ...),
            ...
        ]
        """

        query = f"SELECT * FROM {table_name};"
        result = self.execute_query(query)
        return result, query

    #  Date Dimension Repo
    def date_dimension_query(self):
        query = """
            SELECT * FROM date_dimension;
        """
        result = self.execute_query(query)
        return result, query

    # Victor
    def get_all_table_names(self) -> list[str]:
        """
        Sample output:
        [table_name1, table_name2, table_name3, ...]
        """

        query = """
            SHOW TABLES;
        """
        fetched = self.execute_query(query)  # [(table1,), (table2,), ...]
        return [item[0] for item in fetched], query  # Extract nested

    # Victor
    def get_column_name(self, table_name: str, database: str="gd_uas") -> list[str]:
        """
        Sample output:
        [col_name1, col_name2, col_name3, ...]
        """

        column_query = f"""
            SELECT column_name
            FROM information_schema.columns
            WHERE table_schema='{database}'
            AND table_name='{table_name}';
        """
        fetched = self.execute_query(column_query)  # [(col_name1,), (col_name2,), ...]
        return [item[0] for item in fetched], column_query  # Extract nested

    def drop_tables(self):
        self.execute_query("SET foreign_key_checks = 0;")
        for table_name in self.get_all_table_names()[0]:
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
        self.insert_dummy_datas(self.num_of_order_fact_data_to_insert)

