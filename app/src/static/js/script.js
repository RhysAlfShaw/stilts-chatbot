// DOM element references
const form = document.getElementById('prompt-form');
const input = document.getElementById('prompt-input');
const chatContainer = document.getElementById('chat-container');
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
            statusIndicator.style.backgroundColor = 'green';
            statusIndicator.title = 'Connected';

        } else {
            throw new Error('Server not ready');
        }
    } catch (error) {
        console.error('Health check failed:', error);
        statusIndicator.style.backgroundColor = 'red';
        statusIndicator.title = 'Disconnected';
    }
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


function highlightElementInIframe(location) {
    const iframe = document.getElementById('viewer');
    const iframeDoc = iframe.contentDocument || iframe.contentWindow.document;

    if (!iframeDoc) {
        console.error("Could not access the iframe's document.");
        return;
    }
    
    // 1. Remove previous highlight
    if (lastHighlightedElement) {
        lastHighlightedElement.classList.remove('highlighted');
    }

    // 2. Find the new element to highlight
    const elements = iframeDoc.querySelectorAll(location.tag);
    const targetElement = elements[location.element_index];

    if (targetElement) {
        // 3. Apply the highlight class
        targetElement.classList.add('highlighted');
        
        // 4. Scroll the element into view
        targetElement.scrollIntoView({
            behavior: 'smooth',
            block: 'center'
        });

        lastHighlightedElement = targetElement;
    } else {
        console.warn("Could not find the target element in the iframe for location:", location);
    }
}