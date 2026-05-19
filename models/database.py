import sqlite3 as dbapi2

# Classe responsável por gerir a base de dados
class Database:
    def __init__(self, dbfile):
        self.dbfile = dbfile # Guarda o nome do ficheiro da BD
        self.create_user_table() # Chama o método para criar a tabela se não existir
        
    def create_user_table(self):
        with dbapi2.connect(self.dbfile) as connection:
            cursor = connection.cursor()
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS USER (
                ID INTEGER PRIMARY KEY AUTOINCREMENT,
                USERNAME TEXT UNIQUE NOT NULL,
                PASSWORD TEXT NOT NULL
            )
            """)
            connection.commit()

    def get_user(self, username):
        with dbapi2.connect(self.dbfile) as connection:
            cursor = connection.cursor()
            query = "SELECT USERNAME, PASSWORD FROM USER WHERE USERNAME = ?"
            cursor.execute(query, (username,))
            row = cursor.fetchone()
            if row:
                return {"username": row[0], "password": row[1]}
            return None
        
    def add_user(self, username, hashed_password):
        with dbapi2.connect(self.dbfile) as connection:
            cursor = connection.cursor()
            try:
                #Tenta inserir o utilizador
                query = "INSERT INTO USER (USERNAME, PASSWORD) VALUES (?, ?)"
                cursor.execute(query, (username, hashed_password))
                connection.commit()
                return True # Sucesso!
            except dbapi2.IntegrityError:
                # Como o USERNAME é UNIQUE na vossa BD, se falhar é porque já existe
                return False