from flask import render_template, request, redirect, url_for, current_app, jsonify
from passlib.hash import pbkdf2_sha256 as hasher
from flask_login import login_required, logout_user, login_user, current_user 
from user import get_user
import time
import sqlite3 as dbapi2

CONFIG_SOFTWARE = {
    "Trojan": {
        "custo_dados": 50, "custo_crypto": 0,
        "geracao_dados": 5, "geracao_crypto": 0, # +5 Dados/s
        "tempo_construcao": 10, # 10s de espera ao comprar
        "tempo_venda": 15
    },
    "Servidor": {
        "custo_dados": 150, "custo_crypto": 50,
        "geracao_dados": 10, "geracao_crypto": 2, # +10 Dados/s e +2 Crypto/s
        "tempo_construcao": 30, # 30s de espera ao comprar
        "tempo_venda": 45
    },
    "Fórum da Dark Web": {
        "custo_dados": 500, "custo_crypto": 200,
        "geracao_dados": 20, "geracao_crypto": 6, # +20 Dados/s e +6 Crypto/s
        "tempo_construcao": 60, # 60s de espera ao comprar
        "tempo_venda": 90
    }
}
TEMPO_COOLDOWN_VENDA = 30 # 30 segundos bloqueado para todos após vender

def home_page():
    if not current_user.is_authenticated:
        return render_template("index.html", slots={}, total_fps_dados=0, total_fps_crypto=0)
        
    db = current_app.config["db"]
    agora = int(time.time())
    
    # 1. Base Fixa: Os nomes aparecem sempre associados ao seu slot
    slots = {
        1: {"slot_id": 1, "tipo": "Trojan", "status": "Livre", "producao_d": 0, "producao_c": 0, "fim_tarefa": 0},
        2: {"slot_id": 2, "tipo": "Servidor", "status": "Livre", "producao_d": 0, "producao_c": 0, "fim_tarefa": 0},
        3: {"slot_id": 3, "tipo": "Fórum da Dark Web", "status": "Livre", "producao_d": 0, "producao_c": 0, "fim_tarefa": 0}
    }
    
    total_geracao_dados = 1 # O jogador ganha sempre +1 base
    total_geracao_crypto = 0
    
    try:
        with dbapi2.connect(db.dbfile) as connection:
            connection.row_factory = dbapi2.Row
            cursor = connection.cursor()
            
            cursor.execute("SELECT SLOT_ID, TIPO_SERVIDOR, STATUS, FIM_TAREFA FROM SERVIDORES WHERE USERNAME = ?", (current_user.username,))
            servidores_bd = cursor.fetchall()
            
            for s in servidores_bd:
                slot_id = s["SLOT_ID"]
                status = s["STATUS"]
                fim_tarefa = s["FIM_TAREFA"] or 0
                tipo = slots[slot_id]["tipo"] # Garante o nome correto
                
                # Auto-Resolvers: Verifica se os cronómetros já acabaram
                if status == "EmConstrucao" and agora >= fim_tarefa:
                    status = "Ativo"
                    fim_tarefa = 0
                    cursor.execute("UPDATE SERVIDORES SET STATUS = 'Ativo', FIM_TAREFA = 0 WHERE USERNAME = ? AND SLOT_ID = ?", (current_user.username, slot_id))
                    connection.commit()
                    
                elif status == "CooldownVenda" and agora >= fim_tarefa:
                    # Cooldown da venda acabou. Apaga da BD para voltar a ficar "Livre"
                    cursor.execute("DELETE FROM SERVIDORES WHERE USERNAME = ? AND SLOT_ID = ?", (current_user.username, slot_id))
                    connection.commit()
                    continue # Salta o resto para o slot ficar como "Livre" no HTML
                
                # Atualizar a interface com o estado real
                slots[slot_id]["status"] = status
                slots[slot_id]["fim_tarefa"] = fim_tarefa
                
                # Só soma à geração passiva se o software já estiver construído ("Ativo")
                if status == "Ativo":
                    config = CONFIG_SOFTWARE[tipo]
                    slots[slot_id]["producao_d"] = config["geracao_dados"]
                    slots[slot_id]["producao_c"] = config["geracao_crypto"]
                    total_geracao_dados += config["geracao_dados"]
                    total_geracao_crypto += config["geracao_crypto"]
                    
    except Exception as e:
        print(f"Erro ao carregar slots: {e}")
    
    return render_template(
        "index.html", 
        slots=slots,
        total_fps_dados=total_geracao_dados,
        total_fps_crypto=total_geracao_crypto,
        config=CONFIG_SOFTWARE
    )

@login_required
def comprar_estrutura():
    dados_recebidos = request.get_json() or {}
    slot_id = int(dados_recebidos.get("slot_id", 0))
    
    mapeamento_slots = {1: "Trojan", 2: "Servidor", 3: "Fórum da Dark Web"}
    
    if slot_id not in mapeamento_slots:
        return jsonify({"status": "erro", "mensagem": "Slot inválido."}), 400
        
    tipo_software = mapeamento_slots[slot_id]
    config = CONFIG_SOFTWARE[tipo_software]
    
    if current_user.dados < config["custo_dados"] or current_user.crypto < config["custo_crypto"]:
        return jsonify({"status": "erro", "mensagem": "Recursos insuficientes!"}), 400
        
    db = current_app.config["db"]
    agora = int(time.time())
    fim_construcao = agora + config["tempo_construcao"]
    
    novo_dados = current_user.dados - config["custo_dados"]
    novo_crypto = current_user.crypto - config["custo_crypto"]
    
    try:
        with dbapi2.connect(db.dbfile) as connection:
            cursor = connection.cursor()
            
            # Verifica se já há algo neste slot
            cursor.execute("SELECT STATUS FROM SERVIDORES WHERE USERNAME = ? AND SLOT_ID = ?", (current_user.username, slot_id))
            if cursor.fetchone():
                return jsonify({"status": "erro", "mensagem": "O slot não está livre."}), 400
            
            cursor.execute("UPDATE USER SET DADOS = ?, CRYPTO = ? WHERE USERNAME = ?", (novo_dados, novo_crypto, current_user.username))
            
            # Instala o software mas com estado 'EmConstrucao'
            cursor.execute(
                "INSERT INTO SERVIDORES (USERNAME, SLOT_ID, TIPO_SERVIDOR, STATUS, FIM_TAREFA) VALUES (?, ?, ?, 'EmConstrucao', ?)",
                (current_user.username, slot_id, tipo_software, fim_construcao)
            )
            connection.commit()
            
            current_user.dados = novo_dados
            current_user.crypto = novo_crypto
            
        return jsonify({"status": "sucesso", "mensagem": f"A instalar {tipo_software}..."})
    except Exception as e:
        print(f"Erro ao comprar: {e}")
        return jsonify({"status": "erro", "mensagem": "Erro interno."}), 500

@login_required
def vender_estrutura():
    dados_recebidos = request.get_json() or {}
    slot_id = int(dados_recebidos.get("slot_id", 0))
    
    # Descobrir qual é o software deste slot para saber o tempo de cooldown
    mapeamento_slots = {1: "Trojan", 2: "Servidor", 3: "Fórum da Dark Web"}
    if slot_id not in mapeamento_slots:
        return jsonify({"status": "erro", "mensagem": "Slot inválido."}), 400
        
    tipo_software = mapeamento_slots[slot_id]
    tempo_de_espera = CONFIG_SOFTWARE[tipo_software]["tempo_venda"]
    
    db = current_app.config["db"]
    agora = int(time.time())
    fim_cooldown = agora + tempo_de_espera
    
    try:
        with dbapi2.connect(db.dbfile) as connection:
            cursor = connection.cursor()
            
            # Muda o estado para CooldownVenda
            cursor.execute(
                "UPDATE SERVIDORES SET STATUS = 'CooldownVenda', FIM_TAREFA = ? WHERE USERNAME = ? AND SLOT_ID = ?",
                (fim_cooldown, current_user.username, slot_id)
            )
            if cursor.rowcount == 0:
                return jsonify({"status": "erro", "mensagem": "Nenhuma estrutura para vender neste slot."}), 400
                
            connection.commit()
            
        return jsonify({"status": "sucesso", "mensagem": f"{tipo_software} vendido! O slot entra em manutenção."})
    except Exception as e:
        print(f"Erro ao vender: {e}")
        return jsonify({"status": "erro", "mensagem": "Erro interno."}), 500

@login_required
def salvar_progresso():
    dados_recebidos = request.get_json()
    if not dados_recebidos: return jsonify({"status": "erro"}), 400

    novo_crypto = dados_recebidos.get("crypto", 0)
    novos_dados = dados_recebidos.get("dados", 0)

    db = current_app.config["db"]
    sucesso = db.update_user_resources(current_user.username, novo_crypto, novos_dados)

    if sucesso:
        current_user.crypto = novo_crypto
        current_user.dados = novos_dados
        return jsonify({"status": "sucesso"})
    return jsonify({"status": "erro"}), 500

# ==========================================================
# Funções de Login / Registo Mantidas Iguais
# ==========================================================
def validate_register_form(form):
    form.data = {}
    form.errors = {}
    form_username = form.get("username", "").strip()
    if len(form_username) == 0: form.errors["username"] = "O Username não pode ser vazio."
    else: form.data["username"] = form_username
    form_password = form.get("password", "")
    if len(form_password) < 4: form.errors["password"] = "A Password deve ter pelo menos 4 caracteres."
    else: form.data["password"] = form_password
    return len(form.errors) == 0

def register_page():
    if request.method == "GET": return render_template("registar.html", form=None)
    valid = validate_register_form(request.form)
    if not valid: return render_template("registar.html", form=request.form)
    username = request.form.data["username"]
    password = request.form.data["password"]
    hashed_pw = hasher.hash(password)
    db = current_app.config["db"]
    sucesso = db.add_user(username, hashed_pw)
    if sucesso: return redirect(url_for("login_page"))
    else:
        request.form.errors["username"] = "Este utilizador já existe no Cyber Breach!"
        return render_template("registar.html", form=request.form)

def validate_login_form(form):
    form.data = {}
    form.errors = {}
    form_username = form.get("username", "").strip()
    if len(form_username) == 0: form.errors["username"] = "Username não pode ser vazio."
    else: form.data["username"] = form_username
    form_password = form.get("password", "")
    if len(form_password) == 0: form.errors["password"] = "Password não pode ser vazia."
    else: form.data["password"] = form_password
    return len(form.errors) == 0

def login_page():
    if request.method == "GET": return render_template("login.html", form=None)
    valid = validate_login_form(request.form)
    if not valid: return render_template("login.html", form=request.form)
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
    if len(form_username) == 0: form.errors["username"] = "Username não pode ser vazio."
    else: form.data["username"] = form_username
    form_password = form.get("new_password", "")
    if len(form_password) < 4: form.errors["new_password"] = "A password deve ter pelo menos 4 caracteres."
    else: form.data["new_password"] = form_password
    form_confirm = form.get("confirm_password", "")
    if form_password != form_confirm: form.errors["confirm_password"] = "As palavras-passe não coincidem."
    return len(form.errors) == 0

def recover_page():
    if request.method == "GET": return render_template("recuperar.html", error=None)
    valid = validate_recover_form(request.form)
    if not valid: return render_template("recuperar.html", form=request.form, error=None)
    username = request.form.data["username"]
    new_password = request.form.data["new_password"]
    user = get_user(username)
    if not user: return render_template("recuperar.html", error="Utilizador não encontrado.", form=request.form)
    new_hashed_pw = hasher.hash(new_password)
    db = current_app.config["db"]
    sucesso = db.update_password(username, new_hashed_pw)
    if sucesso: return redirect(url_for("login_page"))
    else: return render_template("recuperar.html", error="Erro ao atualizar password. Tenta novamente.", form=request.form)