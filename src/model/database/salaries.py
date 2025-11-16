import  uuid, calendar
from datetime import datetime
from src.config.colors import *

class DbSalary:

    def __init__(self, db):

        self.db = db
        self.conn = db.conn

    def create(self, date, value, description):
        try:
            cur = self.conn.cursor()
            salary_id = str(uuid.uuid4())
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            print(blue("[Database]: ") + "registering salary...")

            cur.execute(
                """INSERT INTO salary (salary_id, date, salary_value, description, created_at)
                    VALUES (%s, %s, %s, %s, %s)""",
                (salary_id, date, value, description, timestamp),
            )
            
            self.conn.commit()
            cur.close()

            print(green("[Database]: ") + "Salary registered successfully!")
            return True
        except Exception as e:
            print(red("[ERROR]: ") + f"Could not register salary: {e}")
            self.conn.rollback()
            return False
