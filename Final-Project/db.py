import mysql.connector
import os
import random
from datetime import datetime, timedelta

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

    def insert_dummy_datas(self):
        dummy_data_path = "./sql/insertrows/"
        for table_name_sql in os.listdir(dummy_data_path):
            sql_path = dummy_data_path + table_name_sql
            self.execute_sql_file(sql_path)
        self.insert_dates_to_database()

    def execute_sql_file(self, file_path):
        try:
            with open(file_path, 'r') as sql_file:
                sql_script = sql_file.read()
                # Split the script into individual queries
                queries = sql_script.split(';')

                # Execute each query
                for query in queries:
                    if query.strip():  # Skip empty queries
                        self.cursor.execute(query)

                # Commit changes after executing all queries
                self.commit()

                print(f"SQL script in {file_path} executed successfully.")

        except Exception as e:
            print(f"Error executing SQL script: {e}")


    def execute_query(self, query):
        self.cursor.execute(query)
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
                self.execute_query(query)

            print("Dates inserted successfully.")
        except Exception as e:
            print(f"Error inserting dates: {e}")


    def initialize(self):
        mydatabase.create_tables()
        mydatabase.insert_dummy_datas()


if __name__ == '__main__':
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

    mydatabase.initialize()

