function addMessage(role, text) {
    const container = document.getElementById("chat-container");
    const div = document.createElement("div");
    div.className = role === "user" ? "text-right" : "text-left";
    div.innerHTML = `<div class="inline-block max-w-xs p-3 rounded-2xl ${role === "user" ? "bg-emerald-500 text-black" : "bg-zinc-800"}">${text}</div>`;
    container.appendChild(div);
    container.scrollTop = container.scrollHeight;
}

async function sendMessage(text) {
    addMessage("user", text);

    try {
        const res = await fetch("/api/chat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ message: text })
        });

        const data = await res.json();
        addMessage("ai", data.reply || "Sorry, I couldn't process that.");
    } catch (e) {
        addMessage("ai", "Something went wrong. Please try again.");
    }
}

function toggleVoiceInput() {
    const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
    recognition.lang = "en-US";

    recognition.onresult = (event) => {
        const text = event.results[0][0].transcript;
        sendMessage(text);
    };

    recognition.start();
}

// Welcome message
document.addEventListener("DOMContentLoaded", () => {
    addMessage("ai", "Hello! How can I help you today?");
});