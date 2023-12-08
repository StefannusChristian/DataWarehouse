from ui import GUI
from db import Database
from init_db import host, user, password, database


if __name__ == "__main__":
    mydatabase = Database(
        host=host,
        user=user,
        password=password,
        database=database
    )

    # NOTE:
    # EXECUTE `init_db.py` ONCE MANUALLY

    gui = GUI(mydatabase)
