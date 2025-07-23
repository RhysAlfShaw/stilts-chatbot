// DOM element references
const form = document.getElementById('prompt-form');
const input = document.getElementById('prompt-input');
const chatContainer = document.getElementById('chat-container');
const submitButton = document.getElementById('submit-button');
const statusIndicator = document.getElementById('status-indicator');

// Since the HTML is served by FastAPI, we can use relative paths.
const API_URL = '/generate';
const HEALTH_CHECK_URL = '/health';

/**
 * Checks the status of the backend server.
 */
async function checkServerStatus() {
    try {
        const response = await fetch(HEALTH_CHECK_URL);
        if (response.ok) {
            statusIndicator.classList.remove('bg-red-500');
            statusIndicator.classList.add('bg-green-500');
            statusIndicator.title = 'Connected';
        } else {
            throw new Error('Server not ready');
        }
    } catch (error) {
        console.error('Health check failed:', error);
        statusIndicator.classList.remove('bg-green-500');
        statusIndicator.classList.add('bg-red-500');
        statusIndicator.title = 'Disconnected';
    }
}

/**
 * Adds a message bubble to the chat container.
 * @param {string} message - The text content of the message.
 * @param {string} sender - 'user' or 'bot'.
 */
function addMessage(message, sender) {
    const messageWrapper = document.createElement('div');
    messageWrapper.classList.add('flex', 'chat-bubble');
    
    const messageBubble = document.createElement('div');
    messageBubble.classList.add('p-3', 'rounded-lg', 'max-w-md');

    if (sender === 'user') {
        messageWrapper.classList.add('justify-end');
        messageBubble.classList.add('bg-blue-600', 'text-white');
    } else {
        messageWrapper.classList.add('justify-start');
        messageBubble.classList.add('bg-gray-200', 'text-gray-800');
    }

    messageBubble.innerHTML = `<p>${message}</p>`;
    messageWrapper.appendChild(messageBubble);
    chatContainer.appendChild(messageWrapper);
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

/**
 * Shows a loading indicator for the bot's response.
 */
function showLoadingIndicator() {
    const loadingWrapper = document.createElement('div');
    loadingWrapper.id = 'loading-indicator';
    loadingWrapper.classList.add('flex', 'justify-start', 'chat-bubble');
    
    const loadingBubble = document.createElement('div');
    loadingBubble.classList.add('bg-gray-200', 'text-gray-500', 'p-3', 'rounded-lg');
    loadingBubble.innerHTML = `
        <div class="flex items-center space-x-2">
            <div class="w-2 h-2 bg-gray-400 rounded-full animate-pulse"></div>
            <div class="w-2 h-2 bg-gray-400 rounded-full animate-pulse" style="animation-delay: 0.2s;"></div>
            <div class="w-2 h-2 bg-gray-400 rounded-full animate-pulse" style="animation-delay: 0.4s;"></div>
        </div>
    `;
    loadingWrapper.appendChild(loadingBubble);
    chatContainer.appendChild(loadingWrapper);
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

/**
 * Removes the loading indicator.
 */
function hideLoadingIndicator() {
    const indicator = document.getElementById('loading-indicator');
    if (indicator) {
        indicator.remove();
    }
}

// Handle form submission
form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const promptText = input.value.trim();

    if (!promptText) return;

    addMessage(promptText, 'user');
    input.value = '';
    submitButton.disabled = true;
    showLoadingIndicator();

    try {
        const response = await fetch(API_URL, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text: promptText }),
        });

        hideLoadingIndicator();

        if (!response.ok) throw new Error('Network response was not ok.');

        const data = await response.json();
        addMessage(data.reply, 'bot');

    } catch (error) {
        console.error('Error:', error);
        hideLoadingIndicator();
        addMessage('Sorry, something went wrong. Please check the server and try again.', 'bot');
    } finally {
        submitButton.disabled = false;
        input.focus();
    }
});

// Check server status on page load and periodically
window.addEventListener('load', () => {
    checkServerStatus();
    setInterval(checkServerStatus, 60000); // Check every 10 seconds
});