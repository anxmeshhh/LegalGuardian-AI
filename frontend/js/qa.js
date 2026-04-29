/**
 * LegalGuardian AI — Q&A Panel Controller
 * Manages the interactive question & answer chat interface
 */

const QA = {
    /** Initialize Q&A panel */
    init() {
        const input = document.getElementById('qa-input');
        const sendBtn = document.getElementById('qa-send-btn');
        
        // Send on button click
        sendBtn.addEventListener('click', () => this.handleSend());
        
        // Send on Enter key
        input.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.handleSend();
            }
        });
    },

    /** Enable Q&A after analysis */
    enable() {
        document.getElementById('qa-input').disabled = false;
        document.getElementById('qa-send-btn').disabled = false;
    },

    /** Handle sending a question */
    async handleSend() {
        const input = document.getElementById('qa-input');
        const question = input.value.trim();
        
        if (!question || !Results.currentData) return;
        
        // Show user message
        this.addMessage(question, 'user');
        input.value = '';
        
        // Show typing indicator
        const typingId = this.addTyping();
        
        try {
            // Get the contract text
            const contractText = UI.elements.contractText.value;
            
            // Call QA API
            const result = await API.askQuestion(contractText, question);
            
            // Remove typing indicator
            this.removeTyping(typingId);
            
            // Show answer
            let answerHtml = result.answer;
            if (result.confidence > 0) {
                answerHtml += `<span class="qa-confidence">Confidence: ${Math.round(result.confidence * 100)}% · Method: ${result.method}</span>`;
            }
            this.addMessage(answerHtml, 'system', true);
            
        } catch (error) {
            this.removeTyping(typingId);
            this.addMessage(`Sorry, I couldn't process that question. ${error.message}`, 'system', true);
        }
    },

    /** Add a message to the chat */
    addMessage(content, type = 'system', isHtml = false) {
        const container = document.getElementById('qa-messages');
        const msg = document.createElement('div');
        msg.className = `qa-message ${type}`;
        
        const avatar = type === 'user' ? '👤' : '🤖';
        
        msg.innerHTML = `
            <span class="qa-avatar">${avatar}</span>
            <div class="qa-bubble">${isHtml ? content : this.escapeHtml(content)}</div>
        `;
        
        container.appendChild(msg);
        container.scrollTop = container.scrollHeight;
    },

    /** Show typing indicator */
    addTyping() {
        const container = document.getElementById('qa-messages');
        const id = 'typing-' + Date.now();
        const msg = document.createElement('div');
        msg.className = 'qa-message system';
        msg.id = id;
        msg.innerHTML = `
            <span class="qa-avatar">🤖</span>
            <div class="qa-bubble">
                <span class="spinner" style="width:16px;height:16px;border-width:2px;display:inline-block;vertical-align:middle;"></span>
                <span style="margin-left:8px;color:var(--text-muted);">Thinking...</span>
            </div>
        `;
        container.appendChild(msg);
        container.scrollTop = container.scrollHeight;
        return id;
    },

    /** Remove typing indicator */
    removeTyping(id) {
        const el = document.getElementById(id);
        if (el) el.remove();
    },

    /** Escape HTML for user input */
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
};
