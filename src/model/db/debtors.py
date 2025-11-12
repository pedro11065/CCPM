class DbDebtors:

    def __init__(self, db):
        # keep a reference to the parent Db and its connection
        self.db = db
        self.conn = db.conn

    def search(self):

        cur = self.conn.cursor()

        cur.execute("SELECT debtor_id, debtor_name, debtor_limit FROM debtors")
        self.conn.commit() ; rows = cur.fetchall()
        cur.close()

        debtors = []

        for row in rows:
            debtors.append(row)

        return debtors