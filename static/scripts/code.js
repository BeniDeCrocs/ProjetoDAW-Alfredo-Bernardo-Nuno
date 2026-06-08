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

    if (valCryptoElement && valDadosElement) {
        
        let crypto = parseInt(window.INITIAL_CRYPTO || 0, 10);
        let dados = parseInt(window.INITIAL_DADOS || 0, 10);
        let fpsDados = parseInt(window.FPS_DADOS || 1, 10);
        let fpsCrypto = parseInt(window.FPS_CRYPTO || 0, 10);

        function atualizarEcra() {
            valCryptoElement.textContent = crypto;
            valDadosElement.textContent = dados;
        }

        document.getElementById('btn-farm-crypto').addEventListener('click', function() {
            crypto += 1;
            atualizarEcra();
        });

        document.getElementById('btn-farm-dados').addEventListener('click', function() {
            dados += 1;
            atualizarEcra();
        });

        setInterval(function() {
            dados += fpsDados; 
            crypto += fpsCrypto;
            atualizarEcra();
        }, 1000);

        function guardarProgresso() {
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
            fetch("/comprar-estrutura", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ slot_id: parseInt(slotId) })
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
            if (!confirm("Tens a certeza que queres vender esta estrutura por 40% do valor investido?")) {
                return;
            }
            
            fetch("/vender-estrutura", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ slot_id: parseInt(slotId) })
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === "sucesso") {
                    alert(data.mensagem);
                    window.location.reload();
                } else {
                    alert("Erro: " + data.mensagem);
                }
            })
            .catch(error => {
                console.error("Erro na requisição:", error);
                alert("Erro ao comunicar com o servidor.");
            });
        };

        window.evoluirEstrutura = function(slotId) {
            fetch('/evoluir-estrutura', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ slot_id: parseInt(slotId) })
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'sucesso') {
                    alert(data.mensagem);
                    window.location.reload();
                } else {
                    alert('❌ ' + data.mensagem);
                }
            })
            .catch(error => {
                console.error("Erro na comunicação:", error);
                alert("Erro ao comunicar com o servidor.");
            });
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
    }
});
