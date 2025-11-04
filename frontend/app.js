// MultiLLM Router Frontend Application
class MultiLLMChat {
    constructor() {
        this.apiUrl = 'http://localhost:8000';
        this.currentConversationId = null;
        this.availableModels = [];
        this.recognition = null;
        this.isRecording = false;
        
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.checkHealth();
        this.loadApiUrl();
    }

    setupEventListeners() {
        const sendBtn = document.getElementById('sendBtn');
        const messageInput = document.getElementById('messageInput');
        const clearBtn = document.getElementById('clearBtn');
        const connectBtn = document.getElementById('connectBtn');
        const modelsBtn = document.getElementById('modelsBtn');
        const apiUrlInput = document.getElementById('apiUrl');
        const speechBtn = document.getElementById('speechBtn');

        sendBtn.addEventListener('click', () => this.sendMessage());
        
        messageInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });

        clearBtn.addEventListener('click', () => this.clearChat());
        connectBtn.addEventListener('click', () => this.connect());
        modelsBtn.addEventListener('click', () => this.loadModels());
        
        apiUrlInput.addEventListener('change', (e) => {
            this.apiUrl = e.target.value.trim() || 'http://localhost:8000';
            this.saveApiUrl();
            this.checkHealth();
        });

        // Initialize speech recognition
        this.initSpeechRecognition();
        speechBtn.addEventListener('click', () => this.toggleSpeechRecognition());
    }

    saveApiUrl() {
        localStorage.setItem('multillm_api_url', this.apiUrl);
    }

    loadApiUrl() {
        const saved = localStorage.getItem('multillm_api_url');
        if (saved) {
            this.apiUrl = saved;
            document.getElementById('apiUrl').value = saved;
        }
    }

    async connect() {
        await this.checkHealth();
        await this.loadModels();
    }

    async checkHealth() {
        const statusDiv = document.getElementById('systemStatus');
        statusDiv.innerHTML = '<p class="info-placeholder">Checking...</p>';

        try {
            const response = await fetch(`${this.apiUrl}/api/v1/health`);
            const data = await response.json();

            statusDiv.innerHTML = `
                <div class="status-item">
                    <span>API Status</span>
                    <span class="status-badge online">Online</span>
                </div>
                <div class="status-item">
                    <span>Version</span>
                    <span>${data.version || 'N/A'}</span>
                </div>
            `;
        } catch (error) {
            statusDiv.innerHTML = `
                <div class="status-item">
                    <span>API Status</span>
                    <span class="status-badge offline">Offline</span>
                </div>
                <div class="error-message">
                    Cannot connect to API at ${this.apiUrl}
                </div>
            `;
        }
    }

    formatUptime(seconds) {
        if (!seconds) return 'N/A';
        const hours = Math.floor(seconds / 3600);
        const minutes = Math.floor((seconds % 3600) / 60);
        const secs = Math.floor(seconds % 60);
        return `${hours}h ${minutes}m ${secs}s`;
    }

    async loadModels() {
        const modelsDiv = document.getElementById('modelsList');
        modelsDiv.innerHTML = '<p class="info-placeholder">Loading...</p>';

        try {
            const response = await fetch(`${this.apiUrl}/api/v1/models`);
            const data = await response.json();

            // Handle both array and object responses
            const models = Array.isArray(data) ? data : (data.models || []);
            this.availableModels = models;

            if (models.length === 0) {
                modelsDiv.innerHTML = '<p class="info-placeholder">No models available</p>';
                return;
            }

            modelsDiv.innerHTML = models.map(model => `
                <div class="models-list-item">
                    <strong>${model.name || model.model_id || 'Unknown'}</strong>
                    <small>${model.provider || 'N/A'} • ${model.status || 'Available'}</small>
                </div>
            `).join('');
        } catch (error) {
            modelsDiv.innerHTML = `
                <p class="info-placeholder">Error loading models</p>
                <div class="error-message">${error.message}</div>
            `;
        }
    }

    async sendMessage() {
        const messageInput = document.getElementById('messageInput');
        const message = messageInput.value.trim();
        const streamToggle = document.getElementById('streamToggle').checked;

        if (!message) return;

        // Disable input while sending
        messageInput.disabled = true;
        document.getElementById('sendBtn').disabled = true;

        // Add user message to chat
        this.addMessage('user', message);

        // Clear input
        messageInput.value = '';

        try {
            if (streamToggle) {
                await this.sendStreamingMessage(message);
            } else {
                await this.sendRegularMessage(message);
            }
        } catch (error) {
            this.addMessage('assistant', `Error: ${error.message}`, null, true);
        } finally {
            messageInput.disabled = false;
            document.getElementById('sendBtn').disabled = false;
            messageInput.focus();
        }
    }

    async sendRegularMessage(message) {
        const loadingId = this.addMessage('assistant', '<div class="loading"></div> Loading...', null, false, true);

        try {
            const response = await fetch(`${this.apiUrl}/api/v1/chat`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    message: message,
                    conversation_id: this.currentConversationId,
                    stream: false
                })
            });

            if (!response.ok) {
                const error = await response.json().catch(() => ({ detail: response.statusText }));
                throw new Error(error.detail || `HTTP ${response.status}`);
            }

            const data = await response.json();

            // Update conversation ID if provided
            if (data.conversation_id) {
                this.currentConversationId = data.conversation_id;
            }

            // Remove loading message and add actual response
            this.removeMessage(loadingId);
            this.addMessage(
                'assistant',
                data.response || data.content || 'No response received',
                {
                    model: data.model_used || data.model,
                    provider: data.provider,
                    reason: data.routing_reason,
                    cost: data.cost,
                    responseTime: data.response_time || data.responseTime,
                    analysis: data.analysis
                }
            );

            // Update model info sidebar
            this.updateModelInfo(data);
        } catch (error) {
            this.removeMessage(loadingId);
            throw error;
        }
    }

    async sendStreamingMessage(message) {
        const messageDiv = this.addMessage('assistant', '', null, false, true);
        let fullContent = '';
        let modelInfo = {};

        try {
            const response = await fetch(`${this.apiUrl}/api/v1/chat/stream`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    message: message,
                    conversation_id: this.currentConversationId,
                    stream: true
                })
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }

            const reader = response.body.getReader();
            const decoder = new TextDecoder();

            while (true) {
                const { done, value } = await reader.read();
                if (done) break;

                const chunk = decoder.decode(value);
                const lines = chunk.split('\n');

                for (const line of lines) {
                    if (line.startsWith('data: ')) {
                        try {
                            const data = JSON.parse(line.slice(6));

                            if (data.type === 'metadata') {
                                modelInfo = {
                                    model: data.model,
                                    provider: data.provider,
                                    reason: data.reasoning,
                                    analysis: data.analysis
                                };
                                this.updateModelInfo(modelInfo);
                            } else if (data.type === 'chunk') {
                                fullContent += data.content;
                                this.updateStreamingMessage(messageDiv, fullContent, modelInfo);
                            } else if (data.type === 'done') {
                                // Finalize message
                                if (data.model) {
                                    modelInfo.model = data.model;
                                }
                                this.updateStreamingMessage(messageDiv, fullContent, modelInfo, true);
                            } else if (data.type === 'error') {
                                throw new Error(data.error || data.content || 'Streaming error');
                            }
                        } catch (e) {
                            // Skip malformed JSON
                            if (e instanceof SyntaxError) continue;
                            throw e;
                        }
                    }
                }
            }
        } catch (error) {
            this.updateStreamingMessage(messageDiv, `Error: ${error.message}`, null, true);
            throw error;
        }
    }

    addMessage(role, content, meta = null, isError = false, isLoading = false) {
        const messagesDiv = document.getElementById('chatMessages');
        
        // Remove welcome message if it exists
        const welcomeMsg = messagesDiv.querySelector('.welcome-message');
        if (welcomeMsg) {
            welcomeMsg.remove();
        }

        const messageId = `msg-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${role}`;
        messageDiv.id = messageId;

        let metaHtml = '';
        if (meta && !isLoading) {
            metaHtml = `
                <div class="message-meta">
                    ${meta.model ? `<div class="meta-item"><strong>Model:</strong> ${meta.model}</div>` : ''}
                    ${meta.provider ? `<div class="meta-item"><strong>Provider:</strong> ${meta.provider}</div>` : ''}
                    ${meta.responseTime ? `<div class="meta-item"><strong>Time:</strong> ${meta.responseTime.toFixed(2)}s</div>` : ''}
                    ${meta.cost !== undefined ? `<div class="meta-item"><strong>Cost:</strong> $${meta.cost.toFixed(4)}</div>` : ''}
                </div>
            `;
        }

        messageDiv.innerHTML = `
            <div class="message-header">${role === 'user' ? 'You' : 'Assistant'}</div>
            <div class="message-content">${content}</div>
            ${metaHtml}
        `;

        if (isError) {
            messageDiv.classList.add('error');
        }

        messagesDiv.appendChild(messageDiv);
        messagesDiv.scrollTop = messagesDiv.scrollHeight;

        return messageId;
    }

    updateStreamingMessage(messageId, content, meta = null, isComplete = false) {
        const messageDiv = typeof messageId === 'string' 
            ? document.getElementById(messageId) 
            : messageId;
        
        if (!messageDiv) return;

        let metaHtml = '';
        if (meta && isComplete) {
            metaHtml = `
                <div class="message-meta">
                    ${meta.model ? `<div class="meta-item"><strong>Model:</strong> ${meta.model}</div>` : ''}
                    ${meta.provider ? `<div class="meta-item"><strong>Provider:</strong> ${meta.provider}</div>` : ''}
                </div>
            `;
        }

        const contentDiv = messageDiv.querySelector('.message-content');
        if (contentDiv) {
            contentDiv.textContent = content;
            if (!isComplete) {
                contentDiv.innerHTML = content + '<span class="loading"></span>';
            }
        }

        if (isComplete && metaHtml) {
            const metaDiv = messageDiv.querySelector('.message-meta');
            if (metaDiv) {
                metaDiv.outerHTML = metaHtml;
            } else {
                messageDiv.innerHTML += metaHtml;
            }
        }

        const messagesDiv = document.getElementById('chatMessages');
        messagesDiv.scrollTop = messagesDiv.scrollHeight;
    }

    removeMessage(messageId) {
        const messageDiv = document.getElementById(messageId);
        if (messageDiv) {
            messageDiv.remove();
        }
    }

    updateModelInfo(data) {
        const modelInfoDiv = document.getElementById('modelInfo');
        
        if (!data || (!data.model && !data.model_used)) {
            modelInfoDiv.innerHTML = '<p class="info-placeholder">No model selected yet</p>';
            return;
        }

        const model = data.model || data.model_used;
        const provider = data.provider || 'N/A';
        const reason = data.routing_reason || data.reason || 'N/A';

        modelInfoDiv.innerHTML = `
            <div class="model-info-item">
                <div class="model-info-label">Current Model</div>
                <div class="model-info-value">${model}</div>
            </div>
            <div class="model-info-item">
                <div class="model-info-label">Provider</div>
                <div class="model-info-value">${provider}</div>
            </div>
            <div class="model-info-item">
                <div class="model-info-label">Reasoning</div>
                <div class="model-info-value">${reason}</div>
            </div>
            ${data.response_time ? `
                <div class="model-info-item">
                    <div class="model-info-label">Response Time</div>
                    <div class="model-info-value">${data.response_time.toFixed(2)}s</div>
                </div>
            ` : ''}
            ${data.cost !== undefined ? `
                <div class="model-info-item">
                    <div class="model-info-label">Cost</div>
                    <div class="model-info-value">$${data.cost.toFixed(4)}</div>
                </div>
            ` : ''}
        `;
    }

    clearChat() {
        const messagesDiv = document.getElementById('chatMessages');
        messagesDiv.innerHTML = `
            <div class="welcome-message">
                <p>👋 Welcome to MultiLLM Router!</p>
                <p>Start a conversation by typing a message below.</p>
            </div>
        `;
        this.currentConversationId = null;
        document.getElementById('modelInfo').innerHTML = '<p class="info-placeholder">No model selected yet</p>';
    }

    initSpeechRecognition() {
        // Check if browser supports speech recognition
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        
        if (!SpeechRecognition) {
            const speechBtn = document.getElementById('speechBtn');
            speechBtn.disabled = true;
            speechBtn.title = 'Speech recognition not supported in this browser';
            speechBtn.style.opacity = '0.5';
            speechBtn.style.cursor = 'not-allowed';
            return;
        }

        this.recognition = new SpeechRecognition();
        this.recognition.continuous = true;
        this.recognition.interimResults = true;
        this.recognition.lang = 'en-US';

        this.recognition.onstart = () => {
            this.isRecording = true;
            const speechBtn = document.getElementById('speechBtn');
            speechBtn.classList.add('recording');
            speechBtn.title = 'Click to stop recording';
        };

        this.recognition.onend = () => {
            this.isRecording = false;
            const speechBtn = document.getElementById('speechBtn');
            speechBtn.classList.remove('recording');
            speechBtn.title = 'Speech to Text';
        };

        this.recognition.onerror = (event) => {
            console.error('Speech recognition error:', event.error);
            this.isRecording = false;
            const speechBtn = document.getElementById('speechBtn');
            speechBtn.classList.remove('recording');
            speechBtn.title = 'Speech to Text';
            
            let errorMessage = 'Speech recognition error';
            if (event.error === 'no-speech') {
                errorMessage = 'No speech detected. Please try again.';
            } else if (event.error === 'not-allowed') {
                errorMessage = 'Microphone permission denied. Please enable microphone access.';
            } else if (event.error === 'network') {
                errorMessage = 'Network error. Please check your connection.';
            }
            
            this.addMessage('assistant', `⚠️ ${errorMessage}`, null, true);
        };

        this.recognition.onresult = (event) => {
            let interimTranscript = '';
            let finalTranscript = '';

            for (let i = event.resultIndex; i < event.results.length; i++) {
                const transcript = event.results[i][0].transcript;
                if (event.results[i].isFinal) {
                    finalTranscript += transcript + ' ';
                } else {
                    interimTranscript += transcript;
                }
            }

            const messageInput = document.getElementById('messageInput');
            const currentText = messageInput.value;
            
            // Update input with final transcript
            if (finalTranscript) {
                messageInput.value = currentText.trim() + ' ' + finalTranscript.trim();
                messageInput.focus();
                // Auto-scroll textarea to bottom
                messageInput.scrollTop = messageInput.scrollHeight;
            }
        };
    }

    toggleSpeechRecognition() {
        if (!this.recognition) {
            return;
        }

        if (this.isRecording) {
            this.recognition.stop();
        } else {
            try {
                this.recognition.start();
            } catch (error) {
                console.error('Failed to start speech recognition:', error);
                this.addMessage('assistant', '⚠️ Failed to start speech recognition. Please try again.', null, true);
            }
        }
    }
}

// Initialize the chat application when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    new MultiLLMChat();
});
