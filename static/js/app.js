// Document AI Processor - Frontend Application

class DocumentAIProcessor {
    constructor() {
        this.currentSessionId = null;
        this.statusCheckInterval = null;
        this.initializeEventListeners();
    }

    initializeEventListeners() {
        // File upload
        document.getElementById('browseBtn').addEventListener('click', () => {
            document.getElementById('fileInput').click();
        });

        document.getElementById('fileInput').addEventListener('change', (e) => {
            this.handleFileSelection(e.target.files);
        });

        // Drag and drop
        const uploadArea = document.querySelector('.border-dashed');
        uploadArea.addEventListener('dragover', (e) => {
            e.preventDefault();
            uploadArea.classList.add('border-blue-400', 'bg-blue-50');
        });

        uploadArea.addEventListener('dragleave', (e) => {
            e.preventDefault();
            uploadArea.classList.remove('border-blue-400', 'bg-blue-50');
        });

        uploadArea.addEventListener('drop', (e) => {
            e.preventDefault();
            uploadArea.classList.remove('border-blue-400', 'bg-blue-50');
            this.handleFileSelection(e.dataTransfer.files);
        });

        // Form submission
        document.getElementById('uploadForm').addEventListener('submit', (e) => {
            e.preventDefault();
            this.uploadFiles();
        });

        // Summary generation
        document.getElementById('generateSummaryBtn').addEventListener('click', () => {
            this.generateSummary();
        });

        // Quiz generation
        document.getElementById('generateQuizBtn').addEventListener('click', () => {
            this.generateQuiz();
        });

        // Save session
        document.getElementById('saveSessionBtn').addEventListener('click', () => {
            this.saveSession();
        });

        // History modal
        document.getElementById('historyBtn').addEventListener('click', () => {
            this.showHistory();
        });

        document.getElementById('closeHistoryBtn').addEventListener('click', () => {
            this.hideHistory();
        });

        // Close modal on outside click
        document.getElementById('historyModal').addEventListener('click', (e) => {
            if (e.target === e.currentTarget) {
                this.hideHistory();
            }
        });
    }

    handleFileSelection(files) {
        if (files.length === 0) return;

        const fileList = document.getElementById('fileList');
        fileList.innerHTML = '';
        fileList.classList.remove('hidden');

        Array.from(files).forEach(file => {
            const fileItem = this.createFileItem(file);
            fileList.appendChild(fileItem);
        });

        // Enable upload button
        document.getElementById('uploadBtn').disabled = false;
    }

    createFileItem(file) {
        const fileItem = document.createElement('div');
        fileItem.className = 'file-item flex items-center justify-between p-3 bg-gray-50 rounded-lg';
        
        const fileIcon = this.getFileIcon(file.name);
        const fileSize = this.formatFileSize(file.size);
        
        fileItem.innerHTML = `
            <div class="flex items-center">
                <i class="file-icon ${fileIcon.class} ${fileIcon.color}"></i>
                <div>
                    <p class="font-medium text-gray-700">${file.name}</p>
                    <p class="text-sm text-gray-500">${fileSize}</p>
                </div>
            </div>
            <div class="text-sm text-gray-400">
                Ready to upload
            </div>
        `;
        
        return fileItem;
    }

    getFileIcon(filename) {
        const ext = filename.toLowerCase().split('.').pop();
        
        if (['pdf'].includes(ext)) {
            return { class: 'fas fa-file-pdf', color: 'pdf' };
        } else if (['docx', 'doc'].includes(ext)) {
            return { class: 'fas fa-file-word', color: 'docx' };
        } else if (['pptx', 'ppt'].includes(ext)) {
            return { class: 'fas fa-file-powerpoint', color: 'pptx' };
        } else if (['mp3', 'wav', 'm4a', 'flac', 'ogg', 'aac'].includes(ext)) {
            return { class: 'fas fa-music', color: 'audio' };
        } else {
            return { class: 'fas fa-file', color: 'text-gray-400' };
        }
    }

    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    async uploadFiles() {
        const fileInput = document.getElementById('fileInput');
        const files = fileInput.files;
        
        if (files.length === 0) {
            this.showToast('Please select files to upload', 'error');
            return;
        }

        this.showLoadingOverlay();
        
        try {
            const formData = new FormData();
            Array.from(files).forEach(file => {
                formData.append('files', file);
            });

            const response = await fetch('/upload', {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                throw new Error(`Upload failed: ${response.statusText}`);
            }

            const result = await response.json();
            this.currentSessionId = result.session_id;
            
            this.showToast('Files uploaded successfully!', 'success');
            this.showProcessingSection();
            this.startStatusChecking();
            
            // Reset form
            fileInput.value = '';
            document.getElementById('fileList').classList.add('hidden');
            document.getElementById('uploadBtn').disabled = true;
            
        } catch (error) {
            console.error('Upload error:', error);
            this.showToast(`Upload failed: ${error.message}`, 'error');
        } finally {
            this.hideLoadingOverlay();
        }
    }

    showProcessingSection() {
        document.getElementById('uploadSection').classList.add('hidden');
        document.getElementById('processingSection').classList.remove('hidden');
        this.updateProcessingStatus();
    }

    async updateProcessingStatus() {
        if (!this.currentSessionId) return;

        try {
            const response = await fetch(`/status/${this.currentSessionId}`);
            if (!response.ok) throw new Error('Failed to get status');
            
            const status = await response.json();
            this.displayProcessingStatus(status);
            
            if (status.status === 'completed') {
                this.showResultsSection();
                this.stopStatusChecking();
            }
            
        } catch (error) {
            console.error('Status check error:', error);
        }
    }

    displayProcessingStatus(status) {
        const statusContainer = document.getElementById('processingStatus');
        statusContainer.innerHTML = '';

        status.files.forEach(file => {
            const fileStatus = document.createElement('div');
            fileStatus.className = 'flex items-center justify-between p-3 bg-gray-50 rounded-lg';
            
            const statusClass = this.getStatusClass(file.status);
            
            fileStatus.innerHTML = `
                <div class="flex items-center">
                    <i class="fas fa-file mr-3 text-gray-400"></i>
                    <div>
                        <p class="font-medium text-gray-700">${file.filename}</p>
                        <p class="text-sm text-gray-500">${file.file_type.toUpperCase()}</p>
                    </div>
                </div>
                <span class="status-badge ${statusClass}">${file.status}</span>
            `;
            
            statusContainer.appendChild(fileStatus);
        });
    }

    getStatusClass(status) {
        switch (status) {
            case 'pending': return 'pending';
            case 'processing': return 'processing';
            case 'completed': return 'completed';
            case 'failed': return 'failed';
            default: return 'pending';
        }
    }

    startStatusChecking() {
        this.statusCheckInterval = setInterval(() => {
            this.updateProcessingStatus();
        }, 2000);
    }

    stopStatusChecking() {
        if (this.statusCheckInterval) {
            clearInterval(this.statusCheckInterval);
            this.statusCheckInterval = null;
        }
    }

    showResultsSection() {
        document.getElementById('processingSection').classList.add('hidden');
        document.getElementById('resultsSection').classList.remove('hidden');
    }

    async generateSummary() {
        if (!this.currentSessionId) return;

        const summaryType = document.getElementById('summaryType').value;
        this.showLoadingOverlay();

        try {
            const response = await fetch(`/summary/${this.currentSessionId}?summary_type=${summaryType}`);
            if (!response.ok) throw new Error('Failed to generate summary');

            const summary = await response.json();
            this.displaySummary(summary.content);
            
        } catch (error) {
            console.error('Summary generation error:', error);
            this.showToast('Failed to generate summary', 'error');
        } finally {
            this.hideLoadingOverlay();
        }
    }

    displaySummary(content) {
        document.getElementById('summaryContent').textContent = content;
        document.getElementById('summaryResult').classList.remove('hidden');
    }

    async generateQuiz() {
        if (!this.currentSessionId) return;

        const questionCount = document.getElementById('questionCount').value;
        this.showLoadingOverlay();

        try {
            const response = await fetch(`/quiz/${this.currentSessionId}?question_count=${questionCount}`);
            if (!response.ok) throw new Error('Failed to generate quiz');

            const quiz = await response.json();
            this.displayQuiz(quiz.questions);
            
        } catch (error) {
            console.error('Quiz generation error:', error);
            this.showToast('Failed to generate quiz', 'error');
        } finally {
            this.hideLoadingOverlay();
        }
    }

    displayQuiz(questions) {
        const quizContent = document.getElementById('quizContent');
        quizContent.innerHTML = '';

        questions.forEach((question, index) => {
            const questionDiv = document.createElement('div');
            questionDiv.className = 'quiz-question border rounded-lg p-4 bg-white';
            
            const optionsHtml = Object.entries(question.options)
                .map(([key, value]) => `
                    <div class="flex items-center mb-2">
                        <input type="radio" name="q${index}" value="${key}" class="mr-2">
                        <label class="text-sm text-gray-700">${key}. ${value}</label>
                    </div>
                `).join('');

            questionDiv.innerHTML = `
                <h4 class="font-medium text-gray-700 mb-3">Question ${index + 1}:</h4>
                <p class="text-gray-600 mb-3">${question.question}</p>
                <div class="space-y-2">
                    ${optionsHtml}
                </div>
                <div class="mt-3 p-2 bg-blue-50 rounded text-sm text-blue-800">
                    <strong>Correct Answer:</strong> ${question.correct_answer}
                    <br><strong>Explanation:</strong> ${question.explanation}
                </div>
            `;
            
            quizContent.appendChild(questionDiv);
        });

        document.getElementById('quizResult').classList.remove('hidden');
    }

    async saveSession() {
        if (!this.currentSessionId) return;

        const sessionName = document.getElementById('sessionName').value.trim();
        if (!sessionName) {
            this.showToast('Please enter a session name', 'error');
            return;
        }

        try {
            const formData = new FormData();
            formData.append('session_name', sessionName);

            const response = await fetch(`/save-session/${this.currentSessionId}`, {
                method: 'POST',
                body: formData
            });

            if (!response.ok) throw new Error('Failed to save session');

            this.showToast('Session saved successfully!', 'success');
            document.getElementById('sessionName').value = '';
            
        } catch (error) {
            console.error('Save session error:', error);
            this.showToast('Failed to save session', 'error');
        }
    }

    async showHistory() {
        try {
            const response = await fetch('/saved-sessions');
            if (!response.ok) throw new Error('Failed to load history');

            const sessions = await response.json();
            this.displayHistory(sessions);
            document.getElementById('historyModal').classList.remove('hidden');
            
        } catch (error) {
            console.error('History load error:', error);
            this.showToast('Failed to load history', 'error');
        }
    }

    displayHistory(sessions) {
        const historyList = document.getElementById('historyList');
        historyList.innerHTML = '';

        if (sessions.length === 0) {
            historyList.innerHTML = '<p class="text-gray-500 text-center py-4">No saved sessions found</p>';
            return;
        }

        sessions.forEach(session => {
            const sessionItem = document.createElement('div');
            sessionItem.className = 'flex items-center justify-between p-3 bg-gray-50 rounded-lg hover:bg-gray-100 cursor-pointer';
            
            const date = new Date(session.updated_at).toLocaleDateString();
            
            sessionItem.innerHTML = `
                <div>
                    <p class="font-medium text-gray-700">${session.session_name}</p>
                    <p class="text-sm text-gray-500">Last updated: ${date}</p>
                </div>
                <button onclick="app.loadSession('${session.session_id}')" class="text-blue-600 hover:text-blue-800">
                    <i class="fas fa-eye mr-1"></i>View
                </button>
            `;
            
            historyList.appendChild(sessionItem);
        });
    }

    hideHistory() {
        document.getElementById('historyModal').classList.add('hidden');
    }

    async loadSession(sessionId) {
        this.currentSessionId = sessionId;
        this.hideHistory();
        
        // Show processing section and check status
        this.showProcessingSection();
        await this.updateProcessingStatus();
        
        // If completed, show results
        try {
            const response = await fetch(`/status/${sessionId}`);
            if (response.ok) {
                const status = await response.json();
                if (status.status === 'completed') {
                    this.showResultsSection();
                }
            }
        } catch (error) {
            console.error('Error loading session:', error);
        }
    }

    showLoadingOverlay() {
        document.getElementById('loadingOverlay').classList.remove('hidden');
    }

    hideLoadingOverlay() {
        document.getElementById('loadingOverlay').classList.add('hidden');
    }

    showToast(message, type = 'info') {
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        toast.textContent = message;
        
        document.body.appendChild(toast);
        
        setTimeout(() => {
            toast.remove();
        }, 3000);
    }
}

// Initialize the application
const app = new DocumentAIProcessor();

// Global error handler
window.addEventListener('error', (e) => {
    console.error('Global error:', e.error);
    app.showToast('An unexpected error occurred', 'error');
});

// Handle page visibility change to pause status checking when tab is hidden
document.addEventListener('visibilitychange', () => {
    if (document.hidden) {
        app.stopStatusChecking();
    } else if (app.currentSessionId && document.getElementById('processingSection').classList.contains('hidden') === false) {
        app.startStatusChecking();
    }
});