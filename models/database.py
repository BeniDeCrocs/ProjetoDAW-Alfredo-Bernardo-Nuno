import sqlite3 as dbapi2

# Classe responsável por gerir a base de dados
class Database:
    def __init__(self, dbfile):
        self.dbfile = dbfile # Guarda o nome do ficheiro da BD
        self.create_user_table() # Chama o método para criar a tabela se não existir
        self.create_server_table()
        
    def create_user_table(self):
        with dbapi2.connect(self.dbfile) as connection:
            cursor = connection.cursor()
            # Adicionámos as colunas CRYPTO e DADOS com valores por defeito
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS USER (
                ID INTEGER PRIMARY KEY AUTOINCREMENT,
                USERNAME TEXT UNIQUE NOT NULL,
                PASSWORD TEXT NOT NULL,
                CRYPTO INTEGER DEFAULT 0, 
                DADOS INTEGER DEFAULT 50
            )
            """)
            connection.commit()

    def get_user(self, username):
        with dbapi2.connect(self.dbfile) as connection:
            cursor = connection.cursor()
            # Agora pedimos também o CRYPTO e os DADOS à base de dados
            query = "SELECT USERNAME, PASSWORD, CRYPTO, DADOS FROM USER WHERE USERNAME = ?"
            cursor.execute(query, (username,))
            row = cursor.fetchone()
            if row:
                # Devolvemos um dicionário com toda a informação do Hacker
                return {
                    "username": row[0], 
                    "password": row[1],
                    "crypto": row[2],
                    "dados": row[3]
                }
            return None
        
    def add_user(self, username, hashed_password):
        with dbapi2.connect(self.dbfile) as connection:
            cursor = connection.cursor()
            try:
                #Tenta inserir o utilizador
                query = "INSERT INTO USER (USERNAME, PASSWORD, CRYPTO, DADOS) VALUES (?, ?, 0, 50)"
                cursor.execute(query, (username, hashed_password))
                connection.commit()
                return True # Sucesso!
            except dbapi2.IntegrityError:
                # Como o USERNAME é UNIQUE na vossa BD, se falhar é porque já existe
                return False
            
    def update_password(self, username, new_hashed_password):
        """Atualiza a password de um utilizador na base de dados"""
        try:
            with dbapi2.connect(self.dbfile) as connection:
                cursor = connection.cursor()
                query = "UPDATE USER SET PASSWORD = ? WHERE USERNAME = ?"
                cursor.execute(query, (new_hashed_password, username))
                connection.commit()
                return cursor.rowcount > 0  # True se atualizou algum registo
        except Exception as e:
            print(f"Erro ao atualizar password: {e}")
            return False
        
    def create_server_table(self):
        with dbapi2.connect(self.dbfile) as connection:
            cursor = connection.cursor()
            # Cria a tabela de servidores associada aos utilizadores
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS SERVIDORES (
                ID INTEGER PRIMARY KEY AUTOINCREMENT,
                USERNAME TEXT NOT NULL,
                SLOT_ID INTEGER NOT NULL,
                TIPO_SERVIDOR TEXT NOT NULL,
                STATUS TEXT DEFAULT 'Parado',
                FIM_TAREFA TIMESTAMP,
                FOREIGN KEY(USERNAME) REFERENCES USER(USERNAME)
            )
            """)
            connection.commit()
            
    # Função para ir buscar os servidores de um Hacker específico
    def get_user_servers(self, username):
        with dbapi2.connect(self.dbfile) as connection:
            cursor = connection.cursor()
            query = "SELECT SLOT_ID, TIPO_SERVIDOR, STATUS, FIM_TAREFA FROM SERVIDORES WHERE USERNAME = ?"
            cursor.execute(query, (username,))
            # Devolve uma lista de dicionários para ser fácil de usar no HTML
            return [{"slot_id": row[0], "tipo": row[1], "status": row[2], "fim_tarefa": row[3]} for row in cursor.fetchall()]

    def update_user_resources(self, username, crypto, dados):
        """Atualiza os valores de crypto e dados de um utilizador silenciosamente"""
        try:
            with dbapi2.connect(self.dbfile) as connection:
                cursor = connection.cursor()
                query = "UPDATE USER SET CRYPTO = ?, DADOS = ? WHERE USERNAME = ?"
                cursor.execute(query, (crypto, dados, username))
                connection.commit()
                return cursor.rowcount > 0
        except Exception as e:
            print(f"Erro ao guardar recursos: {e}")
            return False

    def insert_server(self, username, slot_id, tipo_servidor, status, fim_tarefa):
        """Cria uma nova construção num determinado slot"""
        with dbapi2.connect(self.dbfile) as connection:
            cursor = connection.cursor()
            query = "INSERT INTO SERVIDORES (USERNAME, SLOT_ID, TIPO_SERVIDOR, STATUS, FIM_TAREFA) VALUES (?, ?, ?, ?, ?)"
            cursor.execute(query, (username, slot_id, tipo_servidor, status, fim_tarefa))
            connection.commit()

    def update_server_status(self, username, slot_id, status, fim_tarefa=None):
        """Atualiza o estado e o timestamp de um slot específico"""
        with dbapi2.connect(self.dbfile) as connection:
            cursor = connection.cursor()
            query = "UPDATE SERVIDORES SET STATUS = ?, FIM_TAREFA = ? WHERE USERNAME = ? AND SLOT_ID = ?"
            cursor.execute(query, (status, fim_tarefa, username, slot_id))
            connection.commit()