from flask import render_template, request, redirect, url_for, current_app, jsonify
from passlib.hash import pbkdf2_sha256 as hasher
from flask_login import login_required, logout_user, login_user, current_user 
from user import get_user
import time

# Configuração de Equilíbrio das Construções (Tempos em segundos)
CONFIG_SOFTWARE = {
    "Trojan": {
        "custo_dados": 50, "custo_crypto": 0,
        "geracao_dados": 1, "geracao_crypto": 0 # +1 Dado por segundo
    },
    "Servidor": {
        "custo_dados": 150, "custo_crypto": 50,
        "geracao_dados": 5, "geracao_crypto": 1 # +5 Dados e +1 Cripto por segundo
    },
    "Fórum da Dark Web": {
        "custo_dados": 500, "custo_crypto": 200,
        "geracao_dados": 20, "geracao_crypto": 5 # +20 Dados e +5 Cripto por segundo
    }
}

@login_required
def home_page():
    db = current_app.config["db"]
    import sqlite3 as dbapi2
    
    # Mapeamento fixo: cada slot tem um software específico
    mapeamento_software_por_slot = {
        1: "Trojan",
        2: "Servidor",
        3: "Fórum da Dark Web"
    }
    
    # Configuração dos slots (estado inicial)
    slots = {
        1: {"slot_id": 1, "tipo": "Slot Vazio", "status": "Livre", "producao_d": 0, "producao_c": 0, "fim_tarefa": 0},
        2: {"slot_id": 2, "tipo": "Slot Vazio", "status": "Livre", "producao_d": 0, "producao_c": 0, "fim_tarefa": 0},
        3: {"slot_id": 3, "tipo": "Slot Vazio", "status": "Livre", "producao_d": 0, "producao_c": 0, "fim_tarefa": 0}
    }
    
    total_geracao_dados = 1
    total_geracao_crypto = 0
    
    try:
        with dbapi2.connect(db.dbfile) as connection:
            connection.row_factory = dbapi2.Row
            cursor = connection.cursor()
            
            # Buscar servidores do utilizador
            cursor.execute("SELECT SLOT_ID, TIPO_SERVIDOR, STATUS, FIM_TAREFA FROM SERVIDORES WHERE USERNAME = ?", (current_user.username,))
            servidores_bd = cursor.fetchall()
            
            for s in servidores_bd:
                slot_id = s["SLOT_ID"]
                tipo_software = s["TIPO_SERVIDOR"]
                status = s["STATUS"]
                fim_tarefa = s["FIM_TAREFA"] or 0
                
                if slot_id in slots:
                    config = CONFIG_SOFTWARE.get(tipo_software, {})
                    slots[slot_id] = {
                        "slot_id": slot_id,
                        "tipo": tipo_software,  # Nome do software (Trojan, Servidor, etc.)
                        "status": status,
                        "fim_tarefa": fim_tarefa,
                        "producao_d": config.get("geracao_dados", 0),
                        "producao_c": config.get("geracao_crypto", 0)
                    }
                    total_geracao_dados += config.get("geracao_dados", 0)
                    total_geracao_crypto += config.get("geracao_crypto", 0)
                    
    except Exception as e:
        print(f"Erro ao carregar slots: {e}")
    
    return render_template(
        "index.html", 
        slots=slots,
        total_fps_dados=total_geracao_dados,
        total_fps_crypto=total_geracao_crypto
    )

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
    
@login_required
def construir():
    dados_json = request.get_json() or {}
    slot_id = int(dados_json.get("slot_id", 0))
    tipo = dados_json.get("tipo")

    if tipo not in CONFIG_SOFTWARE:
        return jsonify({"status": "erro", "mensagem": "Estrutura inválida"}), 400

    config = CONFIG_SOFTWARE[tipo]
    db = current_app.config["db"]
    user_data = db.get_user(current_user.username)

    # Validar recursos no Servidor (Segurança obrigatória do guião!)
    if user_data["dados"] < config["custo_dados"] or user_data["crypto"] < config["custo_crypto"]:
        return jsonify({"status": "erro", "mensagem": "Recursos insuficientes!"}), 400

    # Deduzir custos e atualizar utilizador
    novos_dados = user_data["dados"] - config["custo_dados"]
    novo_crypto = user_data["crypto"] - config["custo_crypto"]
    db.update_user_resources(current_user.username, novo_crypto, novos_dados)

    # Calcular quando termina a construção
    fim_construcao = int(time.time()) + config["tempo_construcao"]
    db.insert_server(current_user.username, slot_id, tipo, "A construir", fim_construcao)

    return jsonify({
        "status": "sucesso",
        "dados": novos_dados,
        "crypto": novo_crypto,
        "fim_tarefa": fim_construcao
    })

@login_required
def iniciar_tarefa():
    dados_json = request.get_json() or {}
    slot_id = int(dados_json.get("slot_id", 0))

    db = current_app.config["db"]
    servidores = db.get_user_servers(current_user.username)
    servidor = next((s for s in servidores if s["slot_id"] == slot_id), None)

    if not servidor or servidor["status"] != "Parado":
        return jsonify({"status": "erro", "mensagem": "Servidor não está pronto"}), 400

    config = CONFIG_SOFTWARE[servidor["tipo"]]
    fim_tarefa = int(time.time()) + config["tempo_tarefa"]
    
    db.update_server_status(current_user.username, slot_id, "Em Tarefa", fim_tarefa)
    return jsonify({"status": "sucesso", "fim_tarefa": fim_tarefa})

@login_required
def receber_recompensa():
    dados_recebidos = request.get_json() or {}
    slot_id = int(dados_recebidos.get("slot_id", 0))
    
    db = current_app.config["db"]
    import sqlite3 as dbapi2
    
    agora = int(time.time())
    
    try:
        with dbapi2.connect(db.dbfile) as connection:
            connection.row_factory = dbapi2.Row  # Permite aceder aos campos por nome
            cursor = connection.cursor()
            cursor.execute(
                "SELECT TIPO_SERVIDOR, STATUS, FIM_TAREFA FROM SERVIDORES WHERE USERNAME = ? AND SLOT_ID = ?", 
                (current_user.username, slot_id)
            )
            row = cursor.fetchone()
            
            if not row:
                return jsonify({"status": "erro", "mensagem": "Nenhuma estrutura ativa neste slot."}), 400
                
            tipo_software = row["TIPO_SERVIDOR"]
            status = row["STATUS"]
            fim_tarefa = int(row["FIM_TAREFA"]) if row["FIM_TAREFA"] else 0
            
            # Ajuste de segurança caso o nome venha ligeiramente diferente do dicionário
            if tipo_software == "Fórum Dark Web" and "Fórum da Dark Web" in CONFIG_SOFTWARE:
                tipo_software = "Fórum da Dark Web"

            # Validar se o tipo de software existe na configuração
            if tipo_software not in CONFIG_SOFTWARE:
                return jsonify({"status": "erro", "mensagem": f"Software '{tipo_software}' inválido."}), 400
                
            config = CONFIG_SOFTWARE[tipo_software]
            
            # Proteção contra cheats de tempo
            if status == "EmConstrucao" and agora < fim_tarefa:
                return jsonify({"status": "erro", "mensagem": "A instalação ainda não acabou!"}), 400
            if status == "Cooldown":
                return jsonify({"status": "erro", "mensagem": "O software ainda está bloqueado em cooldown."}), 400
                
            # Adicionar as recompensas corretas ao utilizador (usando as chaves certas da tua CONFIG_SOFTWARE)
            novo_dados = current_user.dados + config["recompensa_dados"]
            novo_crypto = current_user.crypto + config["recompensa_crypto"]
            
            cursor.execute("UPDATE USER SET DADOS = ?, CRYPTO = ? WHERE USERNAME = ?", (novo_dados, novo_crypto, current_user.username))
            
            # Passar o slot para estado de Cooldown (usando o tempo_espera da tua configuração)
            fim_cooldown = agora + config["tempo_espera"]
            cursor.execute(
                "UPDATE SERVIDORES SET STATUS = 'Cooldown', FIM_TAREFA = ? WHERE USERNAME = ? AND SLOT_ID = ?",
                (fim_cooldown, current_user.username, slot_id)
            )
            connection.commit()
            
            # Atualizar os valores na sessão atual do utilizador logado
            current_user.dados = novo_dados
            current_user.crypto = novo_crypto
            
        return jsonify({
            "status": "sucesso", 
            "mensagem": f"Sucesso! Recebeste {config['recompensa_dados']} TB de dados e {config['recompensa_crypto']} ₿ Cripto."
        })
    except Exception as e:
        print(f"Erro em receber_recompensa: {e}")
        return jsonify({"status": "erro", "mensagem": "Erro interno ao processar recompensa."}), 500
    
@login_required
def comprar_estrutura():
    dados_recebidos = request.get_json() or {}
    slot_id = int(dados_recebidos.get("slot_id", 0))
    
    mapeamento_slots = {
        1: "Trojan",
        2: "Servidor",
        3: "Fórum da Dark Web"
    }
    
    if slot_id not in mapeamento_slots:
        return jsonify({"status": "erro", "mensagem": "Slot inválido."}), 400
        
    tipo_software = mapeamento_slots[slot_id]
    config = CONFIG_SOFTWARE[tipo_software]
    
    if current_user.dados < config["custo_dados"] or current_user.crypto < config["custo_crypto"]:
        return jsonify({"status": "erro", "mensagem": "Recursos insuficientes!"}), 400
        
    db = current_app.config["db"]
    import sqlite3 as dbapi2
    
    # Deduzir custos
    novo_dados = current_user.dados - config["custo_dados"]
    novo_crypto = current_user.crypto - config["custo_crypto"]
    
    try:
        with dbapi2.connect(db.dbfile) as connection:
            cursor = connection.cursor()
            
            # Apagar o que estava no slot anteriormente (se houver) para fazer overwrite/upgrade
            cursor.execute("DELETE FROM SERVIDORES WHERE USERNAME = ? AND SLOT_ID = ?", (current_user.username, slot_id))
            
            # Deduzir o saldo na tabela USER
            cursor.execute("UPDATE USER SET DADOS = ?, CRYPTO = ? WHERE USERNAME = ?", (novo_dados, novo_crypto, current_user.username))
            
            # Inserir o novo gerador permanente ativo
            cursor.execute(
                "INSERT INTO SERVIDORES (USERNAME, SLOT_ID, TIPO_SERVIDOR, STATUS, FIM_TAREFA) VALUES (?, ?, ?, 'Ativo', 0)",
                (current_user.username, slot_id, tipo_software)
            )
            connection.commit()
            
            current_user.dados = novo_dados
            current_user.crypto = novo_crypto
            
        return jsonify({"status": "sucesso", "mensagem": f"{tipo_software} ativado com sucesso!"})
    except Exception as e:
        print(f"Erro ao comprar: {e}")
        return jsonify({"status": "erro", "mensagem": "Erro interno do servidor."}), 500