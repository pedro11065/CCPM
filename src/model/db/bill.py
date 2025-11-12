import uuid, calendar

class DbBill:

    def __init__(self, db):
        # keep a reference to the parent Db and its connection
        self.db = db
        self.conn = db.conn

    

    def create(self, debtor_id, name, date, value, installment, installment_value, remaining_installments, remaining, subscription, localization, bank, place, type):

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
           
                if subscription:

                    installment_value = value
                    value = value * installment 
                    remaining = value
                else:
                
                    installment_value = value / installment
                    remaining = value

                print("Saving bill...")

                cur.execute(
                    """INSERT INTO bills (bill_id, debtor_id, date, bill_name, value, installment, installment_value, remaining_installment, remaining, show, localization, bank, place, type)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
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
                        localization, 
                        bank, 
                        place, 
                        type
                    ),
                )

                print("\nBill registered successfuly!")

            self.conn.commit()

            return True    
        except:            
            return False

        







# db = Db()
# db.bill.get_bill_info()