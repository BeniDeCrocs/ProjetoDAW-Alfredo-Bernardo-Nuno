from flask import current_app
from flask_login import UserMixin

class User(UserMixin):
    def __init__(self, username, password, crypto=0, dados=0):
        self.username = username
        self.password = password
        self.crypto = crypto
        self.dados = dados
        self.active = True
        self.is_admin = False
        
    def get_id(self):
        return self.username
        
    @property
    def is_active(self):
        return self.active

def get_user(user_id):
    if user_id == current_app.config["ADMIN_USERNAME"]:
        return User(
            user_id,
            current_app.config["ADMIN_PASSWORD"],
            crypto=200,
            dados=200
        )
        
    db = current_app.config["db"]
    user_data = db.get_user(user_id)
    if user_data:
        return User(
            user_data["username"],
            user_data["password"],
            crypto=user_data["crypto"],
            dados=user_data["dados"]
        )
    return None