// static/js/main.js - PRO LEVEL IDEAL AI FRONTEND
let conversationHistory = [];
let recognition = null;
let isListening = false;
let currentMediaTimeout = null;

const API_CHAT = "/api/chat";

// Tailwind script already loaded via CDN

// Add message to chat
function addMessage(role, text) {
    const container = document.getElementById("chat-container");
    const div = document.createElement("div");
    div.className = `flex ${role === "user" ? "justify-end" : "justify-start"} mb-6`;

    if (role === "user") {
        div.innerHTML = `
            <div class="chat-bubble-user max-w-[75%] px-5 py-3.5 text-black font-medium">
                ${text}
            </div>`;
    } else {
        div.innerHTML = `
            <div class="chat-bubble-ai max-w-[75%] px-5 py-3.5">
                ${text}
            </div>`;
    }

    container.appendChild(div);
    container.scrollTop = container.scrollHeight;
}

// Show typing indicator
function showTyping() {
    const container = document.getElementById("chat-container");
    const id = "typing-indicator";
    let typingDiv = document.getElementById(id);

    if (!typingDiv) {
        typingDiv = document.createElement("div");
        typingDiv.id = id;
        typingDiv.className = "flex justify-start mb-6";
        typingDiv.innerHTML = `
            <div class="chat-bubble-ai px-5 py-3 flex items-center gap-1">
                <div class="w-2 h-2 bg-zinc-400 rounded-full animate-bounce"></div>
                <div class="w-2 h-2 bg-zinc-400 rounded-full animate-bounce" style="animation-delay: 150ms"></div>
                <div class="w-2 h-2 bg-zinc-400 rounded-full animate-bounce" style="animation-delay: 300ms"></div>
            </div>`;
        container.appendChild(typingDiv);
        container.scrollTop = container.scrollHeight;
    }
    return id;
}

function removeTyping(id) {
    const el = document.getElementById(id);
    if (el) el.remove();
}

// Send message
async function sendMessage() {
    const input = document.getElementById("message-input");
    const message = input.value.trim();

    if (!message) return;

    // Hide welcome screen if visible
    const welcome = document.getElementById("welcome-screen");
    if (welcome) welcome.style.display = "none";

    addMessage("user", message);
    conversationHistory.push({ role: "user", content: message });
    input.value = "";

    const typingId = showTyping();

    try {
        const response = await fetch(API_CHAT, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                message: message,
                conversationHistory: conversationHistory
            })
        });

        const data = await response.json();

        removeTyping(typingId);

        if (data.reply) {
            addMessage("ai", data.reply);
            conversationHistory.push({ role: "assistant", content: data.reply });

            // Speak response (Natural voice)
            speakResponse(data.reply, data.language || "en");

            // Handle Media (Images or Video)
            if (data.show_images && data.images && data.images.length > 0) {
                showImageCarousel(data.images, data.media_duration || 8);
            } else if (data.show_video && data.video_url) {
                showVideo(data.video_url, data.media_duration || 15);
            }
        } else {
            addMessage("ai", "Sorry, I couldn't understand that. Please try again.");
        }

    } catch (error) {
        console.error("API Error:", error);
        removeTyping(typingId);
        addMessage("ai", "Something went wrong. Please check your connection and try again.");
    }
}

// Voice Input (JARVIS Style)
function toggleVoiceInput() {
    const micBtn = document.getElementById("mic-btn");

    if (!recognition) {
        recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
        recognition.continuous = false;
        recognition.interimResults = false;
        recognition.lang = "en-US"; // Change to "te-IN" for Telugu only

        recognition.onresult = (event) => {
            const transcript = event.results[0][0].transcript.trim();
            document.getElementById("message-input").value = transcript;
            sendMessage();
        };

        recognition.onerror = () => {
            stopListening();
        };

        recognition.onend = () => {
            stopListening();
        };
    }

    if (isListening) {
        stopListening();
    } else {
        try {
            recognition.start();
            isListening = true;
            micBtn.classList.add("listening");
        } catch (e) {
            console.error("Speech recognition error", e);
        }
    }
}

function stopListening() {
    if (recognition) recognition.stop();
    isListening = false;
    document.getElementById("mic-btn").classList.remove("listening");
}

// Text-to-Speech (Natural Lady Voice)
function speakResponse(text, lang) {
    if (!('speechSynthesis' in window)) return;

    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = lang === "te" ? "te-IN" : "en-US";
    utterance.pitch = 1.05;
    utterance.rate = 0.97;

    // Try to use female voice
    const voices = speechSynthesis.getVoices();
    const femaleVoice = voices.find(v => 
        v.name.toLowerCase().includes("female") || 
        v.name.toLowerCase().includes("raveena") || 
        v.name.toLowerCase().includes("priya")
    );
    if (femaleVoice) utterance.voice = femaleVoice;

    speechSynthesis.speak(utterance);
}

// Media Functions (Full Screen)
function showImageCarousel(images, duration) {
    const modal = document.getElementById("media-modal");
    const carousel = document.getElementById("image-carousel");
    carousel.innerHTML = "";
    carousel.classList.remove("hidden");

    images.forEach((src, index) => {
        const img = document.createElement("img");
        img.src = src;
        img.className = `w-full max-h-[75vh] object-contain ${index !== 0 ? 'hidden' : ''}`;
        carousel.appendChild(img);
    });

    modal.classList.remove("hidden");

    let current = 0;
    const interval = setInterval(() => {
        const imgs = carousel.querySelectorAll("img");
        imgs.forEach(img => img.classList.add("hidden"));
        current = (current + 1) % imgs.length;
        imgs[current].classList.remove("hidden");
    }, 2000);

    currentMediaTimeout = setTimeout(() => {
        clearInterval(interval);
        hideMedia();
    }, duration * 1000);
}

function showVideo(videoUrl, duration) {
    const modal = document.getElementById("media-modal");
    const videoContainer = document.getElementById("video-container");
    const videoEl = document.getElementById("modal-video");

    videoContainer.classList.remove("hidden");
    videoEl.src = videoUrl;
    videoEl.play();

    modal.classList.remove("hidden");

    currentMediaTimeout = setTimeout(() => {
        hideMedia();
    }, duration * 1000);
}

function hideMedia() {
    const modal = document.getElementById("media-modal");
    modal.classList.add("hidden");

    const videoEl = document.getElementById("modal-video");
    if (videoEl) {
        videoEl.pause();
        videoEl.src = "";
    }

    if (currentMediaTimeout) {
        clearTimeout(currentMediaTimeout);
    }
}

// Quick message from suggestions (if you add later)
function sendQuickMessage(text) {
    document.getElementById("message-input").value = text;
    sendMessage();
}

// Initialize
document.addEventListener("DOMContentLoaded", () => {
    // Preload voices
    if ('speechSynthesis' in window) {
        speechSynthesis.getVoices();
    }

    console.log("%c✅ Ideal AI Pro Frontend Loaded Successfully", "color:#10b981; font-size:14px; font-weight:bold");
});