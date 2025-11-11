import openpyxl

class DbTransport:

    def __init__(self, db):

        self.db = db
        self.conn = db.conn

    def create(self):


        wb = openpyxl.load_workbook(r'data\transports.xlsx')
        sheet = wb.active  

        cur = self.conn.cursor()

        for idx, row in enumerate(sheet.iter_rows(min_row=2, values_only=True), start=2):
            date, day_id, city_id, day_type_id, transport_cost, tax = row
            sql = """
                INSERT INTO transports (date, day_id, city_id, day_type_id, transport_cost, tax)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            cur.execute(sql, (date, day_id, city_id, day_type_id, transport_cost, tax))

        conn.commit()
        cur.close()
        conn.close()
        print("Done inserting all rows.")


