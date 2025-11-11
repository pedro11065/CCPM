import  uuid, calendar
from datetime import datetime

class DbSalary:

    def __init__(self, db):

        self.db = db
        self.conn = db.conn

    def create(self, date, value, times):

        
        def add_months(dt, months):
            month = dt.month - 1 + months
            year = dt.year + month // 12
            month = month % 12 + 1
            day = min(dt.day, calendar.monthrange(year, month)[1])
            return dt.replace(year=year, month=month, day=day)

        start_date = date

        cur = self.conn.cursor()

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
