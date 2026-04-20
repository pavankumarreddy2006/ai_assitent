let history = [];

function addMessage(role, text) {
    const container = document.getElementById("chat-container");
    const div = document.createElement("div");
    div.className = `flex ${role === "user" ? "justify-end" : "justify-start"} mb-4`;
    div.innerHTML = `<div class="${role === "user" ? "chat-bubble-user" : "chat-bubble-ai"}">${text}</div>`;
    container.appendChild(div);
    container.scrollTop = container.scrollHeight;
}

async function sendMessage(message) {
    addMessage("user", message);
    history.push({role: "user", content: message});

    const typing = document.createElement("div");
    typing.innerHTML = `<div class="chat-bubble-ai p-4 flex gap-2"><div class="w-2 h-2 bg-white rounded-full animate-bounce"></div><div class="w-2 h-2 bg-white rounded-full animate-bounce delay-150"></div><div class="w-2 h-2 bg-white rounded-full animate-bounce delay-300"></div></div>`;
    document.getElementById("chat-container").appendChild(typing);
    document.getElementById("chat-container").scrollTop = 9999;

    try {
        const res = await fetch("/api/chat", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({ message: message })
        });

        const data = await res.json();
        typing.remove();

        if (data.reply) {
            addMessage("ai", data.reply);
            history.push({role: "assistant", content: data.reply});
        }
    } catch (e) {
        typing.remove();
        addMessage("ai", "Something went wrong. Please try again.");
    }
}

function toggleVoiceInput() {
    const btn = document.getElementById("mic-btn");
    btn.classList.add("listening");

    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    const recognition = new SpeechRecognition();
    recognition.lang = "en-US";

    recognition.onresult = (event) => {
        const text = event.results[0][0].transcript;
        sendMessage(text);
        btn.classList.remove("listening");
    };

    recognition.onerror = () => btn.classList.remove("listening");
    recognition.onend = () => btn.classList.remove("listening");

    recognition.start();
}

// Welcome
document.addEventListener("DOMContentLoaded", () => {
    addMessage("ai", "Hello! How can I help you today?");
});