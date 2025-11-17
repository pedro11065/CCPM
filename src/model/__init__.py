from src.model.services.auth.readEnv import *
from src.model.database import *
from src.model.classes import *

import psycopg2

class Db:

    def __init__(self):

        self.conn = self.connectDb()

        # Instantiate helpers with a reference to this Db instance
        self.dbDebtors = DbDebtors(self)
        self.dbBill = DbBill(self)
        self.dbSalary = DbSalary(self)
        self.dbTransport = DbTransport(self)

        # Short aliases (optional, for convenient access)
        self.debtors = self.dbDebtors
        self.bill = self.dbBill
        self.salary = self.dbSalary
        self.transport = self.dbTransport


    def connectDb(self):
        
        env = readEnv()
        try:
            conn = psycopg2.connect(
            host=env.get("PGHOST", "localhost"),
            database=env.get("PGDATABASE", "mydatabase"),
            user=env.get("PGUSER", "myuser"),
            password=env.get("PGPASSWORD", "mypass"),
            port=int(env.get("PGPORT", 5432))
            )
            return conn
        except Exception:
            raise
        