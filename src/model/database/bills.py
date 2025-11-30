import uuid, calendar, datetime
from src.config.colors import *

class DbBill:

    def __init__(self, db):
        # keep a reference to the parent Db and its connection
        self.db = db
        self.conn = db.conn

    def create(self, debtor_id, name, date, value, installment, installment_value, remaining_installments, remaining, subscription, localization, coordinates, bank, place, type, credit = True):

        def add_months(dt, months):
            month = dt.month - 1 + months
            year = dt.year + month // 12
            month = month % 12 + 1
            day = min(dt.day, calendar.monthrange(year, month)[1])
            return dt.replace(year=year, month=month, day=day)

        # Parse and normalize date into a datetime object (support several formats)
        def parse_date(d):
            if isinstance(d, datetime.datetime):
                return d
            if isinstance(d, datetime.date):
                return datetime.datetime.combine(d, datetime.time())
            if isinstance(d, str):
                for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d", "%d/%m/%Y %H:%M:%S", "%d/%m/%Y"):
                    try:
                        return datetime.datetime.strptime(d, fmt)
                    except ValueError:
                        continue
            return datetime.datetime.now()

        try:
            cur = self.conn.cursor()

            # Sanitize inputs
            try:
                installment = int(installment)
            except Exception:
                installment = 1
            try:
                remaining_installments = int(remaining_installments)
            except Exception:
                remaining_installments = installment if installment > 0 else 1
            try:
                value = float(value)
            except Exception:
                value = 0.0

            base_date = parse_date(date)

            # Compute values once
            if subscription:
                per_installment_value = value
                total_value = value * (installment if installment > 0 else 1)
                remaining_total = total_value
            else:
                per_installment_value = (value / installment) if installment else value
                total_value = value
                remaining_total = total_value

            for i in range(installment):
                bill_id = str(uuid.uuid4())
                bill_date = base_date if installment <= 1 else add_months(base_date, i)

                timestamp = datetime.datetime.now()
                formatted_string = timestamp.strftime('%Y-%m-%d %H:%M:%S')

                print(blue("[Database]: ") + "registering bill...")

                cur.execute(
                    """INSERT INTO bills (bill_id, debtor_id, date, bill_name, value, installment, installment_value, remaining_installment, remaining, show, localization, bank, place, type, created_at, credit, coordinates)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                    (
                        bill_id,
                        debtor_id,
                        bill_date,
                        name,
                        total_value,
                        installment,
                        per_installment_value,
                        remaining_installments - i,
                        remaining_total - per_installment_value * i,
                        True,
                        localization,
                        bank,
                        place,
                        type,
                        formatted_string,
                        credit,
                        coordinates
                    ),
                )

                print(blue("[Database]: ") + "Bill registered successfuly!")

            self.conn.commit()
            cur.close()
            return True

        except Exception as e:
            print(red("[ERROR]: ") + f"Some error occurred was not possible complete the operation: {e}")
            try:
                self.conn.rollback()
            except Exception:
                pass
            try:
                cur.close()
            except Exception:
                pass
            return False

