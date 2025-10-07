// Chat application JavaScript
class ChatApp {
    constructor() {
        this.messageInput = document.getElementById('messageInput');
        this.sendButton = document.getElementById('sendButton');
        this.clearButton = document.getElementById('clearButton');
        this.chatMessages = document.getElementById('chatMessages');
        this.statusText = document.getElementById('statusText');
        this.statusIndicator = document.getElementById('statusIndicator');
        this.charCount = document.querySelector('.char-count');
        
        this.apiBaseUrl = window.location.origin;
        this.isLoading = false;
        
        this.initializeEventListeners();
        this.updateWelcomeTime();
        this.checkApiHealth();
    }

    initializeEventListeners() {
        // Send button click
        this.sendButton.addEventListener('click', () => this.sendMessage());
        
        // Enter key to send (Shift+Enter for new line)
        this.messageInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });
        
        // Input changes
        this.messageInput.addEventListener('input', () => {
            this.updateCharCount();
            this.updateSendButton();
            this.autoResize();
        });
        
        // Clear chat
        this.clearButton.addEventListener('click', () => this.clearChat());
        
        // Initial setup
        this.updateCharCount();
        this.updateSendButton();
    }

    updateWelcomeTime() {
        const welcomeTimeElement = document.getElementById('welcomeTime');
        if (welcomeTimeElement) {
            welcomeTimeElement.textContent = new Date().toLocaleTimeString();
        }
    }

    async checkApiHealth() {
        try {
            const response = await fetch(`${this.apiBaseUrl}/health`);
            if (response.ok) {
                this.updateStatus('Ready', 'ready');
            } else {
                this.updateStatus('API Error', 'error');
            }
        } catch (error) {
            this.updateStatus('Connection Error', 'error');
            console.error('Health check failed:', error);
        }
    }

    updateStatus(text, type = 'ready') {
        this.statusText.textContent = text;
        const statusDot = this.statusIndicator.querySelector('.status-dot');
        statusDot.className = `status-dot ${type}`;
    }

    updateCharCount() {
        const length = this.messageInput.value.length;
        this.charCount.textContent = `${length}/2000`;
        
        if (length > 1800) {
            this.charCount.style.color = '#dc3545';
        } else if (length > 1500) {
            this.charCount.style.color = '#ffc107';
        } else {
            this.charCount.style.color = '#666';
        }
    }

    updateSendButton() {
        const hasText = this.messageInput.value.trim().length > 0;
        this.sendButton.disabled = !hasText || this.isLoading;
    }

    autoResize() {
        this.messageInput.style.height = 'auto';
        this.messageInput.style.height = Math.min(this.messageInput.scrollHeight, 120) + 'px';
    }

    async sendMessage() {
        const message = this.messageInput.value.trim();
        if (!message || this.isLoading) return;

        // Add user message to chat
        this.addMessage(message, 'user');
        
        // Clear input
        this.messageInput.value = '';
        this.updateCharCount();
        this.updateSendButton();
        this.autoResize();

        // Show loading state
        this.setLoading(true);
        const loadingMessageId = this.addLoadingMessage();

        try {
            // Send message to API
            const response = await fetch(`${this.apiBaseUrl}/chat`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    message: message,
                    context: null
                })
            });

            // Remove loading message
            this.removeMessage(loadingMessageId);

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(errorData.detail || `HTTP ${response.status}`);
            }

            const data = await response.json();
            
            // Add assistant response
            this.addMessage(data.response, 'assistant');
            this.updateStatus('Ready', 'ready');

        } catch (error) {
            // Remove loading message
            this.removeMessage(loadingMessageId);
            
            // Add error message
            const errorMessage = `Sorry, I encountered an error: ${error.message}`;
            this.addMessage(errorMessage, 'assistant', true);
            this.updateStatus('Error occurred', 'error');
            
            console.error('Chat error:', error);
        } finally {
            this.setLoading(false);
        }
    }

    addMessage(content, sender, isError = false) {
        const messageId = 'msg-' + Date.now() + '-' + Math.random().toString(36).substr(2, 9);
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}-message`;
        messageDiv.id = messageId;
        
        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';
        
        if (isError) {
            contentDiv.style.background = '#f8d7da';
            contentDiv.style.color = '#721c24';
            contentDiv.style.border = '1px solid #f5c6cb';
        }
        
        if (sender === 'user') {
            contentDiv.innerHTML = `<strong>You:</strong> ${this.escapeHtml(content)}`;
        } else {
            contentDiv.innerHTML = `<strong>Assistant:</strong> ${this.escapeHtml(content)}`;
        }
        
        const timeDiv = document.createElement('div');
        timeDiv.className = 'message-time';
        timeDiv.textContent = new Date().toLocaleTimeString();
        
        messageDiv.appendChild(contentDiv);
        messageDiv.appendChild(timeDiv);
        
        this.chatMessages.appendChild(messageDiv);
        this.scrollToBottom();
        
        return messageId;
    }

    addLoadingMessage() {
        const messageId = 'loading-' + Date.now();
        const messageDiv = document.createElement('div');
        messageDiv.className = 'message assistant-message';
        messageDiv.id = messageId;
        
        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content loading-message';
        contentDiv.innerHTML = `
            <strong>Assistant:</strong> 
            <span>Thinking</span>
            <div class="loading-dots">
                <span></span>
                <span></span>
                <span></span>
            </div>
        `;
        
        messageDiv.appendChild(contentDiv);
        this.chatMessages.appendChild(messageDiv);
        this.scrollToBottom();
        
        return messageId;
    }

    removeMessage(messageId) {
        const messageElement = document.getElementById(messageId);
        if (messageElement) {
            messageElement.remove();
        }
    }

    setLoading(loading) {
        this.isLoading = loading;
        this.updateSendButton();
        
        if (loading) {
            this.updateStatus('Processing...', 'loading');
        } else {
            this.updateStatus('Ready', 'ready');
        }
    }

    async clearChat() {
        if (confirm('Are you sure you want to clear the chat history?')) {
            try {
                // Clear on server
                await fetch(`${this.apiBaseUrl}/agent/clear-history`, {
                    method: 'POST'
                });
                
                // Clear UI (keep welcome message)
                const messages = this.chatMessages.querySelectorAll('.message:not(.assistant-message:first-child)');
                messages.forEach(msg => msg.remove());
                
                this.updateStatus('Chat cleared', 'ready');
                
            } catch (error) {
                console.error('Failed to clear chat:', error);
                this.updateStatus('Clear failed', 'error');
            }
        }
    }

    scrollToBottom() {
        this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// Initialize the chat app when the page loads
document.addEventListener('DOMContentLoaded', () => {
    new ChatApp();
});

// Handle page visibility changes
document.addEventListener('visibilitychange', () => {
    if (!document.hidden) {
        // Page became visible, check API health
        setTimeout(() => {
            if (window.chatApp) {
                window.chatApp.checkApiHealth();
            }
        }, 1000);
    }
});

// Store chat app instance globally for debugging
window.addEventListener('load', () => {
    if (!window.chatApp) {
        window.chatApp = new ChatApp();
    }
});