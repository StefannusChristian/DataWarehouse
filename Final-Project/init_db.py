from repo import Repository


host = "localhost"
user = "root"
password = ""
database = "gd_uas"

if __name__ == "__main__":
    repo = Repository(
    host=host,
    user=user,
    password=password,
    database=database
    )

    repo.initialize()
