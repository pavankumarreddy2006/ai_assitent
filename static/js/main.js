// static/js/main.js
let conversationHistory = [];
let currentLanguage = "en";
let slideIndex = 0;
let mediaTimeout = null;
let recognition = null;

const API_BASE = window.location.origin;

// Tailwind script already loaded in HTML

function detectTimeGreeting() {
    const hour = new Date().getHours();
    const el = document.getElementById("greeting-time");
    if (hour < 12) el.textContent = "GOOD MORNING";
    else if (hour < 17) el.textContent = "GOOD AFTERNOON";
    else el.textContent = "GOOD EVENING";
}

function toggleVoiceInput() {
    const micBtn = document.getElementById("mic-btn");
    const icon = document.getElementById("mic-icon");
    
    if (!recognition) {
        if ("SpeechRecognition" in window || "webkitSpeechRecognition" in window) {
            recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
            recognition.continuous = false;
            recognition.lang = currentLanguage === "te" ? "te-IN" : "en-US";
            
            recognition.onresult = (event) => {
                const transcript = event.results[0][0].transcript;
                document.getElementById("message-input").value = transcript;
                sendMessage(true); // auto send
            };
            
            recognition.onerror = () => {
                micBtn.classList.remove("listening");
                icon.innerHTML = `<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m-.5-15a3.5 3.5 0 10-7 0v4a3.5 3.5 0 007 0V6z" />`;
            };
            
            recognition.onend = () => {
                micBtn.classList.remove("listening");
                icon.innerHTML = `<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m-.5-15a3.5 3.5 0 10-7 0v4a3.5 3.5 0 007 0V6z" />`;
            };
        } else {
            alert("Voice input not supported in your browser.");
            return;
        }
    }
    
    if (micBtn.classList.contains("listening")) {
        recognition.stop();
    } else {
        micBtn.classList.add("listening");
        icon.innerHTML = `<circle cx="12" cy="12" r="10" stroke="#00ff9d" stroke-width="4" fill="none"/><circle cx="12" cy="12" r="3" fill="#00ff9d"/>`;
        recognition.start();
    }
}

async function sendMessage(isVoice = false) {
    const input = document.getElementById("message-input");
    const message = input.value.trim();
    if (!message) return;
    
    // Hide welcome screen
    document.getElementById("welcome-screen").classList.add("hidden");
    document.getElementById("chat-container").classList.remove("hidden");
    
    // Add user message
    addMessageToChat("user", message);
    
    // Clear input
    input.value = "";
    
    // Show typing indicator
    const typingId = addTypingIndicator();
    
    try {
        const res = await fetch(`${API_BASE}/api/chat`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                message: message,
                conversationHistory: conversationHistory
            })
        });
        
        const data = await res.json();
        
        // Remove typing
        removeTypingIndicator(typingId);
        
        // Save to history
        conversationHistory.push({ role: "user", content: message });
        conversationHistory.push({ role: "assistant", content: data.reply });
        
        // Detect language for TTS
        currentLanguage = data.language || "en";
        
        // Display AI reply
        addMessageToChat("ai", data.reply, data.source || null);
        
        // Voice response (lady voice + correct Telugu/English)
        if (data.reply) {
            speakResponse(data.reply, currentLanguage);
        }
        
        // Handle media (images / video) - FULL SCREEN AUTO RETURN
        if (data.show_images && data.images && data.images.length) {
            showImageCarousel(data.images, data.media_duration || 8);
        } else if (data.show_video && data.video_url) {
            showVideo(data.video_url, data.media_duration || 18);
        }
        
    } catch (e) {
        removeTypingIndicator(typingId);
        addMessageToChat("ai", "Sorry, something went wrong. Please try again.");
    }
}

function sendQuickMessage(text) {
    document.getElementById("message-input").value = text;
    sendMessage();
}

function addMessageToChat(role, text, source = null) {
    const container = document.getElementById("chat-container");
    
    const div = document.createElement("div");
    div.className = `flex ${role === "user" ? "justify-end" : "justify-start"}`;
    
    if (role === "user") {
        div.innerHTML = `
            <div class="chat-bubble-user max-w-[70%] px-5 py-3 text-black font-medium">
                ${text}
            </div>`;
    } else {
        div.innerHTML = `
            <div class="chat-bubble-ai max-w-[70%] px-5 py-3">
                ${text}
                ${source ? `<div class="text-[10px] text-emerald-400/60 mt-2">${source}</div>` : ''}
            </div>`;
    }
    
    container.appendChild(div);
    container.scrollTop = container.scrollHeight;
}

function addTypingIndicator() {
    const container = document.getElementById("chat-container");
    const id = "typing-" + Date.now();
    const div = document.createElement("div");
    div.id = id;
    div.className = "flex justify-start";
    div.innerHTML = `
        <div class="bg-[#1f2937] rounded-3xl px-5 py-3 flex gap-x-1">
            <div class="w-2 h-2 bg-white/60 rounded-full animate-bounce"></div>
            <div class="w-2 h-2 bg-white/60 rounded-full animate-bounce" style="animation-delay:150ms"></div>
            <div class="w-2 h-2 bg-white/60 rounded-full animate-bounce" style="animation-delay:300ms"></div>
        </div>`;
    container.appendChild(div);
    container.scrollTop = container.scrollHeight;
    return id;
}

function removeTypingIndicator(id) {
    const el = document.getElementById(id);
    if (el) el.remove();
}

function speakResponse(text, lang) {
    if (!('speechSynthesis' in window)) return;
    
    const utterance = new SpeechSynthesisUtterance(text);
    
    // Prefer female voice
    const voices = speechSynthesis.getVoices();
    let preferredVoice = voices.find(v => 
        (lang === "te" && v.lang.includes("te")) || 
        (v.name.toLowerCase().includes("female") || v.name.toLowerCase().includes("raveena") || v.name.toLowerCase().includes("priya"))
    );
    
    if (preferredVoice) utterance.voice = preferredVoice;
    utterance.lang = lang === "te" ? "te-IN" : "en-US";
    utterance.pitch = 1.05;
    utterance.rate = 0.98;
    
    speechSynthesis.speak(utterance);
}

// Media Full-Screen Functions
let currentMediaIndex = 0;
let imagesArray = [];

function showImageCarousel(images, duration) {
    imagesArray = images;
    currentMediaIndex = 0;
    document.getElementById("image-carousel").classList.remove("hidden");
    document.getElementById("video-container").classList.add("hidden");
    document.getElementById("media-modal").classList.remove("hidden");
    renderCarousel();
    
    if (mediaTimeout) clearTimeout(mediaTimeout);
    mediaTimeout = setTimeout(hideMedia, duration * 1000);
}

function renderCarousel() {
    const container = document.getElementById("carousel-images");
    container.innerHTML = `
        <img src="${imagesArray[currentMediaIndex]}" class="w-full max-h-[70vh] object-contain" alt="College image">
    `;
}

function nextSlide() {
    currentMediaIndex = (currentMediaIndex + 1) % imagesArray.length;
    renderCarousel();
}

function prevSlide() {
    currentMediaIndex = (currentMediaIndex - 1 + imagesArray.length) % imagesArray.length;
    renderCarousel();
}

function showVideo(videoUrl, duration) {
    document.getElementById("image-carousel").classList.add("hidden");
    const videoContainer = document.getElementById("video-container");
    videoContainer.classList.remove("hidden");
    document.getElementById("media-modal").classList.remove("hidden");
    
    const videoEl = document.getElementById("modal-video");
    videoEl.src = videoUrl;
    videoEl.play();
    
    if (mediaTimeout) clearTimeout(mediaTimeout);
    mediaTimeout = setTimeout(() => {
        hideMedia();
    }, duration * 1000);
}

function hideMedia() {
    if (mediaTimeout) {
        clearTimeout(mediaTimeout);
        mediaTimeout = null;
    }
    const modal = document.getElementById("media-modal");
    modal.classList.add("hidden");
    // Reset video
    const videoEl = document.getElementById("modal-video");
    if (videoEl) {
        videoEl.pause();
        videoEl.src = "";
    }
}

// Load latest updates (static for now - can be fetched later)
function loadLatestUpdates() {
    const container = document.getElementById("latest-updates");
    container.innerHTML = `
        <div class="flex gap-2 text-xs"><span class="text-emerald-400">📌</span> Promising Partnerships: Kenya’s Healthcare Professionals Forge Links in India</div>
        <div class="flex gap-2 text-xs"><span class="text-emerald-400">📌</span> CBSE class 12 result 2026 today or not? Big update after class 10 results</div>
        <div class="flex gap-2 text-xs"><span class="text-emerald-400">📌</span> PM Modi Unveils Sri Guru Bhairavaikya Mandira</div>
    `;
}

// Initialize everything
window.onload = () => {
    detectTimeGreeting();
    loadLatestUpdates();
    
    // Preload voices for better Telugu pronunciation
    if ('speechSynthesis' in window) {
        speechSynthesis.getVoices();
    }
    
    console.log("%c✅ Ideal AI Frontend loaded successfully with mic animation, full-screen media & voice", "color:#00ff9d; font-family:monospace");
};