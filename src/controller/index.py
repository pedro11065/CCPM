from flask import Blueprint, request, render_template
from src.model.classes.bill import *
from src.config.colors import *

index = Blueprint('auth_index', __name__, template_folder='templates', static_folder='static')

@index.route('', methods= ['GET']) #methods=['GET', 'POST']
def index_page():
    return render_template('index.html')
    
@index.route('api/upload', methods= ['POST']) #methods=['GET', 'POST']
def index_upload():
    if request.method == 'POST':
        print(yellow("[API]: ") + "POST request from api/upload received")
        data = request.get_json()
        return analyseBill(data)
