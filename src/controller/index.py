from flask import Blueprint, request, render_template
from src.model.classes import *
from src.config.colors import *

index = Blueprint('auth_index', __name__, template_folder='templates', static_folder='static')

@index.route('', methods= ['GET']) #methods=['GET', 'POST']
def index_page():
    return render_template('index.html')
    
@index.route('/api/login', methods= ['POST']) #methods=['GET', 'POST']
def login_page():
    print(yellow("[API]: ") + "POST request from api/login received")

    data = request.get_json() ; backend = Backend()
    return backend.user.login(data)
