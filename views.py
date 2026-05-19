from flask import render_template, request, redirect, url_for, current_app
from passlib.hash import pbkdf2_sha256 as hasher
from flask_login import login_required, logout_user, login_user
from user import get_user

def validate_register_form(form):
    form.data = {}
    form.errors = {}
    
    form_username = form.get("username", "").strip()
    if len(form_username) == 0:
        form.errors["username"] = "O Username não pode ser vazio."
    else:
        form.data["username"] = form_username
        
    form_password = form.get("password", "")
    if len(form_password) < 4: # Pequena validação de segurança
        form.errors["password"] = "A Password deve ter pelo menos 4 caracteres."
    else:
        form.data["password"] = form_password
        
    return len(form.errors) == 0

def register_page():
    # Se for GET, mostra o formulário vazio [cite: 3563]
    if request.method == "GET":
        return render_template("register.html", form=None)
    
    # Se for POST, processa os dados [cite: 3564]
    valid = validate_register_form(request.form)
    
    if not valid:
        return render_template("register.html", form=request.form)
        
    username = request.form.data["username"]
    password = request.form.data["password"]
    
    # IMPORTANTE: Aplicar hashing antes de guardar! [cite: 3565]
    hashed_pw = hasher.hash(password)
    
    # Chamar a BD para gravar 
    db = current_app.config["db"]
    sucesso = db.add_user(username, hashed_pw)
    
    if sucesso:
        # Se correu bem, manda o utilizador para o Login para ele entrar
        return redirect(url_for("login_page"))
    else:
        # Se o utilizador já existir na BD
        request.form.errors["username"] = "Este utilizador já existe no Syndicate!"
        return render_template("register.html", form=request.form)


# Validação do formulário (Lab 08)
def validate_login_form(form):
    form.data = {}
    form.errors = {}
    
    form_username = form.get("username", "").strip()
    if len(form_username) == 0:
        form.errors["username"] = "Username não pode ser vazio."
    else:
        form.data["username"] = form_username
        
    form_password = form.get("password", "")
    if len(form_password) == 0:
        form.errors["password"] = "Password não pode ser vazia."
    else:
        form.data["password"] = form_password
        
    return len(form.errors) == 0

# Rota para o Ecrã de Login
def login_page():
    if request.method == "GET":
        return render_template("login.html", form=None)
        
    valid = validate_login_form(request.form)
    
    if not valid:
        return render_template("login.html", form=request.form)
        
    username = request.form.data["username"]
    user = get_user(username)
    
    if user is not None:
        password = request.form.data["password"]
        if hasher.verify(password, user.password):
            login_user(user)
            # Redireciona para o dashboard após login de sucesso!
            return redirect(url_for("home_page")) 
            
    return render_template("login.html", form=request.form)

# Rota para o Logout
def logout_page():
    logout_user()
    return redirect(url_for("home_page"))

# Rota temporária para o vosso dashboard (Página principal do jogo)
def home_page():
    return "<h1>Bem-vindo ao Dashboard Cyber-Syndicate!</h1>"

