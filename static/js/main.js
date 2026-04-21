// static/js/main.js
let chatInput;
let sendBtn;
let messagesArea;
let welcomeScreen;
let micBtn;
let transcriptPreview;

let chatHistory = [];
let recognition = null;
let isListening = false;

function esc(str) {
  return String(str)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function scrollBottom() {
  messagesArea.scrollTop = messagesArea.scrollHeight;
}

function appendUserMessage(text) {
  const div = document.createElement("div");
  div.className = "message user-message";
  div.innerHTML = `<div class="message-bubble user-bubble"><p>${esc(text)}</p></div>`;
  messagesArea.appendChild(div);
  scrollBottom();
}

function appendAIMessage(data) {
  const reply = data?.reply ?? "";
  const source = data?.source ?? "";
  const showImages = Boolean(data?.show_images);
  const showVideo = Boolean(data?.show_video);
  const images = Array.isArray(data?.images) ? data.images : [];
  const videoUrl = data?.video_url ?? "";

  let media = "";
  if (showImages && images.length) {
    media += `<div class="media-container images-grid" style="margin-top:10px;display:flex;flex-wrap:wrap;gap:8px;">`;
    images.forEach((src) => {
      media += `<img src="${esc(src)}" alt="college image" style="max-width:220px;border-radius:10px;border:1px solid #283448;">`;
    });
    media += `</div>`;
  }
  if (showVideo && videoUrl) {
    media += `<div style="margin-top:10px;"><video controls autoplay style="width:100%;max-height:320px;border-radius:10px;" src="${esc(videoUrl)}"></video></div>`;
  }

  const div = document.createElement("div");
  div.className = "message ai-message";
  div.innerHTML = `
    <div class="message-bubble ai-bubble">
      <p>${esc(reply)}</p>
      ${media}
      ${source ? `<div class="message-source" style="font-size:12px;color:#93a4bf;margin-top:8px;">${esc(source)}</div>` : ""}
    </div>
  `;
  messagesArea.appendChild(div);
  scrollBottom();
}

function appendTyping() {
  const id = "typing-" + Date.now();
  const div = document.createElement("div");
  div.id = id;
  div.className = "message ai-message";
  div.innerHTML = `
    <div class="message-bubble ai-bubble">
      <div class="typing-indicator"><span>.</span><span>.</span><span>.</span></div>
    </div>`;
  messagesArea.appendChild(div);
  scrollBottom();
  return id;
}

function removeElement(id) {
  const el = document.getElementById(id);
  if (el) el.remove();
}

async function sendMessage() {
  const text = (chatInput.value || "").trim();
  if (!text) return;

  welcomeScreen.style.display = "none";
  messagesArea.style.display = "flex";

  appendUserMessage(text);
  chatHistory.push({ role: "user", content: text });

  chatInput.value = "";
  sendBtn.disabled = true;
  const typingId = appendTyping();

  try {
    const res = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: text, history: chatHistory.slice(-10) }),
    });

    let data;
    try {
      data = await res.json();
    } catch {
      throw new Error("Invalid response");
    }

    removeElement(typingId);

    if (res.ok && typeof data.reply !== "undefined") {
      appendAIMessage(data);
      chatHistory.push({ role: "assistant", content: data.reply });
    } else {
      appendAIMessage({ reply: data?.reply || "Server error.", source: "System" });
    }
  } catch (err) {
    console.error(err);
    removeElement(typingId);
    appendAIMessage({ reply: "Sorry, I couldn't connect to server.", source: "System" });
  } finally {
    sendBtn.disabled = false;
    scrollBottom();
  }
}

function setTranscriptPreview(text) {
  if (!transcriptPreview) return;
  transcriptPreview.textContent = text || "";
}

function initRecognition() {
  const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (!SR) return null;

  const rec = new SR();
  rec.lang = "en-IN";
  rec.interimResults = true;
  rec.continuous = false;
  rec.maxAlternatives = 1;

  rec.onresult = (event) => {
    let transcript = "";
    for (let i = event.resultIndex; i < event.results.length; i++) {
      transcript += event.results[i][0].transcript;
    }
    chatInput.value = transcript;
    setTranscriptPreview(transcript);

    const last = event.results[event.results.length - 1];
    if (last && last.isFinal) {
      setTimeout(() => {
        setTranscriptPreview("");
        sendMessage();
      }, 200);
    }
  };

  rec.onerror = () => {
    isListening = false;
    micBtn.classList.remove("active");
    setTranscriptPreview("");
  };

  rec.onend = () => {
    isListening = false;
    micBtn.classList.remove("active");
    setTranscriptPreview("");
  };

  return rec;
}

function toggleVoice() {
  if (!recognition) recognition = initRecognition();
  if (!recognition) {
    appendAIMessage({ reply: "Voice is not supported in this browser. Use Chrome/Edge.", source: "System" });
    return;
  }

  if (isListening) {
    recognition.stop();
    isListening = false;
    micBtn.classList.remove("active");
    return;
  }

  try {
    recognition.start();
    isListening = true;
    micBtn.classList.add("active");
    setTranscriptPreview("Listening...");
  } catch {
    isListening = false;
    micBtn.classList.remove("active");
  }
}

function sendSuggestion(text) {
  chatInput.value = text;
  sendMessage();
}

document.addEventListener("DOMContentLoaded", () => {
  chatInput = document.getElementById("chatInput");
  sendBtn = document.getElementById("sendBtn");
  messagesArea = document.getElementById("messagesArea");
  welcomeScreen = document.getElementById("welcomeScreen");
  micBtn = document.getElementById("micBtn");
  transcriptPreview = document.getElementById("transcriptPreview");

  sendBtn.addEventListener("click", sendMessage);
  micBtn.addEventListener("click", toggleVoice);

  chatInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter") {
      e.preventDefault();
      sendMessage();
    }
  });

  document.querySelectorAll(".suggestion-btn").forEach((btn) => {
    btn.addEventListener("click", () => sendSuggestion(btn.getAttribute("data-text") || btn.textContent || ""));
  });
});