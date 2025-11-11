import dotenv, psycopg2, os
from src.model.db import *
from src.model.services import *

class Db:

    def __init__(self):

        self.conn = self.connectDb()

        self.dbDebtors = DbDebtors
        self.dbBill = DbBill
        self.dbSalary = DbSalary
        self.dbTransport = DbTransport


    def connectDb(self):
        
        env = self.readEnv()
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
        

    def readEnv(self, env_path=".env", override=True):

        dotenv.load_dotenv(dotenv_path=str(env_path), override=override)
        parsed = dotenv.dotenv_values(dotenv_path=str(env_path))
        result = {k: os.environ.get(k, v) for k, v in parsed.items() if k is not None}

        return result