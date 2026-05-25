# Modo de debug ativo (Cuidado: usar apenas em desenvolvimento)
DEBUG = True

# Porta de execução da aplicação
PORT = 8080

# Chave usada para proteger as sessões da aplicação
SECRET_KEY = "cyber_breach_secret"

# Palavra-passe do admin com HASH (Nunca em texto simples!)
ADMIN_PASSWORD = '$pbkdf2-sha256$29000$LeU857z33jtHaI0R4rx3rg$wGUVZMcQpkEyFVhOAhxqIpNeYML3K2pWXojmGqDwweg'
ADMIN_USERNAME = "admin"
# Duração da sessão "Relembra-me" em segundos (30 dias)
REMEMBER_COOKIE_DURATION = 30 * 24 * 60 * 60  # 2592000 segundos