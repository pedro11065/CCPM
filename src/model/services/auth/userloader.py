from src.model.db.DbController import Db
from src.model.classes.user import User

def load_user(user_id):
    db = Db()
    user_data = db.users.search.by_id(user_id)
    if user_data:
        return user_data
    return None
