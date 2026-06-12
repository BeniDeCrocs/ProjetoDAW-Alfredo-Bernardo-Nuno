from flask import render_template, request, redirect, url_for, current_app, jsonify
from passlib.hash import pbkdf2_sha256 as hasher
from flask_login import login_required, logout_user, login_user, current_user 
from user import get_user
import time
import sqlite3 as dbapi2
import math

CONFIG_SOFTWARE = {
    "Trojan": {
        "custo_dados": 50, "custo_crypto": 0,
        "geracao_dados": 5, "geracao_crypto": 0,
        "tempo_construcao": 10,
        "tempo_venda": 15
    },
    "Servidor": {
        "custo_dados": 150, "custo_crypto": 50,
        "geracao_dados": 10, "geracao_crypto": 2,
        "tempo_construcao": 30,
        "tempo_venda": 45
    },
    "Fórum da Dark Web": {
        "custo_dados": 500, "custo_crypto": 200,
        "geracao_dados": 20, "geracao_crypto": 6,
        "tempo_construcao": 60,
        "tempo_venda": 90
    }
}

def home_page():
    if not current_user.is_authenticated:
        return render_template("index.html", slots={}, total_fps_dados=0, total_fps_crypto=0)
        
    db = current_app.config["db"]
    agora = int(time.time())
    
    slots = {
        1: {"slot_id": 1, "tipo": "Trojan", "status": "Livre", "producao_d": 0, "producao_c": 0, "fim_tarefa": 0, "nivel": 0},
        2: {"slot_id": 2, "tipo": "Servidor", "status": "Livre", "producao_d": 0, "producao_c": 0, "fim_tarefa": 0, "nivel": 0},
        3: {"slot_id": 3, "tipo": "Fórum da Dark Web", "status": "Livre", "producao_d": 0, "producao_c": 0, "fim_tarefa": 0, "nivel": 0}
    }
    
    total_geracao_dados = 1
    total_geracao_crypto = 0
    
    try:
        with dbapi2.connect(db.dbfile) as connection:
            connection.row_factory = dbapi2.Row
            cursor = connection.cursor()
            
            cursor.execute("SELECT SLOT_ID, TIPO_SERVIDOR, STATUS, FIM_TAREFA, NIVEL FROM SERVIDORES WHERE USERNAME = ?", (current_user.username,))
            servidores_bd = cursor.fetchall()
            
            for s in servidores_bd:
                slot_id = s["SLOT_ID"]
                status = s["STATUS"]
                fim_tarefa = s["FIM_TAREFA"] or 0
                nivel = s["NIVEL"] or 1
                tipo = slots[slot_id]["tipo"]
                
                if status == "EmConstrucao" and agora >= fim_tarefa:
                    status = "Ativo"
                    fim_tarefa = 0
                    cursor.execute("UPDATE SERVIDORES SET STATUS = 'Ativo', FIM_TAREFA = 0 WHERE USERNAME = ? AND SLOT_ID = ?", (current_user.username, slot_id))
                    connection.commit()
                    
                elif status == "CooldownVenda" and agora >= fim_tarefa:
                    cursor.execute("DELETE FROM SERVIDORES WHERE USERNAME = ? AND SLOT_ID = ?", (current_user.username, slot_id))
                    connection.commit()
                    continue
                
                slots[slot_id]["status"] = status
                slots[slot_id]["fim_tarefa"] = fim_tarefa
                slots[slot_id]["nivel"] = nivel
                
                if status == "Ativo":
                    config = CONFIG_SOFTWARE[tipo]
                    multiplicador = nivel
                    slots[slot_id]["producao_d"] = config["geracao_dados"] * multiplicador
                    slots[slot_id]["producao_c"] = config["geracao_crypto"] * multiplicador
                    total_geracao_dados += config["geracao_dados"] * multiplicador
                    total_geracao_crypto += config["geracao_crypto"] * multiplicador

            cursor.execute(
                """
                SELECT USERNAME, CRYPTO 
                FROM USER 
                ORDER BY CRYPTO DESC, DADOS DESC 
                LIMIT 5
                """
            )
            leaderboard = cursor.fetchall()
                    
    except Exception as e:
        print(f"Erro ao carregar slots: {e}")
    
    return render_template(
        "index.html", 
        slots=slots,
        total_fps_dados=total_geracao_dados,
        total_fps_crypto=total_geracao_crypto,
        config=CONFIG_SOFTWARE,
        leaderboard=leaderboard
    )

@login_required
def get_leaderboard():
    """Retorna o TOP 5 hackers ordenado por tipo especificado"""
    tipo = request.args.get('tipo', 'crypto')  # 'crypto' ou 'dados'
    db = current_app.config["db"]
    
    try:
        with dbapi2.connect(db.dbfile) as connection:
            connection.row_factory = dbapi2.Row
            cursor = connection.cursor()
            
            if tipo == 'crypto':
                cursor.execute("""
                    SELECT USERNAME, CRYPTO, DADOS 
                    FROM USER 
                    ORDER BY CRYPTO DESC, DADOS DESC 
                    LIMIT 5
                """)
            else:
                cursor.execute("""
                    SELECT USERNAME, CRYPTO, DADOS 
                    FROM USER 
                    ORDER BY DADOS DESC, CRYPTO DESC 
                    LIMIT 5
                """)
            
            leaderboard = cursor.fetchall()
            
            resultado = []
            for row in leaderboard:
                resultado.append({
                    "username": row["USERNAME"],
                    "crypto": row["CRYPTO"],
                    "dados": row["DADOS"]
                })
            
            return jsonify({"status": "sucesso", "leaderboard": resultado})
    except Exception as e:
        print(f"Erro ao buscar leaderboard: {e}")
        return jsonify({"status": "erro", "mensagem": str(e)}), 500

@login_required
def comprar_estrutura():
    dados_recebidos = request.get_json() or {}
    slot_id = int(dados_recebidos.get("slot_id", 0))
    mapeamento_slots = {1: "Trojan", 2: "Servidor", 3: "Fórum da Dark Web"}
    
    if slot_id not in mapeamento_slots:
        return jsonify({"status": "erro", "mensagem": "Slot inválido."}), 400
        
    tipo_software = mapeamento_slots[slot_id]
    config = CONFIG_SOFTWARE[tipo_software]
    
    db = current_app.config["db"]
    agora = int(time.time())
    
    try:
        with dbapi2.connect(db.dbfile) as connection:
            cursor = connection.cursor()
            
            # 1. Puxa os dados atualizados fisicamente da Base de Dados!
            cursor.execute("SELECT DADOS, CRYPTO FROM USER WHERE USERNAME = ?", (current_user.username,))
            user_data = cursor.fetchone()
            db_dados, db_crypto = user_data[0], user_data[1]
            
            if db_dados < config["custo_dados"] or db_crypto < config["custo_crypto"]:
                return jsonify({"status": "erro", "mensagem": "Recursos insuficientes!"}), 400
                
            cursor.execute("SELECT STATUS, FIM_TAREFA FROM SERVIDORES WHERE USERNAME = ? AND SLOT_ID = ?", (current_user.username, slot_id))
            resultado = cursor.fetchone()
            
            if resultado:
                return jsonify({"status": "erro", "mensagem": "Este slot está ocupado ou em manutenção!"}), 400
            
            # Calcula custos e os novos tempos (Nível 1)
            novo_dados = db_dados - config["custo_dados"]
            novo_crypto = db_crypto - config["custo_crypto"]
            fim_construcao = agora + config["tempo_construcao"] # Nível 1 demora o tempo base
            
            cursor.execute("UPDATE USER SET DADOS = ?, CRYPTO = ? WHERE USERNAME = ?", (novo_dados, novo_crypto, current_user.username))
            
            cursor.execute(
                "INSERT INTO SERVIDORES (USERNAME, SLOT_ID, TIPO_SERVIDOR, STATUS, FIM_TAREFA, NIVEL) VALUES (?, ?, ?, 'EmConstrucao', ?, 1)",
                (current_user.username, slot_id, tipo_software, fim_construcao)
            )
            connection.commit()
            
            current_user.dados = novo_dados
            current_user.crypto = novo_crypto
            
        return jsonify({"status": "sucesso", "mensagem": f"A instalar {tipo_software} (Nível 1)..."})
    except Exception as e:
        print(f"Erro ao comprar: {e}")
        return jsonify({"status": "erro", "mensagem": "Erro interno."}), 500

@login_required
def evoluir_estrutura():
    dados_pedido = request.get_json() or {}
    slot_id = int(dados_pedido.get("slot_id", 0))
    
    db = current_app.config["db"]
    agora = int(time.time())

    try:
        with dbapi2.connect(db.dbfile) as connection:
            cursor = connection.cursor()
            
            # Puxa recursos reais do DB!
            cursor.execute("SELECT DADOS, CRYPTO FROM USER WHERE USERNAME = ?", (current_user.username,))
            user_data = cursor.fetchone()
            db_dados, db_crypto = user_data[0], user_data[1]
            
            cursor.execute(
                "SELECT TIPO_SERVIDOR, STATUS, NIVEL FROM SERVIDORES WHERE USERNAME = ? AND SLOT_ID = ?",
                (current_user.username, slot_id)
            )
            linha = cursor.fetchone()

            if not linha:
                return jsonify({"status": "erro", "mensagem": "Não há estrutura neste slot."}), 400

            tipo_software = linha[0]
            status_atual = linha[1]
            nivel_atual = linha[2]

            if status_atual != "Ativo":
                return jsonify({"status": "erro", "mensagem": "Apenas podes evoluir estruturas ativas."}), 400
                
            if nivel_atual >= 3:
                return jsonify({"status": "erro", "mensagem": "Esta estrutura já está no Nível Máximo (3)."}), 400

            config = CONFIG_SOFTWARE.get(tipo_software)
            nivel_alvo = nivel_atual + 1
            custo_dados = config["custo_dados"] * nivel_alvo
            custo_crypto = config["custo_crypto"] * nivel_alvo

            if db_dados < custo_dados or db_crypto < custo_crypto:
                return jsonify({"status": "erro", "mensagem": f"Precisas de {custo_dados} DADOS e {custo_crypto} CRYPTO para o Nível {nivel_alvo}."}), 400

            novo_dados = db_dados - custo_dados
            novo_crypto = db_crypto - custo_crypto
            
            # O Tempo de Instalação AUMENTA de acordo com o Nível
            tempo_evolucao = config["tempo_construcao"] * nivel_alvo
            fim_evolucao = agora + tempo_evolucao

            cursor.execute("UPDATE USER SET DADOS = ?, CRYPTO = ? WHERE USERNAME = ?", (novo_dados, novo_crypto, current_user.username))
            
            cursor.execute(
                "UPDATE SERVIDORES SET STATUS = 'EmConstrucao', FIM_TAREFA = ?, NIVEL = ? WHERE USERNAME = ? AND SLOT_ID = ?",
                (fim_evolucao, nivel_alvo, current_user.username, slot_id)
            )
            connection.commit()

            current_user.dados = novo_dados
            current_user.crypto = novo_crypto

        return jsonify({"status": "sucesso", "mensagem": f"A evoluir para o Nível {nivel_alvo}!"})
        
    except Exception as e:
        print("Erro crítico ao evoluir:", e)
        return jsonify({"status": "erro", "mensagem": "Erro no servidor ao tentar evoluir."}), 500

@login_required
def vender_estrutura():
    dados_pedido = request.get_json() or {}
    slot_id = int(dados_pedido.get("slot_id", 0))
    
    db = current_app.config["db"]
    agora = int(time.time())

    try:
        with dbapi2.connect(db.dbfile) as connection:
            cursor = connection.cursor()

            # Puxa recursos atualizados do DB
            cursor.execute("SELECT DADOS, CRYPTO FROM USER WHERE USERNAME = ?", (current_user.username,))
            user_data = cursor.fetchone()
            db_dados, db_crypto = user_data[0], user_data[1]

            cursor.execute(
                "SELECT TIPO_SERVIDOR, STATUS, NIVEL FROM SERVIDORES WHERE USERNAME = ? AND SLOT_ID = ?",
                (current_user.username, slot_id)
            )
            linha = cursor.fetchone()

            if not linha:
                return jsonify({"status": "erro", "mensagem": "Não tens nenhuma estrutura instalada neste slot."}), 400

            tipo_software = linha[0]
            status_atual = linha[1]
            nivel_atual = linha[2]

            if status_atual != "Ativo":
                return jsonify({"status": "erro", "mensagem": "Apenas podes vender estruturas 'Ativas'."}), 400

            config = CONFIG_SOFTWARE.get(tipo_software)
            
            # Soma de todo o custo (Ex: Vender nivel 2 = custo base x 1 + custo base x 2)
            multiplicador_total = sum(range(1, nivel_atual + 1))
            total_dados_gasto = config["custo_dados"] * multiplicador_total
            total_crypto_gasto = config["custo_crypto"] * multiplicador_total

            reembolso_dados = math.floor(total_dados_gasto * 0.40)
            reembolso_crypto = math.floor(total_crypto_gasto * 0.40)

            # O Tempo do Cooldown AUMENTA consoante o nível do Software destruído
            tempo_espera = config.get("tempo_venda", 30) * nivel_atual
            fim_cooldown = agora + tempo_espera

            novo_dados = db_dados + reembolso_dados
            novo_crypto = db_crypto + reembolso_crypto

            cursor.execute(
                "UPDATE USER SET DADOS = ?, CRYPTO = ? WHERE USERNAME = ?",
                (novo_dados, novo_crypto, current_user.username)
            )

            cursor.execute(
                "UPDATE SERVIDORES SET STATUS = 'CooldownVenda', FIM_TAREFA = ?, NIVEL = 1 WHERE USERNAME = ? AND SLOT_ID = ?",
                (fim_cooldown, current_user.username, slot_id)
            )
            connection.commit()

            current_user.dados = novo_dados
            current_user.crypto = novo_crypto

        return jsonify({
            "status": "sucesso",
            "mensagem": f"Vendido (Nível {nivel_atual})! Recuperaste {reembolso_dados} TB e {reembolso_crypto} ₿."
        })
        
    except Exception as e:
        print("Erro crítico ao vender estrutura:", e)
        return jsonify({"status": "erro", "mensagem": "Erro no servidor ao tentar vender."}), 500

@login_required
def salvar_progresso():
    dados_recebidos = request.get_json()
    if not dados_recebidos: 
        return jsonify({"status": "erro"}), 400

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
# Funções de Login / Registo / Recuperar
# ==========================================================

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