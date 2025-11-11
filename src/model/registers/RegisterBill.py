import dotenv, openpyxl, psycopg2, uuid, os
from datetime import timedelta
from pathlib import Path
from datetime import datetime
import calendar

class Db:

    def __init__(self):
        self.conn = self.connectDb()
        self.bill = self.Bill(self)

    class Bill:

        def __init__(self, db):
            # keep a reference to the parent Db and its connection
            self.db = db
            self.conn = db.conn
            self.debtors = self.searchDebtors()

        
        def get_bill_info(self):

            for i, debtor in enumerate(self.debtors): print(f"{i+1} - {debtor[1]}")
            debtor = input("\nWho are you going to pay?: ") ; os.system("cls")
            debtor_id = self.debtors[int(debtor)-1][0] ; print(debtor) ; os.system("cls")
            debtor_limit = self.debtors[int(debtor)-1][2] ; print(debtor) ; os.system("cls")

            name = input("What you bought?: ") ; os.system("cls")

            date = datetime.strptime(input("Quando será o primeiro pagamento? (DD/MM/YYYY): "), "%d/%m/%Y"); os.system("cls")

            value = float(input("How much?: ")) ; os.system("cls")

            installment = int(input("How much installments?")) ; os.system("cls")

            subscription = input("Its a subscription?? (s/n): ").strip().lower()
            if subscription in ("s", "sim", "y", "yes"):
                subscription=True
            else:
                subscription=False

            installment_value = value/installment 

            remaining_installments = installment

            remaining = value

            self.create(debtor_id, name, date, value, installment, installment_value, remaining_installments, remaining, subscription)

        def create(self, debtor_id, name, date, value, installment, installment_value, remaining_installments, remaining, subscription):

            def add_months(dt, months):
                month = dt.month - 1 + months
                year = dt.year + month // 12
                month = month % 12 + 1
                day = min(dt.day, calendar.monthrange(year, month)[1])
                return dt.replace(year=year, month=month, day=day)
                      
            try:
                cur = self.conn.cursor()


                for i in range(installment):
                    bill_date = add_months(date, i)
                    bill_id = str(uuid.uuid4())
                    # ask once whether this is a subscription (assinatura)
                    if subscription:
                        # here `value` is treated as the per-installment amount
                        installment_value = value
                        value = value * installment  # store total value to keep DB consistent
                        remaining = value
                    else:
                        # non-subscription: keep existing behavior
                        installment_value = value / installment
                        remaining = value

                    print("Saving bill...")

                    cur.execute(
                        """INSERT INTO bills (bill_id, debtor_id, date, bill_name, value, installment, installment_value, remaining_installment, remaining, show)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                        (
                            bill_id,
                            debtor_id,
                            bill_date,
                            name,
                            value,
                            installment,
                            installment_value,
                            remaining_installments - i,
                            remaining - installment_value * i,
                            True,
                        ),
                    )

                    print("\nBill registered successfuly!")

                self.conn.commit()

                return True    
            except:            
                return False

            


        def searchDebtors(self):
            
        #Search all debtors

            cur = self.conn.cursor()

            cur.execute("SELECT debtor_id, debtor_name, debtor_limit FROM debtors")
            self.conn.commit() ; rows = cur.fetchall()
            cur.close()

            debtors = []

            for row in rows:
                debtors.append(row)

            return debtors


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


# db = Db()
# db.bill.get_bill_info()