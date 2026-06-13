# ProjetoDAW-Alfredo-Bernardo-Nuno

1. INTRODUÇÃO E VISÃO GERAL

O Cyber Breach é um jogo incremental estilo clicker em navegador, num cenário de cibercrime e pirataria informática. O objetivo principal do utilizador é acumular dois tipos primários de recursos - Criptomoedas (Crypto) e Dados Roubados (Dados) - através de ações diretas (cliques) e de investimentos em infraestruturas automatizadas (Trojans, Servidores e Fóruns da Dark Web).

O sistema foi estruturado de forma modular e segue o padrão arquitetural Cliente-Servidor (Client-Server), onde a interface interativa corre inteiramente no navegador do cliente (Frontend), enquanto a validação de segurança, autenticação e persistência de dados ocorrem no servidor (Backend).



2. ARQUITETURA DO SISTEMA E ESTRUTURA DOS FICHEIROS

O projeto está dividido entre a lógica do servidor, modelos de dados e os ficheiros estáticos da interface pública:

server.py: Configuração da aplicação Flask e registo de rotas.

views.py: Lógica de negócio das rotas, validações e jogo.

settings.py: Definições de configuração (Portas, Secret Keys, Admin).

database.py: Camada de persistência (Interface com SQLite3).

user.py: Modelo de utilizador para integração com Flask-Login.

app.py: Ponto de entrada básico / teste de execução.

requirements.txt: Dependências e bibliotecas do projeto.

Componentes Principais:
Frontend: HTML5 estruturado com Jinja2, CSS3 estilizado com uma palete de cores inspirada no estilo Cyberpunk e JavaScript Vanilla (code.js) encarregue do loop do jogo e pedidos AJAX assíncronos.

Backend: Python 3 com a micro-framework Flask, gerindo sessões através do Flask-Login e encriptação com passlib.

Base de Dados: SQLite3 (cyberbreach.sqlite), uma solução leve e integrada.



3. ESQUEMA DA BASE DE DADOS

A base de dados é composta por duas tabelas principais geridas através de comandos SQL nativos na classe Database:

Tabela USER
Guarda as credenciais de acesso e os saldos dos recursos acumulados por cada hacker.

ID (INTEGER, Primary Key, Autoincrement)

USERNAME (TEXT, Unique, Not Null)

PASSWORD (TEXT, Not Null): Palavra-passe criptografada (PBKDF2-SHA256).

CRYPTO (INTEGER, Default 0): Saldo atual de criptomoedas.

DADOS (INTEGER, Default 50): Saldo de dados roubados (em Terabytes).


Tabela SERVIDORES
Controla os 3 slots de hardware disponíveis no painel de cada jogador.

ID (INTEGER, Primary Key, Autoincrement)

USERNAME (TEXT): Ligação ao utilizador dono do slot.

SLOT_ID (INTEGER): Número do slot visível (1 a 3).

TIPO_SERVIDOR (TEXT): Nome do software instalado ("Trojan", "Servidor", "Fórum da Dark Web").

STATUS (TEXT, Not Null): Estado do slot ("Livre", "Ativo", "EmConstrucao", "CooldownVenda").

FIM_TAREFA (INTEGER, Not Null): Timestamp UNIX indicando o momento exato em que a tarefa termina.

NIVEL (INTEGER, Default 1): Nível de evolução da estrutura (1 a 3).



4. ESPECIFICAÇÃO DA API (Rotas e Endpoints)

A comunicação do jogo é efetuada através de chamadas assíncronas (via fetch no JavaScript) para os seguintes endpoints HTTP expostos no backend:


4.1. AUTENTICAÇÃO E PÁGINAS DE SISTEMA

GET / : Renderiza o dashboard principal do jogo ou o ecrã de acesso restrito.

GET /login | POST /login : Formulário de login utilizando Flask-Login.

GET /registar | POST /registar : Validação e inserção de novos utilizadores.

GET /recuperar | POST /recuperar : Redefinição segura da palavra-passe.

GET /logout : Encerra a sessão ativa.


4.2. ENDPOINTS DO MOTOR DE JOGO

POST /salvar-progresso

Input JSON: { "crypto": int, "dados": int }

Função: Invocada automaticamente a cada 5 segundos pelo cliente (Auto-Save) para atualizar os saldos correntes.

POST /comprar-estrutura

Input JSON: { "slot_id": int }

Função: Valida o slot e os recursos na BD, deduz os custos fixos definidos em CONFIG_SOFTWARE e coloca o slot em estado EmConstrucao.

POST /evoluir-estrutura

Input JSON: { "slot_id": int }

Função: Incrementa o NIVEL da estrutura até um limite de 3. Os custos e tempos de evolução aumentam consoante o nível.

POST /vender-estrutura

Input JSON: { "slot_id": int }

Função: Remove a estrutura instalada, reembolsa 40% do investimento total despendido e ativa o estado CooldownVenda.

GET /get-leaderboard

Query Params: ?tipo=crypto ou ?tipo=dados

Função: Retorna a lista com o TOP 5 de utilizadores e os respetivos valores acumulados.



5. INSTRUÇÕES DE INSTALAÇÃO E EXECUÇÃO

Pré-requisitos:
Python 3 instalado no sistema.

Passo a Passo:

Extrair os ficheiros do projeto para uma pasta local.

Abrir a linha de comandos apontando para o diretório raiz do projeto.

Instalar as dependências listadas em requirements.txt:

pip install -r requirements.txt

Iniciar a aplicação executando o servidor:
   ```bash
   python server.py
Abrir o navegador e aceder ao endereço local:
[http://127.0.0.1:8080](http://127.0.0.1:8080)