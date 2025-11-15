from flask import Blueprint, request, render_template
from src.model.classes import *
from src.config.colors import *

debit = Blueprint('debit_api', __name__, template_folder='templates', static_folder='static')

@debit.route('/debit', methods= ['POST']) #methods=['GET', 'POST']
def debit_upload():
        
    print(yellow("[API]: ") + "POST request from api/upload received")

    data = request.get_json() ; backend = Backend()
    return backend.bill.debit(data)
