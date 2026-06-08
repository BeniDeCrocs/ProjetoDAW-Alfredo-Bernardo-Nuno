import os
from flask import Flask
import views
from flask_login import LoginManager
from user import get_user  
from models.database import Database  

lm = LoginManager()

@lm.user_loader
def load_user(user_id):
    return get_user(user_id)

def create_app():
    app = Flask(__name__)
    app.config.from_object("settings")
    
    lm.init_app(app)
    lm.login_view = "login_page"  

    # Rotas base
    app.add_url_rule("/", view_func=views.home_page)
    app.add_url_rule("/registar", view_func=views.register_page, methods=["GET", "POST"])
    app.add_url_rule("/login", view_func=views.login_page, methods=["GET", "POST"])
    app.add_url_rule("/recuperar", view_func=views.recover_page, methods=["GET", "POST"])
    app.add_url_rule("/logout", view_func=views.logout_page)
    
    # Rotas do Jogo (APENAS UMA VEZ CADA!)
    app.add_url_rule("/salvar-progresso", view_func=views.salvar_progresso, methods=["POST"])
    app.add_url_rule("/comprar-estrutura", view_func=views.comprar_estrutura, methods=["POST"])
    app.add_url_rule("/vender-estrutura", view_func=views.vender_estrutura, methods=["POST"])
    app.add_url_rule("/evoluir-estrutura", view_func=views.evoluir_estrutura, methods=["POST"])

    # INICIALIZAÇÃO DA BASE DE DADOS
    models_dir = os.path.dirname(os.path.abspath(__file__)) + "/models"
    db = Database(os.path.join(models_dir, "cyberbreach.sqlite"))
    db.create_user_table()
    db.create_server_table()
    app.config["db"] = db
    
    return app

if __name__ == "__main__":
    app = create_app()
    port = app.config.get("PORT", 8080)
    app.run(host="0.0.0.0", port=port)