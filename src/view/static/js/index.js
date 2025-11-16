document.addEventListener('DOMContentLoaded', () => {

    // --- Lógica do Modal de Login ---
    const loginModal = document.getElementById('loginModal');
    const appContent = document.getElementById('appContent');
    const loginForm = document.getElementById('loginForm');
    const loginStatus = document.getElementById('loginStatus');
    const loginBtn = document.getElementById('loginBtn');

    loginForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        loginBtn.disabled = true;
        loginBtn.textContent = 'Entrando...';

        // Limpa status anterior
        loginStatus.classList.add('hidden');
        loginStatus.classList.remove('bg-green-100', 'text-green-700', 'bg-red-100', 'text-red-700');
        loginStatus.textContent = '';

        const username = document.getElementById('username').value;
        const password = document.getElementById('password').value;

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
                loginStatus.classList.remove('hidden');
                loginStatus.classList.add('bg-green-100', 'text-green-700');
                
                // Fecha o modal e mostra o app
                setTimeout(() => {
                    loginModal.classList.add('hidden');
                    appContent.classList.remove('hidden');
                }, 1000);

            } else {
                // Erro retornado pela API
                loginStatus.textContent = data.error || 'Usuário ou senha inválidos.';
                loginStatus.classList.remove('hidden');
                loginStatus.classList.add('bg-red-100', 'text-red-700');
            }

        } catch (error) {
            // Erro de rede ou JSON
            console.error('Erro no login:', error);
            loginStatus.textContent = 'Erro ao conectar. Tente novamente.';
            loginStatus.classList.remove('hidden');
            loginStatus.classList.add('bg-red-100', 'text-red-700');
        } finally {
            // Restaura o botão em caso de erro
            if (!appContent.classList.contains('hidden')) {
                // Não reativar se o login foi bem sucedido e o app está visível
            } else {
                loginBtn.disabled = false;
                loginBtn.textContent = 'Entrar';
            }
        }
    });

    // --- Lógica de Navegação por Abas ---
    const tabs = document.querySelectorAll('.tab-button');
    const panels = document.querySelectorAll('.tab-panel');

    const activeClasses = ['border-blue-600', 'text-blue-600'];
    const inactiveClasses = ['border-transparent', 'text-gray-500', 'hover:text-gray-700', 'hover:border-gray-300'];

    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            const targetPanelId = tab.id.replace('tab-', 'panel-');

            // Desativa todas as abas
            tabs.forEach(t => {
                t.classList.remove(...activeClasses);
                t.classList.add(...inactiveClasses);
                t.setAttribute('aria-current', 'false');
            });

            // Esconde todos os painéis
            panels.forEach(p => {
                p.classList.add('hidden');
            });

            // Ativa a aba clicada
            tab.classList.add(...activeClasses);
            tab.classList.remove(...inactiveClasses);
            tab.setAttribute('aria-current', 'page');

            // Mostra o painel correspondente
            document.getElementById(targetPanelId).classList.remove('hidden');
        });
    });

    // --- Lógica de Máscara de Moeda ---
    function formatCurrency(e) {
        let value = e.target.value.replace(/\D/g, ''); // Remove tudo que não é dígito
        
        if (!value) {
            e.target.value = '';
            return;
        }

        // Converte para número (ex: "12345" -> 123.45)
        let num = parseFloat(value) / 100;

        // Formata como BRL (ex: 123.45 -> "R$ 123,45")
        e.target.value = num.toLocaleString('pt-BR', {
            style: 'currency',
            currency: 'BRL'
        });
    }

    const currencyInputs = document.querySelectorAll('input[inputmode="decimal"]');
    currencyInputs.forEach(input => {
        input.addEventListener('keyup', formatCurrency);
    });

    // --- Helper para converter arquivo para Base64 ---
    function toBase64(file) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.readAsDataURL(file);
            reader.onload = () => resolve(reader.result);
            reader.onerror = error => reject(error);
        });
    }

    // --- Lógica de Feedback e Validação ---
    function showFeedback(elementId, message, type) {
        const feedbackEl = document.getElementById(elementId);
        feedbackEl.textContent = message;
        
        // Remove classes de cor antigas
        feedbackEl.classList.remove('bg-green-100', 'text-green-700', 'bg-red-100', 'text-red-700');

        if (type === 'success') {
            feedbackEl.classList.add('bg-green-100', 'text-green-700');
        } else if (type === 'error') {
            feedbackEl.classList.add('bg-red-100', 'text-red-700');
        }
        
        feedbackEl.classList.remove('hidden');

        // Esconde a mensagem após 5 segundos
        setTimeout(() => {
            feedbackEl.classList.add('hidden');
        }, 5000);
    }

    // --- Lógica do Painel de Débito (baseado em debit.js) ---
    const dropZone = document.getElementById('dropZone');
    const fileInput = document.getElementById('fileInput');
    const fileList = document.getElementById('fileList');
    const uploadBtn = document.getElementById('uploadBtn');
    const clearBtn = document.getElementById('clearBtn');
    const progressContainer = document.getElementById('progressContainer');
    const progressBar = document.getElementById('progressBar');
    const progressText = document.getElementById('progressText');
    const statusMessage = document.getElementById('statusMessage');

    if (dropZone) { // Garante que o código só rode se os elementos existirem
        let selectedFiles = [];
        const API_ENDPOINT_DEBIT = '/api/debit';

        function validateFile(file) {
            const validTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp'];
            const maxSize = 10 * 1024 * 1024; // 10MB
            if (!validTypes.includes(file.type)) return { valid: false, error: 'Tipo de arquivo não suportado.' };
            if (file.size > maxSize) return { valid: false, error: 'Arquivo muito grande (Máx: 10MB).' };
            return { valid: true };
        }

        function formatFileSize(bytes) {
            if (bytes === 0) return '0 Bytes';
            const k = 1024;
            const sizes = ['Bytes', 'KB', 'MB', 'GB'];
            const i = Math.floor(Math.log(bytes) / Math.log(k));
            return `${(bytes / Math.pow(k, i)).toFixed(2)} ${sizes[i]}`;
        }

        function updateFileList() {
            fileList.innerHTML = '';
            if (selectedFiles.length === 0) {
                fileList.classList.remove('visible');
                uploadBtn.disabled = true;
                return;
            }
            fileList.classList.add('visible');
            uploadBtn.disabled = false;
            selectedFiles.forEach((file, index) => {
                const fileItem = document.createElement('div');
                fileItem.className = 'file-item';
                fileItem.innerHTML = `
                    <div class="file-info">
                        <div class="file-name">📄 ${file.name}</div>
                        <div class="file-size">${formatFileSize(file.size)}</div>
                    </div>
                    <button class="file-remove" data-index="${index}">Remover</button>
                `;
                fileList.appendChild(fileItem);
            });
        }

        function removeFile(index) {
            selectedFiles.splice(index, 1);
            updateFileList();
        }

        function handleFiles(files) {
            for (const file of Array.from(files)) {
                const validation = validateFile(file);
                if (!validation.valid) {
                    showStatus(validation.error, 'error');
                    continue;
                }
                const isDuplicate = selectedFiles.some(f => f.name === file.name && f.size === file.size);
                if (!isDuplicate) selectedFiles.push(file);
            }
            updateFileList();
        }

        function showStatus(message, type) {
            statusMessage.textContent = message;
            statusMessage.className = `status-message visible ${type} text-center`;
            setTimeout(() => statusMessage.classList.remove('visible'), 3000);
        }

        async function uploadFiles() {
            if (selectedFiles.length === 0) return;
            uploadBtn.disabled = true;
            clearBtn.disabled = true;
            progressContainer.classList.add('visible');
            statusMessage.classList.remove('visible');

            try {
                const total = selectedFiles.length;
                for (let i = 0; i < total; i++) {
                    const file = selectedFiles[i];
                    progressText.textContent = `Processando ${i + 1} de ${total}...`;
                    progressBar.style.width = `${((i + 1) / total) * 100}%`;
                    const base64Data = await toBase64(file);
                    const response = await fetch(API_ENDPOINT_DEBIT, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ data: base64Data, filename: file.name })
                    });
                    if (!response.ok) {
                        const error = await response.json();
                        throw new Error(error.error || 'Erro ao enviar arquivo');
                    }
                }
                progressText.textContent = 'Upload concluído!';
                showStatus(`${total} arquivo(s) enviado(s) com sucesso! ✓`, 'success');
                selectedFiles = [];
                updateFileList();
            } catch (error) {
                showStatus(`Erro: ${error.message}`, 'error');
            } finally {
                uploadBtn.disabled = false;
                clearBtn.disabled = false;
                setTimeout(() => {
                    progressContainer.classList.remove('visible');
                    progressBar.style.width = '0';
                }, 3000);
            }
        }

        function clearFiles() {
            selectedFiles = [];
            updateFileList();
            statusMessage.classList.remove('visible');
        }

        dropZone.addEventListener('click', () => fileInput.click());
        dropZone.addEventListener('dragover', (e) => { e.preventDefault(); dropZone.classList.add('dragover'); });
        dropZone.addEventListener('dragleave', () => dropZone.classList.remove('dragover'));
        dropZone.addEventListener('drop', (e) => { e.preventDefault(); dropZone.classList.remove('dragover'); handleFiles(e.dataTransfer.files); });
        fileInput.addEventListener('change', (e) => { handleFiles(e.target.files); e.target.value = ''; });
        uploadBtn.addEventListener('click', uploadFiles);
        clearBtn.addEventListener('click', clearFiles);
        fileList.addEventListener('click', (e) => {
            if (e.target.classList.contains('file-remove')) {
                removeFile(parseInt(e.target.dataset.index, 10));
            }
        });
    }

    // Validação do Formulário de Crédito
    document.getElementById('form-credit').addEventListener('submit', async (e) => {
        e.preventDefault();
        const form = e.target;
        const submitButton = form.querySelector('button[type="submit"]');
        const originalButtonText = submitButton.textContent;

        const file = document.getElementById('credit-file').files[0];
        const card = document.getElementById('credit-card').value;

        if (!file || !card) {
            showFeedback('feedback-credit', 'Por favor, anexe um arquivo e selecione um cartão.', 'error');
            return;
        }

        submitButton.disabled = true;
        submitButton.textContent = 'Enviando...';

        try {
            const base64Data = await toBase64(file);

            const response = await fetch('/api/credit', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    data: base64Data,
                    filename: file.name,
                    card: card
                })
            });

            const result = await response.json();

            if (!response.ok) {
                throw new Error(result.error || 'Erro ao enviar o crédito.');
            }

            showFeedback('feedback-credit', 'Crédito adicionado com sucesso!', 'success');
            form.reset();
            document.getElementById('credit-file-name').textContent = '';
        } catch (error) {
            showFeedback('feedback-credit', `Erro: ${error.message}`, 'error');
        } finally {
            submitButton.disabled = false;
            submitButton.textContent = originalButtonText;
        }
    });

    // Validação do Formulário de Entrada
    document.getElementById('form-entry').addEventListener('submit', async (e) => {
        e.preventDefault();
        const form = e.target;
        const submitButton = form.querySelector('button[type="submit"]');
        const originalButtonText = submitButton.textContent;

        const valorRaw = document.getElementById('entry-valor').value;
        const data = document.getElementById('entry-data').value;
        const desc = document.getElementById('entry-desc').value;

        if (!valorRaw || !data) {
            showFeedback('feedback-entry', 'Os campos Valor e Data são obrigatórios.', 'error');
            return;
        }

        // Converte "R$ 1.234,56" para 1234.56
        const valor = parseFloat(valorRaw.replace('R$', '').replace(/\./g, '').replace(',', '.').trim());

        if (isNaN(valor) || valor <= 0) {
            showFeedback('feedback-entry', 'Por favor, insira um valor válido.', 'error');
            return;
        }

        submitButton.disabled = true;
        submitButton.textContent = 'Enviando...';

        try {
            const response = await fetch('/api/salary', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ valor, data, desc })
            });

            const result = await response.json();

            if (!response.ok) {
                throw new Error(result.error || 'Erro ao adicionar entrada.');
            }

            showFeedback('feedback-entry', 'Entrada adicionada com sucesso!', 'success');
            form.reset();
        } catch (error) {
            showFeedback('feedback-entry', `Erro: ${error.message}`, 'error');
        } finally {
            submitButton.disabled = false;
            submitButton.textContent = originalButtonText;
        }
    });

    // --- Lógica para mostrar nome do arquivo selecionado ---
    function setupFileInput(inputId, nameId) {
        const fileInput = document.getElementById(inputId);
        const fileNameEl = document.getElementById(nameId);
        if (fileInput) {
            fileInput.addEventListener('change', (e) => {
                if (e.target.files.length > 0) {
                    fileNameEl.textContent = `Arquivo: ${e.target.files[0].name}`;
                } else {
                    fileNameEl.textContent = '';
                }
            });
        }
    }

    setupFileInput('debit-file', 'debit-file-name');
    setupFileInput('credit-file', 'credit-file-name');

});