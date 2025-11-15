import datetime, os


class Salary:

    def register():

        date = datetime.strptime(input("When you going to payed?(YYYY-MM-DD): "), "%Y-%m-%d") ; os.system("cls")
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        value = float(input("How much?: ")) ; os.system("cls")
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        times = int(input("How much times you want to replicate this payment?")) ; os.system("cls")

        return date, value, times