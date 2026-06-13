# Documentação da API - Cyber Breach

## Informações Gerais

- **Base URL:** `http://localhost:8080`
- **Formato de dados:** JSON
- **Autenticação:** Sessões Flask-Login

---

## Índice

1. [Rotas Públicas](#rotas-públicas)
2. [Rotas Protegidas](#rotas-protegidas)

---

## Rotas Públicas

### `GET /`
Página inicial do jogo.

### `GET /login`
Mostra o formulário de login.

### `POST /login`
Processa o login.

**Parâmetros:**
| Campo | Tipo | Descrição |
|-------|------|-----------|
| username | string | Nome do utilizador |
| password | string | Palavra-passe |
| remember | string | "yes" para lembrar |

### `GET /registar`
Mostra o formulário de registo.

### `POST /registar`
Regista um novo hacker.

**Parâmetros:**
| Campo | Tipo | Descrição |
|-------|------|-----------|
| username | string | Nome (mínimo 1 caractere) |
| password | string | Password (mínimo 4 caracteres) |

### `GET /recuperar`
Mostra o formulário de recuperação.

### `POST /recuperar`
Altera a password.

**Parâmetros:**
| Campo | Tipo | Descrição |
|-------|------|-----------|
| username | string | Nome do utilizador |
| new_password | string | Nova password |
| confirm_password | string | Confirmação |

### `GET /logout`
Termina a sessão.

---

## Rotas Protegidas (requerem login)

### `POST /salvar-progresso`
Guarda os recursos do jogador.

**Headers:** `Content-Type: application/json`

**Corpo:**
```json
{
    "crypto": 1500,
    "dados": 3200
}
```

**Resposta:**
```json
{"status": "sucesso"}
```

---

### `POST /comprar-estrutura`
Compra uma estrutura para um slot.

**Headers:** `Content-Type: application/json`

**Corpo:**
```json
{"slot_id": 1}
```

**Mapeamento:**
| slot_id | Estrutura |
|---------|-----------|
| 1 | Trojan |
| 2 | Servidor |
| 3 | Fórum da Dark Web |

**Resposta (sucesso):**
```json
{"status": "sucesso", "mensagem": "A instalar Trojan (Nível 1)..."}
```

**Resposta (erro):**
```json
{"status": "erro", "mensagem": "Recursos insuficientes!"}
```

---

### `POST /vender-estrutura`
Vende uma estrutura ativa (reembolso de 40%).

**Headers:** `Content-Type: application/json`

**Corpo:**
```json
{"slot_id": 1}
```

**Resposta (sucesso):**
```json
{"status": "sucesso", "mensagem": "Vendido (Nível 2)! Recuperaste 120 TB e 40 ₿."}
```

**Resposta (erro):**
```json
{"status": "erro", "mensagem": "Não tens nenhuma estrutura instalada neste slot."}
```

---

### `POST /evoluir-estrutura`
Evolui uma estrutura (máximo nível 3).

**Headers:** `Content-Type: application/json`

**Corpo:**
```json
{"slot_id": 1}
```

**Resposta (sucesso):**
```json
{"status": "sucesso", "mensagem": "A evoluir para o Nível 2!"}
```

**Resposta (erro):**
```json
{"status": "erro", "mensagem": "Esta estrutura já está no Nível Máximo (3)."}
```

---

### `GET /get-leaderboard`
Retorna o TOP 5 hackers.

**Parâmetros (opcionais):**
| Campo | Tipo | Descrição |
|-------|------|-----------|
| tipo | string | `crypto` (padrão) ou `dados` |

**Exemplo:**
```
GET /get-leaderboard?tipo=crypto
```

**Resposta:**
```json
{
    "status": "sucesso",
    "leaderboard": [
        {"username": "hacker1", "crypto": 5000, "dados": 10000},
        {"username": "hacker2", "crypto": 3200, "dados": 8500}
    ]
}
```

---

## Códigos de Status

| Código | Significado |
|--------|-------------|
| 200 | Sucesso |
| 302 | Redirecionamento |
| 400 | Erro nos dados |
| 500 | Erro no servidor |

---

## Segurança

- Passwords guardadas com hash (pbkdf2_sha256)
- Sessões com SECRET_KEY
- Rotas protegidas com `@login_required`