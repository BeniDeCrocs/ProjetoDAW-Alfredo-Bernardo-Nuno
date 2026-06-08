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
    // 2. LÓGICA DO JOGO E UPGRADES
    // ==========================================
    const valCryptoElement = document.getElementById('val-crypto');
    const valDadosElement = document.getElementById('val-dados');

    // Só avança se os elementos do saldo existirem no HTML (ou seja, está logado)
    if (valCryptoElement && valDadosElement) {
        
        // CARREGAR ESTADO INICIAL E FPS
        let crypto = parseInt(window.INITIAL_CRYPTO || 0, 10);
        let dados = parseInt(window.INITIAL_DADOS || 0, 10);
        let fpsDados = parseInt(window.FPS_DADOS || 1, 10);
        let fpsCrypto = parseInt(window.FPS_CRYPTO || 0, 10);

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

        // 4. GERAÇÃO AUTOMÁTICA (+X Dados e Cryptos por segundo)
        setInterval(function() {
            dados += fpsDados; 
            crypto += fpsCrypto;
            atualizarEcra();
        }, 1000);

        // 5. A PONTE FANTASMA (Guardar na BD a cada 5 segundos)
        function guardarProgresso() {
            return fetch('/salvar-progresso', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ crypto: crypto, dados: dados })
            }).then(response => response.json());
        }

        setInterval(function() {
            guardarProgresso().catch(error => console.error("Falha ao auto-guardar:", error));
        }, 5000);

        // ==========================================
        // 6. LÓGICA DA LOJA DE SERVIDORES (Slots)
        // ==========================================
        window.comprarEstrutura = function(slotId) {
            guardarProgresso().then(() => {
                return fetch("/comprar-estrutura", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ slot_id: parseInt(slotId) })
                });
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === "sucesso") {
                    window.location.reload(); 
                } else {
                    alert("⚠️ " + data.mensagem); 
                }
            })
            .catch(error => console.error("Erro:", error));
        };

        window.venderEstrutura = function(slotId) {
            guardarProgresso().then(() => {
                return fetch("/vender-estrutura", { // CORRIGIDO PARA APONTAR PARA A ROTA CERTA!
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ slot_id: parseInt(slotId) })
                });
            })
            .then(res => res.json())
            .then(data => {
                if (data.status === "sucesso") {
                    alert(data.mensagem || "Estrutura Vendida!");
                    window.location.reload(); 
                } else {
                    alert("⚠️ " + data.mensagem); 
                }
            })
            .catch(error => console.error("Erro:", error));
        };

        // ==========================================
        // 7. LÓGICA DOS TEMPORIZADORES DOS SLOTS
        // ==========================================
        function atualizarContadoresRegressivos() {
            const agora = Math.floor(Date.now() / 1000);
            const cards = document.querySelectorAll(".slot-card");

            cards.forEach(card => {
                const status = card.getAttribute("data-status");
                const fim = parseInt(card.getAttribute("data-fim"), 10);
                
                const timerDisplay = card.querySelector(".timer-display");

                if (!status || !fim || status === "Livre") return;

                const tempoRestante = fim - agora;

                if (status === "EmConstrucao") {
                    if (tempoRestante > 0) {
                        if (timerDisplay) timerDisplay.innerText = `⏳ A Instalar: ${tempoRestante}s`;
                    } else {
                        // AQUI ESTÁ A MAGIA: Recarrega automaticamente mal a instalação termina!
                        window.location.reload();
                    }
                } else if (status === "CooldownVenda" || status === "Cooldown") {
                    if (tempoRestante > 0) {
                        if (timerDisplay) timerDisplay.innerText = `🔒 Em Manutenção: ${tempoRestante}s`;
                    } else {
                        // Recarrega automaticamente mal a manutenção termina!
                        window.location.reload();
                    }
                }
            });
        }

        atualizarContadoresRegressivos();
        setInterval(atualizarContadoresRegressivos, 1000);

        // ==========================================
        // 8. LÓGICA DO MEGA-ROUBO (AGORA INDIVIDUAL POR CONTA!)
        // ==========================================
        const btnMegaRoubo = document.getElementById('btn-mega-roubo');
        const COOLDOWN_MS = 1 * 60 * 1000; 
        
        // CRIA A CHAVE ÚNICA USANDO O NOME DO UTILIZADOR
        const megaRouboKey = 'megaRouboStart_' + window.USERNAME;

        function verificarCooldown() {
            const megaRouboStart = localStorage.getItem(megaRouboKey);
            
            if (!megaRouboStart) {
                btnMegaRoubo.disabled = false;
                btnMegaRoubo.style.opacity = '1';
                btnMegaRoubo.style.cursor = 'pointer';
                btnMegaRoubo.style.borderColor = '#db08a7'; 
                btnMegaRoubo.style.color = '#db08a7';
                btnMegaRoubo.innerText = "🚨 Iniciar Mega-Roubo (Demora 1m)";
                return "START";
            }

            const tempoPassado = Date.now() - parseInt(megaRouboStart);
            
            if (tempoPassado < COOLDOWN_MS) {
                btnMegaRoubo.disabled = true;
                btnMegaRoubo.style.opacity = '0.5';
                btnMegaRoubo.style.cursor = 'not-allowed';
                const tempoRestante = COOLDOWN_MS - tempoPassado;
                const minutos = Math.floor(tempoRestante / 60000);
                const segundos = Math.floor((tempoRestante % 60000) / 1000);
                const segFormatados = segundos < 10 ? "0" + segundos : segundos;
                
                btnMegaRoubo.innerText = `⏳ A extrair dados... (${minutos}m ${segFormatados}s)`;
                return "IN_PROGRESS";
            } else {
                btnMegaRoubo.disabled = false;
                btnMegaRoubo.style.opacity = '1';
                btnMegaRoubo.style.cursor = 'pointer';
                btnMegaRoubo.style.borderColor = '#00ffcc'; 
                btnMegaRoubo.style.color = '#00ffcc';
                btnMegaRoubo.innerText = "💰 Resgatar Mega-Roubo!";
                return "CLAIM";
            }
        }

        btnMegaRoubo.addEventListener('click', function() {
            const estadoAtual = verificarCooldown();
            if (estadoAtual === "START") {
                localStorage.setItem(megaRouboKey, Date.now().toString());
                verificarCooldown(); 
            } else if (estadoAtual === "CLAIM") {
                crypto += 500;
                dados += 1000;
                atualizarEcra();
                localStorage.removeItem(megaRouboKey);
                verificarCooldown(); 
            }
        });

        setInterval(verificarCooldown, 1000);
        verificarCooldown();

        // ==========================================
        // 9. LÓGICA DE LOGOUT E LIMPEZA
        // ==========================================
        const btnLogout = document.getElementById('btn-logout');
        
        if (btnLogout) {
            btnLogout.addEventListener('click', function() {
                // Ao fazer logout, já NÃO apagamos a chave do Mega Roubo
                // Assim impedimos que os jogadores façam batota fechando a sessão!
                guardarProgresso().then(() => {
                    window.location.href = '/logout';
                }).catch(() => {
                    window.location.href = '/logout';
                });
            });
        }
    }
});