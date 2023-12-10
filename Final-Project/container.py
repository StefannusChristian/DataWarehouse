from repo import Repository
from service import Service
from ui import GUI
from init_db import host, user, password, database

class Container:
    def __init__(self):
        self.repo = self.create_repository()
        self.service = self.create_service()
        self.gui = self.create_ui()

    def create_repository(self):
        return Repository(
            host=host,
            user=user,
            password=password,
            database=database
            )

    def create_service(self):
        return Service(self.repo)

    def create_ui(self):
        return GUI(self.service)

    def run(self):
        self.gui