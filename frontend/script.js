const chatWindow = document.getElementById('chat-window');
const textInput = document.getElementById('text-input');
const sendBtn = document.getElementById('send-btn');
const micBtn = document.getElementById('mic-btn');
const statusIndicator = document.getElementById('status-indicator');
const correctionDisplay = document.getElementById('correction-display');
const correctionText = document.getElementById('correction-text');

let sessionId = localStorage.getItem('ai_partner_session_id');
if (!sessionId) {
    sessionId = crypto.randomUUID();
    localStorage.setItem('ai_partner_session_id', sessionId);
}

// --- Speech Recognition Setup ---
let recognition;
let isRecording = false;

if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    recognition = new SpeechRecognition();
    recognition.continuous = false;
    recognition.lang = 'en-US';
    recognition.interimResults = false;

    recognition.onstart = () => {
        isRecording = true;
        micBtn.classList.add('recording');
        statusIndicator.innerText = "Listening...";
    };

    recognition.onend = () => {
        isRecording = false;
        micBtn.classList.remove('recording');
        statusIndicator.innerText = "Ready";
    };

    recognition.onresult = (event) => {
        const transcript = event.results[0][0].transcript;
        textInput.value = transcript;
        sendMessage();
    };

    recognition.onerror = (event) => {
        console.error("Speech recognition error", event.error);
        statusIndicator.innerText = "Error: " + event.error;
    };
} else {
    micBtn.style.display = 'none';
    console.warn("Speech Recognition not supported in this browser.");
}

micBtn.addEventListener('click', () => {
    if (isRecording) {
        recognition.stop();
    } else {
        recognition.start();
    }
});

// --- Chat Logic ---

sendBtn.addEventListener('click', sendMessage);
textInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') sendMessage();
});

async function sendMessage() {
    const text = textInput.value.trim();
    if (!text) return;

    // Remove welcome message on first chat
    const welcome = document.querySelector('.welcome-message');
    if (welcome) welcome.remove();

    // Add User Message
    addMessage(text, 'user');
    textInput.value = '';
    statusIndicator.innerText = "AI is thinking...";

    // Hide previous correction
    correctionDisplay.classList.add('hidden');

    try {
        const response = await fetch('http://localhost:8000/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                user_message: text,
                session_id: sessionId
            })
        });

        if (!response.ok) throw new Error("API Error");

        const data = await response.json();

        statusIndicator.innerText = "Ready";

        // Add AI Message
        addMessage(data.ai_reply, 'ai');

        // Speak AI Response
        speak(data.ai_reply);

        // Show Correction if exists
        if (data.grammar_correction) {
            correctionText.innerText = data.grammar_correction;
            correctionDisplay.classList.remove('hidden');
        }

    } catch (error) {
        console.error(error);
        statusIndicator.innerText = "Error connecting to server";
        addMessage("Sorry, I couldn't reach the server. Make sure the backend is running.", 'ai');
    }
}

function addMessage(text, sender) {
    const div = document.createElement('div');
    div.classList.add('message', sender === 'user' ? 'user-message' : 'ai-message');
    div.textContent = text;
    chatWindow.appendChild(div);
    chatWindow.scrollTop = chatWindow.scrollHeight;
}

// --- Speech Synthesis ---
function speak(text) {
    if (!('speechSynthesis' in window)) return;

    // Cancel any current speaking
    window.speechSynthesis.cancel();

    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = 'en-US';

    // Try to find a nice English voice
    const voices = window.speechSynthesis.getVoices();
    const preferredVoice = voices.find(v => v.name.includes("Google US English")) ||
        voices.find(v => v.lang === 'en-US' && v.name.includes("Female")) ||
        voices.find(v => v.lang === 'en-US');

    if (preferredVoice) utterance.voice = preferredVoice;

    utterance.rate = 1.0;
    utterance.pitch = 1.0;

    window.speechSynthesis.speak(utterance);
}

// Pre-load voices (sometimes required in Chrome)
window.speechSynthesis.onvoiceschanged = () => {
    // just to trigger loading
    window.speechSynthesis.getVoices();
};
