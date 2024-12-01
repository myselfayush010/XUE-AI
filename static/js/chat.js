document.addEventListener('DOMContentLoaded', () => {
    const chatForm = document.getElementById('chat-form');
    const userInput = document.getElementById('user-input');
    const chatMessages = document.getElementById('chat-messages');
    let conversationHistory = [
        {
            role: "system",
            content: "You are a helpful AI assistant for students. Format your responses in markdown when appropriate. Provide clear, educational responses."
        }
    ];

    // Configure marked.js options
    marked.setOptions({
        highlight: function(code, lang) {
            if (lang && hljs.getLanguage(lang)) {
                return hljs.highlight(code, { language: lang }).value;
            }
            return hljs.highlightAuto(code).value;
        },
        breaks: true
    });

    function addMessage(content, isUser) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${isUser ? 'user-message' : 'assistant-message markdown-body'}`;
        
        if (isUser) {
            messageDiv.textContent = content;
        } else {
            messageDiv.innerHTML = marked.parse(content);
            // Apply syntax highlighting to code blocks
            messageDiv.querySelectorAll('pre code').forEach((block) => {
                hljs.highlightElement(block);
            });
        }
        
        chatMessages.appendChild(messageDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    function addThinkingIndicator() {
        const thinkingDiv = document.createElement('div');
        thinkingDiv.className = 'message assistant-message thinking';
        thinkingDiv.innerHTML = `
            AI is thinking
            <div class="thinking-dots">
                <span></span>
                <span></span>
                <span></span>
            </div>
        `;
        chatMessages.appendChild(thinkingDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
        return thinkingDiv;
    }

    async function sendMessage(message) {
        try {
            const thinkingIndicator = addThinkingIndicator();
            
            conversationHistory.push({
                role: "user",
                content: message
            });

            const response = await fetch('/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    messages: conversationHistory
                })
            });

            if (!response.ok) {
                throw new Error('Network response was not ok');
            }

            const data = await response.json();
            const assistantMessage = data.choices[0].message.content;
            
            // Remove thinking indicator
            thinkingIndicator.remove();
            
            conversationHistory.push({
                role: "assistant",
                content: assistantMessage
            });

            addMessage(assistantMessage, false);
        } catch (error) {
            console.error('Error:', error);
            const errorMessage = '```error\nSorry, there was an error processing your request.\n```';
            addMessage(errorMessage, false);
        }
    }

    chatForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const message = userInput.value.trim();
        if (message) {
            addMessage(message, true);
            userInput.value = '';
            await sendMessage(message);
        }
    });

    // Add loading indicator
    function setLoading(isLoading) {
        const button = chatForm.querySelector('button');
        button.disabled = isLoading;
        button.textContent = isLoading ? 'Sending...' : 'Send';
    }
});
