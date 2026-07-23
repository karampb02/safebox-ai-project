// ============================================================================
// SafeBox Web - Frontend JavaScript
// ============================================================================

// DOM Elements
const urlInput = document.getElementById('url-input');
const analyzeBtn = document.getElementById('analyze-btn');
const resultsSection = document.getElementById('results-section');
const resultsContent = document.getElementById('results-content');
const loadingIndicator = document.getElementById('loading-indicator');
const errorMessage = document.getElementById('error-message');
const errorText = document.getElementById('error-text');
const closeResultsBtn = document.getElementById('close-results-btn');

// API Endpoint
const API_ENDPOINT = '/analyze';

// Event Listeners
analyzeBtn.addEventListener('click', handleAnalyze);
urlInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        handleAnalyze();
    }
});
closeResultsBtn.addEventListener('click', resetUI);

// ============================================================================
// Main Functions
// ============================================================================

/**
 * Handles the URL analysis workflow
 */
async function handleAnalyze() {
    const url = urlInput.value.trim();

    // Validate URL
    if (!url) {
        showError('Please enter a URL to analyze.');
        return;
    }

    if (!isValidURL(url)) {
        showError('Please enter a valid URL (e.g., https://example.com).');
        return;
    }

    // Clear previous results and errors
    hideError();
    resetUI();

    // Show loading indicator
    showLoading();

    try {
        // Send request to backend
        await streamAnalysis(url);
    } catch (error) {
        showError(`Analysis failed: ${error.message}`);
    } finally {
        hideLoading();
    }
}

/**
 * Validates if the input is a valid URL
 */
function isValidURL(url) {
    try {
        // Add protocol if missing
        let urlToValidate = url;
        if (!url.startsWith('http://') && !url.startsWith('https://')) {
            urlToValidate = 'https://' + url;
        }
        new URL(urlToValidate);
        return true;
    } catch (error) {
        return false;
    }
}

/**
 * Streams the analysis response from the backend
 */
async function streamAnalysis(url) {
    try {
        const response = await fetch(API_ENDPOINT, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ url: url }),
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Analysis request failed');
        }

        // Show results section
        showResults();

        // Clear previous content
        resultsContent.textContent = '';

        // Stream the response
        const reader = response.body.getReader();
        const decoder = new TextDecoder();

        while (true) {
            const { done, value } = await reader.read();

            if (done) {
                break;
            }

            const chunk = decoder.decode(value, { stream: true });
            resultsContent.textContent += chunk;

            // Auto-scroll to bottom
            resultsContent.scrollTop = resultsContent.scrollHeight;
        }
    } catch (error) {
        throw error;
    }
}

// ============================================================================
// UI Helper Functions
// ============================================================================

/**
 * Shows the loading indicator
 */
function showLoading() {
    loadingIndicator.style.display = 'flex';
    analyzeBtn.disabled = true;
}

/**
 * Hides the loading indicator
 */
function hideLoading() {
    loadingIndicator.style.display = 'none';
    analyzeBtn.disabled = false;
}

/**
 * Shows the results section
 */
function showResults() {
    resultsSection.style.display = 'block';
    resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

/**
 * Resets the UI to its initial state, clearing results and hiding panels.
 */
function resetUI() {
    resultsSection.style.display = 'none';
    resultsContent.textContent = ''; // Clear streamed content
    urlInput.value = ''; // Optionally clear input
    hideError();
    hideLoading();
    urlInput.focus();
}

/**
 * Shows an error message
 */
function showError(message) {
    errorText.textContent = message;
    errorMessage.style.display = 'flex';
}

/**
 * Hides the error message
 */
function hideError() {
    errorMessage.style.display = 'none';
}

// ============================================================================
// Initialization
// ============================================================================

// Focus on input field on page load
window.addEventListener('load', () => {
    urlInput.focus();
});
