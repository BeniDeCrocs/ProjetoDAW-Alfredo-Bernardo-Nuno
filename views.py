from flask import render_template, request, redirect, url_for, current_app, jsonify
from passlib.hash import pbkdf2_sha256 as hasher
from flask_login import login_required, logout_user, login_user, current_user 
from user import get_user

def home_page():
    # 1. Se o utilizador NÃO estiver logado (visitante), envia slots vazios 
    # para não dar erro no HTML, mas o HTML vai mostrar o ecrã de Acesso Restrito.
    if not current_user.is_authenticated:
        return render_template("index.html", slots=None)

    # 2. Vamos buscar os servidores que este Hacker já tem na BD
    db = current_app.config["db"]
    servidores_bd = db.get_user_servers(current_user.username)

    # 3. Criamos a "grelha" base com 3 Slots (todos Livres inicialmente)
    slots = {
        1: {"status": "Livre", "tipo": None},
        2: {"status": "Livre", "tipo": None},
        3: {"status": "Livre", "tipo": None}
    }

    # 4. Verificamos a BD. Se ele já tiver construído algo no Slot 1, atualizamos a grelha.
    for s in servidores_bd:
        slot_id = s["slot_id"]
        if slot_id in slots:
            slots[slot_id] = {
                "status": "Ocupado",
                "tipo": s["tipo"]
            }

    # 5. Enviamos os slots configurados para o HTML os desenhar!
    return render_template("index.html", slots=slots)

def validate_register_form(form):
    form.data = {}
    form.errors = {}
    
    form_username = form.get("username", "").strip()
    if len(form_username) == 0:
        form.errors["username"] = "O Username não pode ser vazio."
    else:
        form.data["username"] = form_username
        
    form_password = form.get("password", "")
    if len(form_password) < 4: 
        form.errors["password"] = "A Password deve ter pelo menos 4 caracteres."
    else:
        form.data["password"] = form_password
        
    return len(form.errors) == 0

def register_page():
    if request.method == "GET":
        return render_template("registar.html", form=None)
    
    valid = validate_register_form(request.form)
    
    if not valid:
        return render_template("registar.html", form=request.form)
        
    username = request.form.data["username"]
    password = request.form.data["password"]
    
    hashed_pw = hasher.hash(password)
    
    db = current_app.config["db"]
    sucesso = db.add_user(username, hashed_pw)
    
    if sucesso:
        return redirect(url_for("login_page"))
    else:
        request.form.errors["username"] = "Este utilizador já existe no Cyber Breach!"
        return render_template("registar.html", form=request.form)

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
            remember = request.form.get("remember") == "yes"
            login_user(user, remember=remember)
            return redirect(url_for("home_page"))
            
    return render_template("login.html", form=request.form)

def logout_page():
    logout_user()
    return redirect(url_for("home_page"))

def validate_recover_form(form):
    form.data = {}
    form.errors = {}
    
    form_username = form.get("username", "").strip()
    if len(form_username) == 0:
        form.errors["username"] = "Username não pode ser vazio."
    else:
        form.data["username"] = form_username
        
    form_password = form.get("new_password", "")
    if len(form_password) < 4:
        form.errors["new_password"] = "A password deve ter pelo menos 4 caracteres."
    else:
        form.data["new_password"] = form_password
        
    form_confirm = form.get("confirm_password", "")
    if form_password != form_confirm:
        form.errors["confirm_password"] = "As palavras-passe não coincidem."
    
    return len(form.errors) == 0

def recover_page():
    if request.method == "GET":
        return render_template("recuperar.html", error=None)
    
    valid = validate_recover_form(request.form)
    
    if not valid:
        return render_template("recuperar.html", form=request.form, error=None)
    
    username = request.form.data["username"]
    new_password = request.form.data["new_password"]
    
    user = get_user(username)
    
    if not user:
        return render_template("recuperar.html", error="Utilizador não encontrado.", form=request.form)
    
    new_hashed_pw = hasher.hash(new_password)
    
    db = current_app.config["db"]
    sucesso = db.update_password(username, new_hashed_pw)
    
    if sucesso:
        return redirect(url_for("login_page"))
    else:
        return render_template("recuperar.html", error="Erro ao atualizar password. Tenta novamente.", form=request.form)

@login_required
def salvar_progresso():
    # 1. Receber os dados em formato JSON que o JS enviou
    dados_recebidos = request.get_json()
    
    if not dados_recebidos:
        return jsonify({"status": "erro", "mensagem": "Nenhum dado recebido"}), 400

    # 2. Extrair os valores
    novo_crypto = dados_recebidos.get("crypto", 0)
    novos_dados = dados_recebidos.get("dados", 0)

    # 3. Guardar na BD
    db = current_app.config["db"]
    sucesso = db.update_user_resources(current_user.username, novo_crypto, novos_dados)

    if sucesso:
        current_user.crypto = novo_crypto
        current_user.dados = novos_dados
        return jsonify({"status": "sucesso"})
    else:
        return jsonify({"status": "erro"}), 500