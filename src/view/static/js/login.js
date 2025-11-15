// === SCRIPT DO MODAL DE LOGIN ===

// Espera o DOM estar pronto para adicionar os listeners
document.addEventListener('DOMContentLoaded', () => {
    
    const loginForm = document.getElementById('loginForm');
    const loginStatus = document.getElementById('loginStatus');
    const loginBtn = document.getElementById('loginBtn');

    if (loginForm) {
        loginForm.addEventListener('submit', async (e) => {
            e.preventDefault(); // Impede o recarregamento da página

            const username = document.getElementById('username').value;
            const password = document.getElementById('password').value;

            // Mostra feedback no botão
            loginBtn.disabled = true;
            loginBtn.textContent = 'Entrando...';
            
            // Limpa status anterior
            loginStatus.classList.remove('visible', 'error', 'success');
            loginStatus.textContent = '';

            try {
                const response = await fetch('/api/login', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        username: username,
                        password: password
                    })
                });

                const data = await response.json();

                if (response.ok && data.ok) {
                    // Sucesso no login
                    loginStatus.textContent = data.message || 'Login bem-sucedido!';
                    loginStatus.className = 'status-message visible success';
                    
                    // Opcional: redirecionar ou fechar o modal
                    // document.getElementById('loginModal').style.display = 'none';

                } else {
                    // Erro retornado pela API
                    loginStatus.textContent = data.error || 'Usuário ou senha inválidos.';
                    loginStatus.className = 'status-message visible error';
                }

            } catch (error) {
                // Erro de rede ou JSON
                console.error('Erro no login:', error);
                loginStatus.textContent = 'Erro ao conectar. Tente novamente.';
                loginStatus.className = 'status-message visible error';
            } finally {
                // Restaura o botão
                loginBtn.disabled = false;
                loginBtn.textContent = 'Entrar';
            }
        });
    }
});