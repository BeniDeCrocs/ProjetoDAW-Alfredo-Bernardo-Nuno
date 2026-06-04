// Esperar que o DOM esteja carregado
document.addEventListener('DOMContentLoaded', function () {
    
    // ==========================================
    // 1. LÓGICA DO OLHO DA PASSWORD
    // ==========================================
    const passwordInput = document.getElementById('password-input');
    const togglePassword = document.getElementById('toggle-password');

    if (togglePassword && passwordInput) {
        togglePassword.addEventListener('click', function () {
            if (passwordInput.type === 'password') {
                passwordInput.type = 'text';
                togglePassword.innerHTML = '<img src="/static/images/password_escondida.png" alt="Esconder Password" width="24">'; 
            } else {
                passwordInput.type = 'password';
                togglePassword.innerHTML = '<img src="/static/images/hacker_password.png" alt="Mostrar Password" width="24">';                
            }
        });
    }

    // ==========================================
    // 2. LÓGICA DO JOGO (IDLE CLICKER & MEGA ROUBO)
    // ==========================================
    const valCryptoElement = document.getElementById('val-crypto');
    const valDadosElement = document.getElementById('val-dados');

    // Só avança se os elementos do saldo existirem no HTML (ou seja, está logado)
    if (valCryptoElement && valDadosElement) {
        
        // CARREGAR ESTADO INICIAL
        let crypto = parseInt(window.INITIAL_CRYPTO || 0, 10);
        let dados = parseInt(window.INITIAL_DADOS || 0, 10);

        // FUNÇÃO PARA ATUALIZAR O ECRÃ
        function atualizarEcra() {
            valCryptoElement.innerText = crypto;
            valDadosElement.innerText = dados;
        }

        // 3. AÇÕES MANUAIS (Cliques)
        document.getElementById('btn-farm-crypto').addEventListener('click', function() {
            crypto += 1;
            atualizarEcra();
        });

        document.getElementById('btn-farm-dados').addEventListener('click', function() {
            dados += 1;
            atualizarEcra();
        });

        // 4. GERAÇÃO AUTOMÁTICA (+1 Dados por segundo)
        setInterval(function() {
            dados += 1; 
            atualizarEcra();
        }, 1000);

        // 5. A PONTE FANTASMA (Guardar na BD a cada 5 segundos)
        setInterval(function() {
            fetch('/salvar-progresso', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    crypto: crypto,
                    dados: dados
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.status !== "sucesso") {
                    console.error("Erro na Ponte Fantasma:", data);
                }
            })
            .catch(error => console.error("Falha de rede ao guardar:", error));
        }, 5000);

        // ==========================================
        // 6. LÓGICA DO MEGA-ROUBO (INICIAR -> ESPERAR -> RESGATAR)
        // ==========================================
        const btnMegaRoubo = document.getElementById('btn-mega-roubo');
        const COOLDOWN_MS = 1 * 60 * 1000; // 1 minuto (Muda para 15 * 60 * 1000 mais tarde)

        function verificarCooldown() {
            const megaRouboStart = localStorage.getItem('megaRouboStart');
            
            // ESTADO 1: Livre para iniciar
            if (!megaRouboStart) {
                btnMegaRoubo.disabled = false;
                btnMegaRoubo.style.opacity = '1';
                btnMegaRoubo.style.cursor = 'pointer';
                btnMegaRoubo.style.borderColor = '#ff4d4d'; // Cor vermelha
                btnMegaRoubo.style.color = '#ff4d4d';
                btnMegaRoubo.innerText = "🚨 Iniciar Mega-Roubo (Demora 1m)";
                return "START";
            }

            const tempoPassado = Date.now() - parseInt(megaRouboStart);

            // ESTADO 2: Em progresso (A roubar...)
            if (tempoPassado < COOLDOWN_MS) {
                btnMegaRoubo.disabled = true;
                btnMegaRoubo.style.opacity = '0.5';
                btnMegaRoubo.style.cursor = 'not-allowed';

                const tempoRestante = COOLDOWN_MS - tempoPassado;
                const minutos = Math.floor(tempoRestante / 60000);
                const segundos = Math.floor((tempoRestante % 60000) / 1000);
                
                // Formatar os segundos para terem sempre dois dígitos (ex: 09)
                const segFormatados = segundos < 10 ? "0" + segundos : segundos;
                
                btnMegaRoubo.innerText = `⏳ A extrair dados... (${minutos}m ${segFormatados}s)`;
                return "IN_PROGRESS";
            } 
            // ESTADO 3: Concluído, pronto a resgatar!
            else {
                btnMegaRoubo.disabled = false;
                btnMegaRoubo.style.opacity = '1';
                btnMegaRoubo.style.cursor = 'pointer';
                btnMegaRoubo.style.borderColor = '#00ffcc'; // Cor cyan
                btnMegaRoubo.style.color = '#00ffcc';
                btnMegaRoubo.innerText = "💰 Resgatar Mega-Roubo!";
                return "CLAIM";
            }
        }

        // Lógica ao clicar no botão do Mega Roubo
        btnMegaRoubo.addEventListener('click', function() {
            const estadoAtual = verificarCooldown();

            if (estadoAtual === "START") {
                // Inicia a contagem
                localStorage.setItem('megaRouboStart', Date.now().toString());
                verificarCooldown(); 
            } 
            else if (estadoAtual === "CLAIM") {
                // Recompensa
                crypto += 500;
                dados += 1000;
                atualizarEcra();

                // Liberta o botão para o próximo roubo
                localStorage.removeItem('megaRouboStart');
                verificarCooldown(); 
            }
        });

        // Verifica o relógio do Mega Roubo a cada segundo
        setInterval(verificarCooldown, 1000);
        verificarCooldown(); // Executa logo no início

        // ==========================================
        // 7. LÓGICA DE LOGOUT E LIMPEZA
        // ==========================================
        const btnLogout = document.getElementById('btn-logout');
        
        if (btnLogout) {
            btnLogout.addEventListener('click', function() {
                // 1. Guardar o progresso uma última vez
                fetch('/salvar-progresso', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ crypto: crypto, dados: dados })
                }).then(() => {
                    // 2. Apagar o relógio da memória do browser
                    localStorage.removeItem('megaRouboStart');
                    
                    // 3. Fazer logout seguro e ir para a página inicial
                    window.location.href = '/logout';
                }).catch(error => {
                    // Se a internet falhar na gravação, faz logout à mesma para não prender o jogador
                    localStorage.removeItem('megaRouboStart');
                    window.location.href = '/logout';
                });
            });
        }
    }
});