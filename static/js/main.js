const API_BASE = "";
let chatHistory = [];
let voiceState = "idle";
let recognition = null;

const chatInput      = document.getElementById("chatInput");
const sendBtn        = document.getElementById("sendBtn");
const messagesArea   = document.getElementById("messagesArea");
const welcomeScreen  = document.getElementById("welcomeScreen");
const micBtn         = document.getElementById("micBtn");
const newsList       = document.getElementById("newsList");
const transcriptEl   = document.getElementById("transcriptPreview");

/* ── Init ─────────────────────────────────────────────────── */
chatInput.addEventListener("keydown", e => {
  if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); sendMessage(); }
});

chatInput.addEventListener("input", () => {
  sendBtn.disabled = !chatInput.value.trim();
});

window.addEventListener("load", () => {
  loadNews();
  const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (!SR) micBtn.style.display = "none";
});

/* ── Send message ─────────────────────────────────────────── */
function sendSuggestion(text) {
  chatInput.value = text;
  sendBtn.disabled = false;
  sendMessage();
}

async function sendMessage() {
  const text = chatInput.value.trim();
  if (!text) return;

  welcomeScreen.style.display = "none";
  messagesArea.style.display  = "flex";

  appendUserMessage(text);
  chatHistory.push({ role: "user", content: text });
  chatInput.value  = "";
  sendBtn.disabled = true;

  const typingId = appendTyping();

  try {
    const res = await fetch(`${API_BASE}/api/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: text, history: chatHistory.slice(-10) })
    });

    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();

    removeElement(typingId);
    appendAIMessage(data);
    chatHistory.push({ role: "assistant", content: data.reply });
  } catch (err) {
    removeElement(typingId);
    appendSimpleAIMessage("Sorry, I couldn't connect. Please try again.", "System");
  }

  scrollBottom();
}

/* ── DOM helpers ──────────────────────────────────────────── */
function appendUserMessage(text) {
  const row = document.createElement("div");
  row.className = "msg-row msg-row--user";

  const avatar = mkAvatar("user");
  const body   = document.createElement("div");
  body.className = "msg-body";

  const bubble = document.createElement("div");
  bubble.className = "bubble bubble--user";
  bubble.textContent = text;
  body.appendChild(bubble);

  row.appendChild(body);
  row.appendChild(avatar);
  messagesArea.appendChild(row);
  scrollBottom();
}

function appendSimpleAIMessage(text, source) {
  const row    = document.createElement("div");
  row.className = "msg-row msg-row--ai";
  const avatar = mkAvatar("ai");
  const body   = document.createElement("div");
  body.className = "msg-body";
  const bubble = document.createElement("div");
  bubble.className = "bubble bubble--ai";
  bubble.textContent = text;
  body.appendChild(bubble);
  if (source) {
    const s = document.createElement("span");
    s.className = "msg-source";
    s.textContent = source;
    body.appendChild(s);
  }
  row.appendChild(avatar);
  row.appendChild(body);
  messagesArea.appendChild(row);
  scrollBottom();
}

function appendAIMessage(data) {
  const row    = document.createElement("div");
  row.className = "msg-row msg-row--ai";
  const avatar = mkAvatar("ai");
  const body   = document.createElement("div");
  body.className = "msg-body";

  const bubble = document.createElement("div");
  bubble.className = "bubble bubble--ai";
  bubble.textContent = data.reply;
  body.appendChild(bubble);

  if (data.show_images && data.images && data.images.length > 0) {
    const grid = document.createElement("div");
    grid.className = "image-grid";
    data.images.forEach((src, i) => {
      const img = document.createElement("img");
      img.src = src;
      img.alt = `Campus ${i + 1}`;
      img.onerror = () => { img.src = `https://picsum.photos/seed/campus${i+1}/400/300`; };
      grid.appendChild(img);
    });
    body.appendChild(grid);
  }

  if (data.show_video && data.video_url) {
    const wrapper = document.createElement("div");
    wrapper.className = "video-wrapper";
    const vid = document.createElement("video");
    vid.controls = true;
    vid.autoplay = true;
    const src = document.createElement("source");
    src.src  = data.video_url;
    src.type = "video/mp4";
    vid.appendChild(src);
    wrapper.appendChild(vid);
    body.appendChild(wrapper);
  }

  if (data.source) {
    const srcEl = document.createElement("span");
    srcEl.className = "msg-source";
    srcEl.textContent = data.source;
    body.appendChild(srcEl);
  }

  row.appendChild(avatar);
  row.appendChild(body);
  messagesArea.appendChild(row);
  scrollBottom();
}

function appendTyping() {
  const id = "typing-" + Date.now();
  const row = document.createElement("div");
  row.className = "msg-row msg-row--ai";
  row.id = id;

  const avatar = mkAvatar("ai");
  const body   = document.createElement("div");
  body.className = "msg-body";

  const bubble = document.createElement("div");
  bubble.className = "bubble bubble--ai";
  bubble.innerHTML = `<div class="typing-indicator"><span></span><span></span><span></span></div>`;
  body.appendChild(bubble);

  row.appendChild(avatar);
  row.appendChild(body);
  messagesArea.appendChild(row);
  scrollBottom();
  return id;
}

function mkAvatar(role) {
  const el = document.createElement("div");
  el.className = `avatar avatar--${role}`;
  el.textContent = role === "user" ? "U" : "A";
  return el;
}

function removeElement(id) {
  const el = document.getElementById(id);
  if (el) el.remove();
}

function scrollBottom() {
  messagesArea.scrollTop = messagesArea.scrollHeight;
}

/* ── Voice input ──────────────────────────────────────────── */
function toggleVoice() {
  if (voiceState === "listening") {
    if (recognition) recognition.stop();
    return;
  }

  const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (!SR) return;

  recognition = new SR();
  recognition.continuous     = false;
  recognition.interimResults = true;
  recognition.lang = "en-IN";

  recognition.onstart = () => {
    voiceState = "listening";
    micBtn.classList.add("active");
  };

  recognition.onresult = e => {
    let interim = "", final = "";
    for (let i = e.resultIndex; i < e.results.length; i++) {
      const t = e.results[i][0].transcript;
      if (e.results[i].isFinal) final += t;
      else interim += t;
    }
    const text = final || interim;
    transcriptEl.textContent    = text;
    transcriptEl.style.display  = text ? "block" : "none";
    if (final) chatInput.value  = final;
  };

  recognition.onend = () => {
    voiceState = "idle";
    micBtn.classList.remove("active");
    transcriptEl.style.display  = "none";
    transcriptEl.textContent    = "";
    const val = chatInput.value.trim();
    if (val) sendMessage();
  };

  recognition.onerror = () => {
    voiceState = "idle";
    micBtn.classList.remove("active");
    transcriptEl.style.display = "none";
  };

  recognition.start();
}

/* ── News sidebar ─────────────────────────────────────────── */
async function loadNews() {
  try {
    const res  = await fetch(`${API_BASE}/api/news`);
    if (!res.ok) return;
    const data = await res.json();
    if (!data || !data.length) return;

    newsList.innerHTML = "";
    data.slice(0, 5).forEach(item => {
      const div = document.createElement("div");
      div.className = "news-item";
      div.innerHTML = `
        <div class="news-title">${escHtml(item.title)}</div>
        <div class="news-source">${escHtml(item.source)}</div>`;
      newsList.appendChild(div);
    });
  } catch {
    newsList.innerHTML = `<div class="news-loading">Could not load updates.</div>`;
  }
}

function escHtml(str) {
  return (str || "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}
