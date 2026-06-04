import os
from flask import Flask
import views
from flask_login import LoginManager
from user import get_user  # Importa a função do ficheiro user.py do Lab 08
from models.database import Database  # Garanta que a vossa classe Database está na pasta models

#Configuração do Gestor
lm = LoginManager()

import os
from flask import Flask
import views
from flask_login import LoginManager
from user import get_user  
from models.database import Database  

#Configuração do Gestor
lm = LoginManager()

@lm.user_loader
def load_user(user_id):
    return get_user(user_id)


def create_app():
    app = Flask(__name__)
    app.config.from_object("settings")
    
    lm.init_app(app)
    lm.login_view = "login_page"  

    app.add_url_rule("/", view_func=views.home_page)
    app.add_url_rule("/registar", view_func=views.register_page, methods=["GET", "POST"])
    app.add_url_rule("/login", view_func=views.login_page, methods=["GET", "POST"])
    app.add_url_rule("/recuperar", view_func=views.recover_page, methods=["GET", "POST"])
    app.add_url_rule("/logout", view_func=views.logout_page)
    # Rota da Ponte Fantasma
    app.add_url_rule("/salvar-progresso", view_func=views.salvar_progresso, methods=["POST"])

    # INICIALIZAÇÃO DA BASE DE DADOS

    models_dir = os.path.dirname(os.path.abspath(__file__)) + "/models"
    db = Database(os.path.join(models_dir, "cyberbreach.sqlite"))
    db.create_user_table()
    app.config["db"] = db
    
    return app


# EXECUÇÃO DO SERVIDOR

if __name__ == "__main__":
    app = create_app()
    port = app.config.get("PORT", 8080)
    app.run(host="0.0.0.0", port=port)