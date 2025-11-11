import dotenv, openpyxl, psycopg2, uuid, os
from datetime import timedelta
from pathlib import Path
from datetime import datetime
import calendar

class Db:

    def __init__(self):
        self.conn = self.connectDb()
        self.salary = self.Salary(self)

    class Salary:

        def __init__(self, db):
            # keep a reference to the parent Db and its connection
            self.db = db
            self.conn = db.conn

        def create(self):
            
            date = datetime.strptime(input("When you going to payed?(YYYY-MM-DD): "), "%Y-%m-%d") ; os.system("cls")

            value = float(input("How much?: ")) ; os.system("cls")

            times = int(input("How much times you want to replicate this payment?")) ; os.system("cls")

            cur = self.conn.cursor()
            def add_months(dt, months):
                month = dt.month - 1 + months
                year = dt.year + month // 12
                month = month % 12 + 1
                day = min(dt.day, calendar.monthrange(year, month)[1])
                return dt.replace(year=year, month=month, day=day)

            # preserve the original start date and compute each payment date from it
            start_date = date

            for i in range(times):
                current_date = add_months(start_date, i)
                user_id = str(uuid.uuid4())

                cur.execute(
                    """INSERT INTO salary (user_id, date, user_salary)
                       VALUES (%s, %s, %s)""",
                    (
                        user_id,
                        current_date.date() if isinstance(current_date, datetime) else current_date,
                        value,
                    ),
                )
            cur.close()
            self.conn.commit()

            print("\nBill registered successfuly!")

    def connectDb(self):
        
        env = self.read_env()
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

    def read_env(self, env_path=".env", override=True):

        dotenv.load_dotenv(dotenv_path=str(env_path), override=override)
        parsed = dotenv.dotenv_values(dotenv_path=str(env_path))
        result = {k: os.environ.get(k, v) for k, v in parsed.items() if k is not None}

        return result

        
db = Db()
db.salary.create()