from src.model.classes.bill import *
from src.model.classes.salary import *
from src.model.classes.user import *

class Backend:

    def __init__(self):
        self.bill=Bill()
        self.salary=Salary()
        self.user=User()