const dropZone = document.getElementById('dropZone');
const fileInput = document.getElementById('fileInput');
const fileList = document.getElementById('fileList');
const uploadBtn = document.getElementById('uploadBtn');
const clearBtn = document.getElementById('clearBtn');
const progressContainer = document.getElementById('progressContainer');
const progressBar = document.getElementById('progressBar');
const progressText = document.getElementById('progressText');
const statusMessage = document.getElementById('statusMessage');

let selectedFiles = [];

// API Configuration
const API_ENDPOINT = '/api/debit';

// File validation
function validateFile(file) {
    const validTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp'];
    const maxSize = 10 * 1024 * 1024; // 10MB

    if (!validTypes.includes(file.type)) {
        return { valid: false, error: 'Tipo de arquivo não suportado. Use apenas imagens.' };
    }

    if (file.size > maxSize) {
        return { valid: false, error: 'Arquivo muito grande. Máximo: 10MB.' };
    }

    return { valid: true };
}

// Format file size
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i];
}

// Update file list UI
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
            <button class="file-remove" onclick="removeFile(${index})">Remover</button>
        `;
        fileList.appendChild(fileItem);
    });
}

// Remove file
function removeFile(index) {
    selectedFiles.splice(index, 1);
    updateFileList();
}

// Handle file selection
function handleFiles(files) {
    const fileArray = Array.from(files);
    
    for (const file of fileArray) {
        const validation = validateFile(file);
        
        if (!validation.valid) {
            showStatus(validation.error, 'error');
            continue;
        }

        // Check for duplicates
        const isDuplicate = selectedFiles.some(f => 
            f.name === file.name && f.size === file.size
        );

        if (!isDuplicate) {
            selectedFiles.push(file);
        }
    }

    updateFileList();
}

// Convert file to base64
function toBase64(file) {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.readAsDataURL(file);
        reader.onload = () => resolve(reader.result);
        reader.onerror = error => reject(error);
    });
}

// Show status message
function showStatus(message, type) {
    statusMessage.textContent = message;
    statusMessage.className = `status-message visible ${type}`;
    
    if (type === 'success') {
        setTimeout(() => {
            statusMessage.classList.remove('visible');
        }, 5000);
    }
}

// Upload files
async function uploadFiles() {
    if (selectedFiles.length === 0) return;

    uploadBtn.disabled = true;
    clearBtn.disabled = true;
    progressContainer.classList.add('visible');
    statusMessage.classList.remove('visible');

    try {
        const total = selectedFiles.length;
        let completed = 0;

        for (const file of selectedFiles) {
            progressText.textContent = `Processando ${completed + 1} de ${total}...`;
            progressBar.style.width = `${(completed / total) * 100}%`;

            // Convert to base64
            const base64Data = await toBase64(file);

            // Send to API
            const response = await fetch(API_ENDPOINT, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    data: base64Data,
                    filename: file.name
                })
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.error || 'Erro ao enviar arquivo');
            }

            completed++;
            progressBar.style.width = `${(completed / total) * 100}%`;
        }

        progressText.textContent = 'Upload concluído!';
        showStatus(`${total} arquivo(s) enviado(s) com sucesso! ✓`, 'success');
        
        // Clear files after successful upload
        selectedFiles = [];
        updateFileList();

    } catch (error) {
        console.error('Upload error:', error);
        showStatus(`Erro: ${error.message}`, 'error');
    } finally {
        uploadBtn.disabled = false;
        clearBtn.disabled = false;
        
        setTimeout(() => {
            progressContainer.classList.remove('visible');
            progressBar.style.width = '0';
        }, 2000);
    }
}

// Clear all files
function clearFiles() {
    selectedFiles = [];
    updateFileList();
    statusMessage.classList.remove('visible');
}

// Event listeners
dropZone.addEventListener('click', () => fileInput.click());

dropZone.addEventListener('dragover', (e) => {
    e.preventDefault();
    dropZone.classList.add('dragover');
});

dropZone.addEventListener('dragleave', () => {
    dropZone.classList.remove('dragover');
});

dropZone.addEventListener('drop', (e) => {
    e.preventDefault();
    dropZone.classList.remove('dragover');
    handleFiles(e.dataTransfer.files);
});

fileInput.addEventListener('change', (e) => {
    handleFiles(e.target.files);
    fileInput.value = ''; // Reset input
});

uploadBtn.addEventListener('click', uploadFiles);
clearBtn.addEventListener('click', clearFiles);

// Prevent default drag behavior on document
document.addEventListener('dragover', (e) => e.preventDefault());
document.addEventListener('drop', (e) => e.preventDefault());
