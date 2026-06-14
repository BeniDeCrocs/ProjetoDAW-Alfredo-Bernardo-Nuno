## Introdução

Este documento descreve todas as rotas que a aplicação "Cyber Breach" disponibiliza. Basicamente, é aqui que são explicados como o frontend (a parte que o utilizador vê) se comunica com o backend (o servidor) para guardar dados, comprar estruturas, evoluir estruturas, etc.

A aplicação corre localmente em `http://localhost:8080`.

---

## Índice

1. Rotas Públicas
2. Rotas Protegidas



## Rotas Públicas (não precisam de login)

Estas rotas podem ser acedidas por qualquer pessoa, mesmo sem estar autenticada.

**GET/ – Página inicial**

É a primeira página que o utilizador vê. Se já tiver sessão iniciada, mostra o dashboard do jogo. Se não, mostra o ecrã de "Acesso Restrito".


**GET/login – Página de login**

Mostra o formulário onde o utilizador introduz o nome de utilizador e a palavra-passe para entrar no jogo.


**POST/login – Fazer login**

O que faz: Recebe os dados do formulário de login e autentica o utilizador.

Parâmetros (enviados pelo formulário):

- username (string, obrigatório) – Nome do utilizador
- password (string, obrigatório) – Palavra-passe
- remember (string, opcional) – Se for enviado com o valor "yes", o navegador guarda a sessão por mais tempo

O que acontece depois:
- Se as credenciais estiverem corretas: redireciona para o dashboard
- Se estiverem erradas: volta a mostrar o login com uma mensagem de erro


**GET/registar – Página de registo**

Mostra o formulário para criar uma nova conta de hacker.


**POST/registar – Registar novo hacker**

O que faz: Cria uma nova conta na base de dados.

Parâmetros (enviados pelo formulário):

- username (string, obrigatório) – Nome do novo hacker (mínimo 1 carácter)
- password (string, obrigatório) – Palavra-passe (mínimo 4 caracteres)

O que acontece depois:
- Se correr bem: redireciona para a página de login
- Se o nome de utilizador já existir: mostra uma mensagem de erro


**GET/recuperar – Página de recuperação de palavra-passe**

Mostra o formulário para redefinir a palavra-passe (para quem se esqueceu).

**POST/recuperar – Redefinir palavra-passe**

O que faz: Altera a palavra-passe de um utilizador na base de dados.

Parâmetros (enviados pelo formulário):

- username (string, obrigatório) – Nome do utilizador
- new_password (string, obrigatório) – Nova palavra-passe (mínimo 4 caracteres)
- confirm_password (string, obrigatório) – Confirmação da nova palavra-passe (tem de ser igual)

O que acontece depois:
- Se correr bem: redireciona para a página de login
- Se algo falhar (palavras-passe diferentes, utilizador não existe): mostra uma mensagem de erro


## Rotas Protegidas (precisam de login)

Para aceder a estas rotas, o utilizador tem de estar autenticado. Caso contrário, é redirecionado para a página de login.


**POST/salvar-progresso – Guardar recursos**

O que faz: Guarda os recursos atuais do jogador (criptomoeda e dados) na base de dados. Isto é chamado automaticamente a cada 5 segundos (auto-save) e também antes de comprar, vender ou evoluir, para não perder progresso.

Cabeçalho obrigatório: Content-Type: application/json

Corpo da requisição (JSON):

{
    "crypto": 1500,
    "dados": 3200
}

Campos:
- crypto (inteiro, obrigatório) – Quantidade de criptomoeda que o jogador tem
- dados (inteiro, obrigatório) – Quantidade de dados (em TB) que o jogador tem

Resposta (sucesso):
{"status": "sucesso"}

Resposta (erro):
{"status": "erro"}


**POST/comprar-estrutura – Comprar uma estrutura**

O que faz: Permite ao jogador comprar uma estrutura (Trojan, Servidor ou Fórum da Dark Web) para um dos três slots disponíveis.

Cabeçalho obrigatório: Content-Type: application/json

Corpo da requisição (JSON):
{"slot_id": 1}

Mapeamento de slots:
- slot_id 1: Trojan (custo: 50 TB)
- slot_id 2: Servidor (custo: 150 TB + 50 crypto)
- slot_id 3: Fórum da Dark Web (custo: 500 TB + 200 crypto)

Resposta (sucesso):
{"status": "sucesso", "mensagem": "A instalar Trojan (Nível 1)..."}

Respostas de erro possíveis:
- Recursos insuficientes: {"status": "erro", "mensagem": "Recursos insuficientes!"}
- Slot ocupado ou em manutenção: {"status": "erro", "mensagem": "Este slot está ocupado ou em manutenção!"}
- Slot inválido: {"status": "erro", "mensagem": "Slot inválido."}


**POST/vender-estrutura – Vender uma estrutura**

O que faz: Vende uma estrutura que está ativa. O jogador recebe 40% do valor total que investiu nela (incluindo todas as evoluções que fez).

Exemplo: Se gastaste 150 TB + 50 crypto no nível 1 e depois 300 TB + 100 crypto no nível 2 (total 450 TB + 150 crypto), recebes de volta 180 TB + 60 crypto.

Cabeçalho obrigatório: Content-Type: application/json

Corpo da requisição (JSON):
{"slot_id": 1}

Resposta (sucesso):
{"status": "sucesso", "mensagem": "Vendido (Nível 2)! Recuperaste 120 TB e 40 ₿."}

Respostas de erro possíveis:
- Slot vazio: {"status": "erro", "mensagem": "Não tens nenhuma estrutura instalada neste slot."}
- Estrutura não está ativa: {"status": "erro", "mensagem": "Apenas podes vender estruturas 'Ativas'."}


**POST/evoluir-estrutura – Evoluir uma estrutura**

O que faz: Evolui uma estrutura ativa para o próximo nível. Cada nível é mais caro que o anterior e aumenta a produção por segundo. O nível máximo é 3.

Custos de evolução:
- Nível 1 para 2: Custo base vezes 2
- Nível 2 para 3: Custo base vezes 3

Exemplo (Servidor, com custo base 150 TB + 50 crypto):
- Evoluir para nível 2: custa 300 TB + 100 crypto
- Evoluir para nível 3: custa 450 TB + 150 crypto

Cabeçalho obrigatório: Content-Type: application/json

Corpo da requisição (JSON):
{"slot_id": 1}

Resposta (sucesso):
{"status": "sucesso", "mensagem": "A evoluir para o Nível 2!"}

Respostas de erro possíveis:
- Já no nível máximo: {"status": "erro", "mensagem": "Esta estrutura já está no Nível Máximo (3)."}
- Recursos insuficientes: {"status": "erro", "mensagem": "Precisas de 300 DADOS e 100 CRYPTO para o Nível 2."}
- Estrutura não está ativa: {"status": "erro", "mensagem": "Apenas podes evoluir estruturas ativas."}


**GET/get-leaderboard – Ver o ranking**

O que faz: Devolve os cinco hackers com mais recursos (para mostrar no leaderboard do lado direito do ecrã).

Parâmetros opcionais:
- tipo=crypto – Ordena por quem tem mais criptomoeda (é o comportamento padrão)
- tipo=dados – Ordena por quem tem mais dados

Exemplos de pedido:
GET/get-leaderboard?tipo=crypto
GET/get-leaderboard?tipo=dados
GET/get-leaderboard (funciona da mesma forma que o primeiro)

Resposta (exemplo):

{
    "status": "sucesso",
    "leaderboard": [
        {"username": "hacker1", "crypto": 5000, "dados": 10000},
        {"username": "hacker2", "crypto": 3200, "dados": 8500},
        {"username": "hacker3", "crypto": 2100, "dados": 4300},
        {"username": "hacker4", "crypto": 1500, "dados": 2100},
        {"username": "hacker5", "crypto": 800, "dados": 1200}
    ]
}

Nota: O jogador atual aparece destacado no frontend (borda verde e letras neon), mas isso é tratado no lado do cliente, não nesta rota.

**GET/logout – Terminar sessão**

O que faz: Termina a sessão do utilizador e depois redireciona para a página inicial.


## Códigos de estado HTTP

- 200 – Sucesso: Pedidos bem-sucedidos
- 302 – Redirecionamento: Depois de login, logout, registo, etc.
- 400 – Pedido inválido: Faltam dados ou os dados estão mal formatados
- 500 – Erro no servidor: Algo correu mal no backend (base de dados, erro interno, etc.)


## Segurança

As palavras-passe não são guardadas em texto simples na base de dados. É utilizada a biblioteca passlib com o algoritmo pbkdf2_sha256 para criar hashes.

As sessões são geridas pelo Flask-Login e a chave secreta está definida no ficheiro settings.py.

As rotas protegidas usam o decorador login_required do Flask-Login.

É feita uma validação dos dados tanto no frontend (JavaScript) como no backend (Python) para garantir que não entram dados inválidos.


## Exemplo de um fluxo completo

1. O utilizador regista-se (POST /registar)
2. Faz login (POST /login)
3. Na página inicial, compra um Trojan (POST /comprar-estrutura com {"slot_id": 1})
4. Espera 10 segundos (tempo de instalação)
5. Evolui o Trojan para nível 2 (POST /evoluir-estrutura com {"slot_id": 1})
6. O progresso é guardado automaticamente a cada 5 segundos (POST /salvar-progresso)
7. O ranking é atualizado no lado direito (GET /get-leaderboard)
8. Decide vender a estrutura (POST /vender-estrutura com {"slot_id": 1})
9. Termina a sessão (GET /logout)

