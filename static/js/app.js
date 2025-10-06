// State management
let transcript = '';

// DOM Elements
let mealInput;
let transcriptDiv;
let submitBtn;
let resultDiv;
let dailyTotalsDiv;
let microphoneIcon;
let mealListDiv;

// Initialize the application
document.addEventListener('DOMContentLoaded', async () => {
    initializeElements();
    await initializeUserId();
    loadProfileAndUpdateDisplay();
    setupEventListeners();
    // Initial update of meal list and nutrition data
    await updateNutritionData();
});

function initializeElements() {
    mealInput = document.getElementById('meal-input');
    transcriptDiv = document.getElementById('transcript');
    submitBtn = document.getElementById('submit-btn');
    resultDiv = document.getElementById('result');
    dailyTotalsDiv = document.getElementById('daily-totals');
    microphoneIcon = document.getElementById('microphone-icon');
    mealListDiv = document.getElementById('meal-list');
}

function updateDisplayName() {
    try {
        const profileKey = `profile_${window.userId}`;
        console.log('Looking for profile with key:', profileKey);
        
        const profileData = localStorage.getItem(profileKey);
        console.log('Found profile data:', profileData);
        
        const userIdElement = document.getElementById('user-id');
        if (!userIdElement) {
            console.error('Could not find user-id element');
            return;
        }

        if (profileData) {
            const profile = JSON.parse(profileData);
            console.log('Parsed profile:', profile);
            if (profile.name) {
                console.log('Found name:', profile.name);
                userIdElement.textContent = `Hello, ${profile.name}`;
                return;
            }
        }
        console.log('No name found, showing userId:', window.userId);
        userIdElement.textContent = `User ID: ${window.userId}`;
    } catch (error) {
        console.error('Error in updateDisplayName:', error);
        const userIdElement = document.getElementById('user-id');
        if (userIdElement) {
            userIdElement.textContent = `User ID: ${window.userId}`;
        }
    }
}

async function initializeUserId() {
    try {
        // Store userId in the window object for global access
        window.userId = getCookie('user_id');
        if (!window.userId) {
            window.userId = generateUserId();
            setCookie('user_id', window.userId, 365, '/');
            console.log('New user ID generated and stored in cookie:', window.userId);
        } else {
            console.log('Existing User ID retrieved from cookie:', window.userId);
        }
        
        // Now that we have a valid userId, load the initial data
        try {
            await Promise.all([
                updateMealList(),
                updateDailyTotals(window.userId)
            ]);
        } catch (error) {
            console.error('Error loading initial data:', error);
        }
    } catch (error) {
        console.error('Error in initializeUserId:', error);
    }
}

function loadProfileAndUpdateDisplay() {
    updateDisplayName();
}

function generateUserId() {
    if (window.crypto && window.crypto.randomUUID) {
        return window.crypto.randomUUID();
    } else if (typeof uuidv4 === 'function') {
        return uuidv4();
    }
    return generateFallbackUUID();
}

function generateFallbackUUID() {
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
        const r = Math.random() * 16 | 0;
        const v = c === 'x' ? r : (r & 0x3 | 0x8);
        return v.toString(16);
    });
}

function setupEventListeners() {
    // Voice input setup
    if ('webkitSpeechRecognition' in window && microphoneIcon) {
        setupVoiceRecognition();
    } else if (microphoneIcon) {
        microphoneIcon.style.display = 'none';
    }

    // Text input setup
    if (mealInput) {
        mealInput.addEventListener('keypress', async (event) => {
            if (event.key === 'Enter') {
                event.preventDefault();
                await handleMealSubmission();
            }
        });
    }

    // Submit button setup
    if (submitBtn) {
        submitBtn.addEventListener('click', handleMealSubmission);
    }
}

// Cookie utilities
function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
}

function setCookie(name, value, days, path = '/') {
    const expires = new Date(Date.now() + days * 864e5).toUTCString();
    document.cookie = `${name}=${encodeURIComponent(value)}; expires=${expires}; path=${path}`;
}
