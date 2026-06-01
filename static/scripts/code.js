// Esperar que o DOM esteja carregado (Lab 04)
document.addEventListener('DOMContentLoaded', function () {
    // 1. O JavaScript vai procurar o input e o ícone do olho
    const passwordInput = document.getElementById('password-input');
    const togglePassword = document.getElementById('toggle-password');

    // Verifica se os elementos existem nesta página antes de adicionar o evento
    if (togglePassword && passwordInput) {
        // 2. Fica à espera que alguém clique no olho
        togglePassword.addEventListener('click', function () {
            
            // 3. Verifica se a password está escondida
            if (passwordInput.type === 'password') {
                // Se estiver, muda para texto normal e muda o ícone
                passwordInput.type = 'text';
                togglePassword.innerHTML = '<img src="/static/images/password_escondida.png" alt="Esconder Password" width="24">'; 

            } else {
                // Se não, volta a esconder em forma de password e repõe o olho normal
                passwordInput.type = 'password';
                togglePassword.innerHTML = '<img src="/static/images/hacker_password.png" alt="Mostrar Password" width="24">';                
            }
        });
    }
});