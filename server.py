import os
from flask import Flask
import views
from flask_login import LoginManager
from user import get_user  # Importa a função do ficheiro user.py do Lab 08
from models.database import Database  # Garanta que a vossa classe Database está na pasta models

#Configuração do Gestor
lm = LoginManager()

@lm.user_loader
def load_user(user_id):
    # Esta função diz ao Flask-Login como ir buscar o utilizador à BD pelo ID/Username
    return get_user(user_id)


def create_app():
    # Instanciação da aplicação Flask (Lab 07)
    app = Flask(__name__)
    
    # Definição de configurações de execução a partir do settings.py (Lab 07)
    app.config.from_object("settings")
    
    # Inicialização do gestor de autenticação na app (Lab 08)
    lm.init_app(app)
    lm.login_view = "login_page"  # Se alguém tentar entrar numa página protegida, é mandado para aqui

    app.add_url_rule("/home", view_func=views.home_page)
    
    # ==========================================
    # 3. DEFINIÇÃO DAS ROTAS (ROUTES)
    # ==========================================
    # Rota para a página principal / Dashboard (Lab 07)
    app.add_url_rule("/", view_func=views.home_page)
    
    # Rotas obrigatórias para o Login e Logout (Lab 08)
    app.add_url_rule("/registar", view_func=views.register_page, methods=["GET", "POST"])
    app.add_url_rule("/login", view_func=views.login_page, methods=["GET", "POST"])
    app.add_url_rule("/recuperar", view_func=views.recover_page, methods=["GET", "POST"])
    app.add_url_rule("/logout", view_func=views.logout_page)
    app.add_url_rule("/", view_func=views.home_page)
    
    # Se quiserem adicionar a rota do ecrã de registo (Desafio do Lab 08)
    # app.add_url_rule("/registar", view_func=views.register_page, methods=["GET", "POST"])

    # ==========================================
    # 4. INICIALIZAÇÃO DA BASE DE DADOS (Lab 07)
    # ==========================================
    # Descobre o caminho para a vossa pasta 'models' e liga ao ficheiro SQLite
    models_dir = os.path.dirname(os.path.abspath(__file__)) + "/models"
    db = Database(os.path.join(models_dir, "movies.sqlite"))
    db.create_user_table()
    app.config["db"] = db
    
    return app

# ==========================================
# 5. EXECUÇÃO DO SERVIDOR
# ==========================================
if __name__ == "__main__":
    app = create_app()
    # VAI BUSCAR A PORTA DEFINIDA NO SETTINGS.PY (Lab 07)
    port = app.config.get("PORT", 8080)
    app.run(host="0.0.0.0", port=port)