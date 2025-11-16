from flask import Blueprint, request
from src.model.classes import Backend
from src.config.colors import yellow

salary = Blueprint('salary_api', __name__)

@salary.route('/salary', methods=['POST'])
def salary_add():
    print(yellow("[API]: ") + "POST request from api/salary received")
    data = request.get_json()
    backend = Backend()
    return backend.salary.add(data)
