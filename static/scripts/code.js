// Esperar que o DOM esteja carregado
document.addEventListener('DOMContentLoaded', function () {

    // LÓGICA DO OLHO DA PASSWORD
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

    // LÓGICA DO JOGO E UPGRADES
    const valCryptoElement = document.getElementById('val-crypto');
    const valDadosElement = document.getElementById('val-dados');

    if (valCryptoElement && valDadosElement) {
        
        let crypto = parseInt(window.INITIAL_CRYPTO || 0, 10);
        let dados = parseInt(window.INITIAL_DADOS || 0, 10);
        let fpsDados = parseInt(window.FPS_DADOS || 1, 10);
        let fpsCrypto = parseInt(window.FPS_CRYPTO || 0, 10);

        // =================================================================
        // O CADEADO DE SEGURANÇA (Evita que o auto-save apague compras/vendas)
        // =================================================================
        let isProcessingTransaction = false;

        function atualizarEcra() {
            valCryptoElement.textContent = crypto;
            valDadosElement.textContent = dados;
        }

        document.getElementById('btn-farm-crypto').addEventListener('click', function() {
            if(isProcessingTransaction) return;
            crypto += 1;
            atualizarEcra();
        });

        document.getElementById('btn-farm-dados').addEventListener('click', function() {
            if(isProcessingTransaction) return;
            dados += 1;
            atualizarEcra();
        });

        setInterval(function() {
            if(isProcessingTransaction) return;
            dados += fpsDados; 
            crypto += fpsCrypto;
            atualizarEcra();
        }, 1000);

        function guardarProgresso() {
            // Se estivermos a comprar/vender, NÃO FAZ SAVE (Evita o Bug do dinheiro sumir)
            if (isProcessingTransaction) return Promise.resolve({status: "ignorado"});
            
            return fetch('/salvar-progresso', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ crypto: crypto, dados: dados })
            }).then(response => response.json());
        }

        let autoSaveTimer = setInterval(function() {
            guardarProgresso().catch(error => console.error("Falha ao auto-guardar:", error));
        }, 5000);

        // ==========================================
        // 3. FUNÇÕES DE COMPRAR, VENDER E EVOLUIR
        // ==========================================
        window.comprarEstrutura = function(slotId) {
            if (isProcessingTransaction) return;
            isProcessingTransaction = true; // Tranca o jogo

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
                    isProcessingTransaction = false; // Destranca em caso de erro
                    alert("⚠️ " + data.mensagem);
                }
            })
            .catch(error => { isProcessingTransaction = false; console.error("Erro:", error); });
        };

        window.venderEstrutura = function(slotId) {
            if (isProcessingTransaction) return;
            if (!confirm("Tens a certeza que queres vender esta estrutura por 40% do valor investido?")) return;
            
            isProcessingTransaction = true; // Tranca o jogo

            guardarProgresso().then(() => {
                return fetch("/vender-estrutura", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ slot_id: parseInt(slotId) })
                });
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === "sucesso") {
                    alert(data.mensagem);
                    window.location.reload();
                } else {
                    isProcessingTransaction = false; // Destranca
                    alert("Erro: " + data.mensagem);
                }
            })
            .catch(error => { isProcessingTransaction = false; alert("Erro ao comunicar."); });
        };

        window.evoluirEstrutura = function(slotId) {
            if (isProcessingTransaction) return;
            isProcessingTransaction = true; // Tranca o jogo

            // ADICIONADO: Faltava aqui o guardarProgresso antes de evoluir!
            guardarProgresso().then(() => {
                return fetch('/evoluir-estrutura', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ slot_id: parseInt(slotId) })
                });
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'sucesso') {
                    alert(data.mensagem);
                    window.location.reload();
                } else {
                    isProcessingTransaction = false; // Destranca
                    alert('❌ ' + data.mensagem);
                }
            })
            .catch(error => { isProcessingTransaction = false; alert("Erro ao comunicar."); });
        };

        // ==========================================
        // 4. TEMPORIZADORES DOS SLOTS
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
                        if (timerDisplay) timerDisplay.textContent = `⏳ A Instalar: ${tempoRestante}s`;
                    } else {
                        window.location.reload();
                    }
                } else if (status === "CooldownVenda") {
                    if (tempoRestante > 0) {
                        if (timerDisplay) timerDisplay.textContent = `🔒 Em Manutenção: ${tempoRestante}s`;
                    } else {
                        window.location.reload();
                    }
                }
            });
        }

        atualizarContadoresRegressivos();
        setInterval(atualizarContadoresRegressivos, 1000);

        // ==========================================
        // 5. MEGA-ROUBO
        // ==========================================
        const btnMegaRoubo = document.getElementById('btn-mega-roubo');
        const COOLDOWN_MS = 60 * 1000;
        const megaRouboKey = 'megaRouboStart_' + window.USERNAME;

        function verificarCooldown() {
            const megaRouboStart = localStorage.getItem(megaRouboKey);
            
            if (!megaRouboStart) {
                btnMegaRoubo.disabled = false;
                btnMegaRoubo.style.opacity = '1';
                btnMegaRoubo.style.cursor = 'pointer';
                btnMegaRoubo.style.borderColor = '#db08a7'; 
                btnMegaRoubo.style.color = '#db08a7';
                btnMegaRoubo.textContent = "🚨 Iniciar Mega-Roubo (Demora 1m)";
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
                btnMegaRoubo.textContent = `⏳ A extrair dados... (${minutos}m ${segundos}s)`;
                return "IN_PROGRESS";
            } else {
                btnMegaRoubo.disabled = false;
                btnMegaRoubo.style.opacity = '1';
                btnMegaRoubo.style.cursor = 'pointer';
                btnMegaRoubo.style.borderColor = '#00ffcc'; 
                btnMegaRoubo.style.color = '#00ffcc';
                btnMegaRoubo.textContent = "💰 Resgatar Mega-Roubo!";
                return "CLAIM";
            }
        }

        if (btnMegaRoubo) {
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
        }

        // ==========================================
        // 6. LOGOUT
        // ==========================================
        const btnLogout = document.getElementById('btn-logout');
        if (btnLogout) {
            btnLogout.addEventListener('click', function() {
                clearInterval(autoSaveTimer); 
                guardarProgresso().then(() => {
                    window.location.href = '/logout';
                }).catch(() => {
                    window.location.href = '/logout';
                });
            });
        }

        // ==========================================
        // LEADERBOARD COM ABA SELETORA
        // ==========================================
        let leaderboardTipoAtual = 'crypto';

        function carregarLeaderboard() {
            const container = document.getElementById('leaderboard-container');
            if (!container) return;
            
            container.innerHTML = '<div style="text-align: center; padding: 20px; color: #666;"><span>⏳ A carregar...</span></div>';
            
            fetch(`/get-leaderboard?tipo=${leaderboardTipoAtual}`, {
                method: 'GET',
                headers: { 'Content-Type': 'application/json' }
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'sucesso' && data.leaderboard) {
                    if (data.leaderboard.length === 0) {
                        container.innerHTML = '<div style="text-align: center; padding: 20px; color: #666;">Sem dados para ranking.</div>';
                        return;
                    }
                    
                    let html = '';
                    data.leaderboard.forEach((jogador, index) => {
                        let medalha = '';
                        if (index === 0) medalha = '🥇';
                        else if (index === 1) medalha = '🥈';
                        else if (index === 2) medalha = '🥉';
                        else medalha = `${index + 1}º`;
                        
                        // Destacar o próprio jogador
                        const isCurrentUser = (jogador.username === window.USERNAME);
                        const rowStyle = isCurrentUser ? 'background-color: rgba(0, 255, 204, 0.15); border-left: 3px solid #00ffcc;' : '';
                        const nameStyle = isCurrentUser ? 'color: #00ffcc; font-weight: bold;' : 'color: #ffffff;';
                        
                        // Formatar números
                        let cryptoDisplay = jogador.crypto;
                        let dadosDisplay = jogador.dados;
                        if (cryptoDisplay >= 1000000) cryptoDisplay = (cryptoDisplay / 1000000).toFixed(1) + 'M';
                        else if (cryptoDisplay >= 1000) cryptoDisplay = (cryptoDisplay / 1000).toFixed(1) + 'K';
                        
                        if (dadosDisplay >= 1000000) dadosDisplay = (dadosDisplay / 1000000).toFixed(1) + 'M';
                        else if (dadosDisplay >= 1000) dadosDisplay = (dadosDisplay / 1000).toFixed(1) + 'K';
                        
                        html += `
                            <div style="display: flex; justify-content: space-between; align-items: center; padding: 8px 5px; border-bottom: 1px solid #333; ${rowStyle}">
                                <div style="display: flex; align-items: center; gap: 10px;">
                                    <span style="color: #ffc107; font-weight: bold; width: 35px; font-size: 14px;">${medalha}</span>
                                    <span style="${nameStyle} font-size: 13px;">${escapeHtml(jogador.username)}</span>
                                </div>
                                <div style="display: flex; gap: 12px;">
                                    <span style="color: gold; font-size: 11px;">
                                        <img src="/static/images/bitcoin_currency2.png" style="width: 12px; height: 12px; vertical-align: middle;"> ${cryptoDisplay}
                                    </span>
                                    <span style="color: #00ffcc; font-size: 11px;">
                                        <img src="/static/images/dados_currency.png" style="width: 12px; height: 12px; vertical-align: middle;"> ${dadosDisplay} TB
                                    </span>
                                </div>
                            </div>
                        `;
                    });
                    
                    container.innerHTML = html;
                } else {
                    container.innerHTML = '<div style="text-align: center; padding: 20px; color: #ff4d4d;">Erro ao carregar ranking.</div>';
                }
            })
            .catch(error => {
                console.error("Erro ao buscar leaderboard:", error);
                container.innerHTML = '<div style="text-align: center; padding: 20px; color: #ff4d4d;">Erro ao carregar ranking.</div>';
            });
        }

        // Função auxiliar para escapar HTML
        function escapeHtml(text) {
            if (!text) return '';
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }

        // Configurar botões do leaderboard
        const btnCrypto = document.getElementById('leaderboard-crypto-btn');
        const btnDados = document.getElementById('leaderboard-dados-btn');

        if (btnCrypto && btnDados) {
            btnCrypto.addEventListener('click', function() {
                leaderboardTipoAtual = 'crypto';
                btnCrypto.style.backgroundColor = '#1a1a2e';
                btnDados.style.backgroundColor = '#000000';
                carregarLeaderboard();
            });
            
            btnDados.addEventListener('click', function() {
                leaderboardTipoAtual = 'dados';
                btnDados.style.backgroundColor = '#1a1a2e';
                btnCrypto.style.backgroundColor = '#000000';
                carregarLeaderboard();
            });
            
            // Carregar leaderboard inicial
            carregarLeaderboard();
            
            // Atualizar a cada 15 segundos
            setInterval(carregarLeaderboard, 15000);
        }
    }
});