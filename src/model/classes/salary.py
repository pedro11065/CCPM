import datetime, os, traceback
from flask import jsonify
from src.config.colors import *
from src.model.services.Qapp import reloadAppAsync


class Salary:

    def add(self, data):
        try:
            from src.model import Db
            db = Db()

            valor = data.get('valor')
            date = data.get('data')
            desc = data.get('desc')

            success = db.salary.create(date, valor, desc)

            if success:
                reloadAppAsync()
                print(cyan("[back-end]: ") + "Salary registered successfully!")
                return jsonify({'ok': True, 'message': 'Entrada adicionada com sucesso!'}), 201
            else:
                raise Exception("Database insertion failed")

        except Exception as e:
            print(red("[ERROR]: ") + f"Error adding salary: {str(e)}")
            traceback.print_exc()
            return jsonify({'ok': False, 'error': f'Erro ao adicionar entrada: {str(e)}'}), 500

    @staticmethod
    def register():

        date = datetime.datetime.strptime(input("When you going to payed?(YYYY-MM-DD): "), "%Y-%m-%d") ; os.system("cls")
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        value = float(input("How much?: ")) ; os.system("cls")
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        times = int(input("How much times you want to replicate this payment?")) ; os.system("cls")

        return date, value, times