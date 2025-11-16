from flask import Blueprint, request, render_template
from src.model.classes import *
from src.config.colors import *

credit = Blueprint('credit_api', __name__, template_folder='templates', static_folder='static')

@credit.route('/credit', methods= ['POST']) #methods=['GET', 'POST']
def credit_upload():
        
    print(yellow("[API]: ") + "POST request from api/credit received")

    data = request.get_json() ; backend = Backend()
    return backend.bill.credit(data)
