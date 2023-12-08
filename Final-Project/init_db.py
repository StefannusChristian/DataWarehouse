from db import Database


host = "localhost"
user = "root"
password = ""
database = "gd_uas"


if __name__ == "__main__":
    mydatabase = Database(
        host=host,
        user=user,
        password=password,
        database=database
    )

    mydatabase.initialize()
