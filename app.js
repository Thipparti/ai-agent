# Navigate to frontend scripts folder
cd C:\Users\laxma\OneDrive\Desktop\aiml\ai-research-agent\frontend\scripts

# Create app.js with complete code
@"
class ThinkingLog {
    constructor() {
        this.logContainer = document.getElementById('thinkingLog');
        this.queryInput = document.getElementById('queryInput');
        this.submitBtn = document.getElementById('submitBtn');
        this.clearBtn = document.getElementById('clearLog');
        this.exportBtn = document.getElementById('exportLog');
        this.sampleCards = document.querySelectorAll('.sample-card');
        
        this.logs = [];
        this.eventCount = 0;
        this.apiBaseUrl = 'http://localhost:8000';
        this.useRealAPI = true;
        
        this.init();
    }
    
    async init() {
        // Add event listeners
        this.submitBtn.addEventListener('click', () => this.submitQuery());
        
        if (this.clearBtn) {
            this.clearBtn.addEventListener('click', () => this.clearLog());
        }
        
        if (this.exportBtn) {
            this.exportBtn.addEventListener('click', () => this.exportLog());
        }
        
        // Sample cards
        if (this.sampleCards) {
            this.sampleCards.forEach(card => {
                card.addEventListener('click', (e) => {
                    const query = card.dataset.query;
                    this.queryInput.value = query;
                    this.submitQuery();
                });
            });
        }
        
        // Ctrl+Enter to submit
        this.queryInput.addEventListener('keydown', (e) => {
            if (e.ctrlKey && e.key === 'Enter') {
                this.submitQuery();
            }
        });
        
        // Check backend connection
        await this.checkBackendConnection();
        this.updateLogCount();
    }
    
    async checkBackendConnection() {
        try {
            const response = await fetch(`${this.apiBaseUrl}/health`);
            const data = await response.json();
            
            if (response.ok) {
                this.showNotification('✅ Connected to Groq API', 'success');
                document.querySelector('.status-text').textContent = 'Groq Connected';
                document.querySelector('.status-dot').style.background = '#0F0';
            } else {
                this.useRealAPI = false;
                this.showNotification('⚠️ Using Demo Mode', 'warning');
            }
        } catch (error) {
            console.log('Backend not connected:', error);
            this.useRealAPI = false;
            this.showNotification('⚠️ Using Demo Mode - Start backend with: python backend/api_server.py', 'warning');
            document.querySelector('.status-text').textContent = 'Demo Mode';
            document.querySelector('.status-dot').style.background = '#FF0';
        }
    }
    
    async submitQuery() {
        const query = this.queryInput.value.trim();
        if (!query) {
            alert('Please enter a question');
            return;
        }
        
        this.clearLog();
        this.eventCount = 0;
        
        if (this.useRealAPI) {
            await this.processWithAPI(query);
        } else {
            this.simulateResponse(query);
        }
    }
    
    async processWithAPI(query) {
        try {
            // Show initial thought
            this.addEntry('thought', { message: `Processing: "${query}"` });
            
            // Call the API
            const response = await fetch(`${this.apiBaseUrl}/api/query`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    query: query,
                    model: 'llama-3.1-8b-instant',
                    temperature: 0.7
                })
            });
            
            if (!response.ok) {
                throw new Error('API request failed');
            }
            
            const data = await response.json();
            
            // Show steps if available
            if (data.steps) {
                data.steps.forEach(step => {
                    this.addEntry(step.type, step.data);
                });
            }
            
            // Show final response
            if (data.response) {
                this.addEntry('response', { message: data.response });
            }
            
            // Update token count if available
            if (data.usage) {
                console.log('Tokens used:', data.usage.total_tokens);
            }
            
        } catch (error) {
            console.error('API Error:', error);
            this.addEntry('thought', { message: '⚠️ Error calling API. Using demo mode.' });
            this.simulateResponse(query);
        }
    }
    
    simulateResponse(query) {
        // Simulate thinking process
        const steps = [
            { type: 'thought', delay: 500, data: { message: 'Analyzing query...' } },
            { type: 'action', delay: 1000, data: { name: 'call_groq', details: { model: 'llama-3.1-8b-instant' } } },
            { type: 'observation', delay: 1500, data: { data: { tokens: 150, finish: 'stop' } } }
        ];
        
        steps.forEach(step => {
            setTimeout(() => {
                this.addEntry(step.type, step.data);
            }, step.delay);
        });
        
        // Generate response based on query
        setTimeout(() => {
            let response = '';
            if (query.toLowerCase().includes('paris')) {
                response = 'Paris is the capital of France. The Eiffel Tower is its most famous landmark.';
            } else if (query.toLowerCase().includes('weather')) {
                response = 'The weather is sunny with a temperature of 22°C.';
            } else {
                response = `I processed your query: "${query}". This is a demo response.`;
            }
            this.addEntry('response', { message: response });
        }, 2000);
    }
    
    addEntry(type, data) {
        const template = document.getElementById(`${type}Template`);
        if (!template) return;
        
        const clone = document.importNode(template.content, true);
        const entry = clone.querySelector('.log-entry');
        
        // Add timestamp
        const now = new Date();
        const timeStr = now.toLocaleTimeString('en-US', { 
            hour: '2-digit', 
            minute: '2-digit', 
            second: '2-digit'
        });
        
        const timeSpan = entry.querySelector('.entry-time');
        if (timeSpan) timeSpan.textContent = timeStr;
        
        // Fill content based on type
        switch(type) {
            case 'thought':
                const thoughtMsg = entry.querySelector('.thought-message');
                if (thoughtMsg) thoughtMsg.textContent = data.message;
                break;
                
            case 'action':
                const actionName = entry.querySelector('.action-name');
                const actionDetails = entry.querySelector('.action-details');
                if (actionName) actionName.textContent = data.name;
                if (actionDetails) actionDetails.textContent = JSON.stringify(data.details, null, 2);
                break;
                
            case 'observation':
                const obsData = entry.querySelector('.observation-data');
                if (obsData) obsData.textContent = JSON.stringify(data.data, null, 2);
                break;
                
            case 'response':
                const responseMsg = entry.querySelector('.response-message');
                if (responseMsg) responseMsg.textContent = data.message;
                break;
        }
        
        // Add to log (newest at top)
        this.logContainer.insertBefore(entry, this.logContainer.firstChild);
        
        // Remove welcome message
        const welcome = this.logContainer.querySelector('.log-welcome');
        if (welcome) welcome.remove();
        
        // Update counters
        this.eventCount++;
        const logCount = document.getElementById('logCount');
        if (logCount) logCount.textContent = this.eventCount;
        
        // Store in logs array
        this.logs.push({ type, data, timestamp: now });
    }
    
    clearLog() {
        this.logContainer.innerHTML = '';
        this.logs = [];
        this.eventCount = 0;
        
        const logCount = document.getElementById('logCount');
        if (logCount) logCount.textContent = '0';
        
        // Add welcome message back
        const welcomeDiv = document.createElement('div');
        welcomeDiv.className = 'log-welcome';
        welcomeDiv.innerHTML = `
            <div class="neural-placeholder">
                <h3>AI Agent Ready</h3>
                <p>Ask me anything!</p>
            </div>
        `;
        this.logContainer.appendChild(welcomeDiv);
    }
    
    exportLog() {
        if (this.logs.length === 0) {
            alert('No logs to export');
            return;
        }
        
        const dataStr = JSON.stringify(this.logs, null, 2);
        const dataUri = 'data:application/json;charset=utf-8,' + encodeURIComponent(dataStr);
        const link = document.createElement('a');
        const date = new Date().toISOString().slice(0, 19).replace(/:/g, '-');
        link.setAttribute('href', dataUri);
        link.setAttribute('download', `agent-log-${date}.json`);
        link.click();
        
        this.showNotification('Logs exported', 'success');
    }
    
    showNotification(message, type) {
        console.log(`${type}: ${message}`);
        // You can add visual notifications here
    }
}

// Initialize when page loads
document.addEventListener('DOMContentLoaded', () => {
    new ThinkingLog();
});
"@ | Out-File -FilePath app.js -Encoding utf8