// PRO MAIN.JS - Fixed API Connection
let history = [];

function addMessage(role, text) {
    const container = document.getElementById("chat-container");
    const div = document.createElement("div");
    div.className = `flex ${role === "user" ? "justify-end" : "justify-start"} mb-6`;
    div.innerHTML = `<div class="${role === "user" ? "chat-bubble-user" : "chat-bubble-ai"}">${text}</div>`;
    container.appendChild(div);
    container.scrollTop = container.scrollHeight;
}

function showTyping() {
    const id = "typing-" + Date.now();
    const container = document.getElementById("chat-container");
    const div = document.createElement("div");
    div.id = id;
    div.innerHTML = `<div class="chat-bubble-ai px-6 py-4 flex gap-2"><div class="w-3 h-3 bg-white/60 rounded-full animate-bounce"></div><div class="w-3 h-3 bg-white/60 rounded-full animate-bounce delay-150"></div><div class="w-3 h-3 bg-white/60 rounded-full animate-bounce delay-300"></div></div>`;
    container.appendChild(div);
    container.scrollTop = container.scrollHeight;
    return id;
}

function removeTyping(id) {
    const el = document.getElementById(id);
    if (el) el.remove();
}

// FIXED API CALL
async function sendToBackend(message) {
    const typingId = showTyping();
    try {
        const response = await fetch("/api/chat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                message: message,
                conversationHistory: history
            })
        });

        if (!response.ok) throw new Error("Server error");

        const data = await response.json();
        removeTyping(typingId);

        if (data.reply) {
            addMessage("ai", data.reply);
            history.push({ role: "assistant", content: data.reply });

            // Voice Response
            speakResponse(data.reply, data.language || "en");

            // Media
            if (data.show_images) showImages(data.images);
            if (data.show_video) showVideo(data.video_url);
        }
    } catch (err) {
        console.error("API Call Failed:", err);
        removeTyping(typingId);
        addMessage("ai", "Something went wrong. Please try again.");
    }
}

function speakResponse(text, lang) {
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = lang === "te" ? "te-IN" : "en-US";
    speechSynthesis.speak(utterance);
}

function toggleVoiceInput() {
    const btn = document.getElementById("mic-btn");
    if (!('SpeechRecognition' in window)) return alert("Voice not supported");

    const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
    recognition.lang = "en-US";
    recognition.onresult = (e) => {
        const text = e.results[0][0].transcript;
        addMessage("user", text);
        history.push({ role: "user", content: text });
        sendToBackend(text);
    };
    recognition.start();
    btn.classList.add("listening");
    setTimeout(() => btn.classList.remove("listening"), 6000);
}

function showImages(images) { /* Full screen logic */ }
function showVideo(url) { /* Full screen video logic */ }
function hideMedia() { /* hide modal */ }

// Auto start greeting
document.addEventListener("DOMContentLoaded", () => {
    console.log("%c✅ Ideal AI Pro Connected", "color:#10b981; font-weight:bold");
});