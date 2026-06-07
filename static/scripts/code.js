document.addEventListener('DOMContentLoaded', function () {

    const passwordInput = document.getElementById('password-input');
    const togglePassword = document.getElementById('toggle-password');
    if (togglePassword && passwordInput) {
        togglePassword.addEventListener('click', function () {
            if (passwordInput.type === 'password') {
                passwordInput.type = 'text';
                togglePassword.innerHTML = '<img src="/static/images/password_escondida.png" alt="Esconder" width="24">'; 
            } else {
                passwordInput.type = 'password';
                togglePassword.innerHTML = '<img src="/static/images/hacker_password.png" alt="Mostrar" width="24">';                
            }
        });
    }

    const valCryptoElement = document.getElementById('val-crypto');
    const valDadosElement = document.getElementById('val-dados');

    if (valCryptoElement && valDadosElement) {
        
        let crypto = parseInt(window.INITIAL_CRYPTO || 0, 10);
        let dados = parseInt(window.INITIAL_DADOS || 0, 10);
        let fpsDados = parseInt(window.FPS_DADOS || 1, 10);
        let fpsCrypto = parseInt(window.FPS_CRYPTO || 0, 10);

        function atualizarEcra() {
            valCryptoElement.innerText = crypto;
            valDadosElement.innerText = dados;
        }

        const btnFarmC = document.getElementById('btn-farm-crypto');
        if (btnFarmC) btnFarmC.addEventListener('click', function() { crypto += 1; atualizarEcra(); });

        const btnFarmD = document.getElementById('btn-farm-dados');
        if (btnFarmD) btnFarmD.addEventListener('click', function() { dados += 1; atualizarEcra(); });

        // ==========================================
        // LÓGICA DO MEGA ROUBO
        // ==========================================
        const btnMegaRoubo = document.getElementById('btn-mega-roubo');
        const COOLDOWN_MS = 1 * 60 * 1000; // 1 Minuto de espera. Podes mudar aqui!

        if (btnMegaRoubo) {
            function verificarCooldown() {
                const megaRouboStart = localStorage.getItem('megaRouboStart');
                
                if (!megaRouboStart) {
                    btnMegaRoubo.disabled = false;
                    btnMegaRoubo.style.opacity = '1';
                    btnMegaRoubo.style.cursor = 'pointer';
                    btnMegaRoubo.style.borderColor = '#db08a7'; 
                    btnMegaRoubo.style.color = '#db08a7';
                    btnMegaRoubo.innerText = "🚨 Iniciar Mega-Roubo";
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
                    
                    btnMegaRoubo.innerText = `⏳ A extrair... (${minutos}m ${segFormatados}s)`;
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
                    localStorage.setItem('megaRouboStart', Date.now().toString());
                    verificarCooldown(); 
                } 
                else if (estadoAtual === "CLAIM") {
                    // Recompensas do Mega Roubo (Podes alterar os valores à vontade)
                    crypto += 50;  
                    dados += 200;  
                    atualizarEcra();

                    localStorage.removeItem('megaRouboStart');
                    verificarCooldown(); 
                }
            });

            setInterval(verificarCooldown, 1000);
            verificarCooldown(); 
        }

        // Geração Automática
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
            }).then(r => r.json());
        }

        setInterval(function() {
            guardarProgresso().catch(e => console.error("Falha ao guardar:", e));
        }, 5000);

        // ==========================================
        // COMUNICAÇÃO COM O SERVIDOR (Comprar e Vender)
        // ==========================================
        window.comprarEstrutura = function(slotId) {
            guardarProgresso().then(() => {
                return fetch("/comprar-estrutura", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ slot_id: parseInt(slotId) })
                });
            })
            .then(r => r.json())
            .then(data => {
                if (data.status === "sucesso") window.location.reload(); 
                else alert("⚠️ " + data.mensagem); 
            }).catch(e => console.error(e));
        };

        window.venderEstrutura = function(slotId) {
            if(!confirm("Tens a certeza que queres desligar e vender esta estrutura? Vais perder a geração passiva que ela dá.")) return;
            
            guardarProgresso().then(() => {
                return fetch("/vender-estrutura", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ slot_id: parseInt(slotId) })
                });
            })
            .then(r => r.json())
            .then(data => {
                if (data.status === "sucesso") window.location.reload(); 
                else alert(data.mensagem); 
            }).catch(e => console.error(e));
        };

        // ==========================================
        // GESTOR DOS CRONÓMETROS DOS SLOTS
        // ==========================================
        function atualizarCronometros() {
            const agora = Math.floor(Date.now() / 1000);
            const cards = document.querySelectorAll(".slot-card");

            cards.forEach(card => {
                const status = card.getAttribute("data-status");
                const fim = parseInt(card.getAttribute("data-fim"), 10);
                const timerDisplay = card.querySelector(".timer-display");

                if (!status || !fim || status === "Livre" || status === "Ativo") return;

                const tempoRestante = fim - agora;

                if (status === "EmConstrucao") {
                    if (tempoRestante > 0) {
                        if (timerDisplay) timerDisplay.innerText = `⏳ A Instalar: ${tempoRestante}s`;
                    } else {
                        // Construção Acabou -> Recarrega para gerar recursos
                        window.location.reload();
                    }
                } else if (status === "CooldownVenda") {
                    if (tempoRestante > 0) {
                        if (timerDisplay) timerDisplay.innerText = `🔒 Bloqueado: ${tempoRestante}s`;
                    } else {
                        // Cooldown de Venda Acabou -> Recarrega para poder comprar
                        window.location.reload();
                    }
                }
            });
        }

        atualizarCronometros();
        setInterval(atualizarCronometros, 1000);

        // ==========================================
        // LOGOUT
        // ==========================================
        const btnLogout = document.getElementById('btn-logout');
        if (btnLogout) {
            btnLogout.addEventListener('click', function() {
                guardarProgresso().then(() => window.location.href = '/logout')
                                  .catch(() => window.location.href = '/logout');
            });
        }
    }
});