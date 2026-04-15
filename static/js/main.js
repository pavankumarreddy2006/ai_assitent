"use strict";

/* ========================
   STATE
======================== */
let conversationHistory = [];
let isListening = false;
let isSpeaking = false;
let recognition = null;
let voices = [];

const API_BASE = "";

/* ========================
   DOM REFS
======================== */
const messagesEl = document.getElementById("messages");
const welcomeEl = document.getElementById("welcome");
const inputForm = document.getElementById("inputForm");
const messageInput = document.getElementById("messageInput");
const sendBtn = document.getElementById("sendBtn");
const micBtn = document.getElementById("micBtn");
const typingIndicator = document.getElementById("typingIndicator");
const greetingEl = document.getElementById("greeting");
const statusDot = document.getElementById("statusDot");
const sysStatus = document.getElementById("sysStatus");
const infoPanel = document.getElementById("infoPanel");
const infoToggle = document.getElementById("infoToggle");
const infoContent = document.getElementById("infoContent");
const newsContent = document.getElementById("newsContent");

/* ========================
   GREETING
======================== */
function getGreeting() {
  const h = new Date().getHours();
  if (h >= 6 && h < 12) return "Good Morning";
  if (h >= 12 && h < 16) return "Good Afternoon";
  if (h >= 16 && h < 20) return "Good Evening";
  return "Good Night";
}

function updateGreeting() {
  greetingEl.textContent = getGreeting();
}

updateGreeting();
setInterval(updateGreeting, 60000);

/* ========================
   HEALTH CHECK
======================== */
async function checkHealth() {
  try {
    const res = await fetch(`${API_BASE}/api/healthz`);
    const data = await res.json();
    if (data.status === "ok") {
      statusDot.classList.add("active");
      sysStatus = ""; // quiet if ok
    }
  } catch {
    statusDot.classList.remove("active");
  }
}

checkHealth();
setInterval(checkHealth, 30000);

/* ========================
   COLLEGE INFO
======================== */
async function loadCollegeInfo() {
  try {
    const res = await fetch(`${API_BASE}/api/college-info`);
    const data = await res.json();

    infoContent.innerHTML = `
      <div class="info-section">
        <div class="info-label">Facilities</div>
        <div class="tags">
          ${data.facilities.map(f => `<span class="tag">${f}</span>`).join("")}
        </div>
      </div>
      <div class="info-section">
        <div class="info-label">Key Courses</div>
        <div class="tags">
          ${data.courses.slice(0, 6).map(c => `<span class="tag">${c}</span>`).join("")}
          ${data.courses.length > 6 ? `<span class="tag">+${data.courses.length - 6} more</span>` : ""}
        </div>
      </div>
      <div class="info-section">
        <div class="contact-row"><span class="contact-icon">&#9742;</span><span>${data.contact}</span></div>
        <div class="contact-row"><a class="info-link" href="${data.website}" target="_blank">&#127760; Official Website</a></div>
      </div>
    `;
  } catch {
    infoContent.innerHTML = `<p class="info-loading">Could not load college info.</p>`;
  }
}

async function loadNews() {
  try {
    const res = await fetch(`${API_BASE}/api/news`);
    const { articles } = await res.json();
    if (articles.length === 0) {
      newsContent.innerHTML = `<p class="info-loading">No news available.</p>`;
      return;
    }
    newsContent.innerHTML = articles.slice(0, 5).map(a => `
      <div class="news-item">
        <div class="news-title">${a.title}</div>
        <div class="news-source">${a.source || "Unknown"}</div>
      </div>
    `).join("");
  } catch {
    newsContent.innerHTML = `<p class="info-loading">Could not fetch news.</p>`;
  }
}

loadCollegeInfo();
loadNews();

/* ========================
   MOBILE PANEL TOGGLE
======================== */
infoToggle.addEventListener("click", () => {
  infoPanel.classList.toggle("open");
});

/* ========================
   VOICE — RECOGNITION
======================== */
const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
if (SpeechRecognition) {
  recognition = new SpeechRecognition();
  recognition.lang = "en-US";
  recognition.continuous = false;
  recognition.interimResults = false;

  recognition.onresult = (e) => {
    const transcript = e.results[0][0].transcript;
    messageInput.value = transcript;
    setListeningState(false);
    if (transcript.trim()) sendMessage(transcript.trim());
  };

  recognition.onerror = () => setListeningState(false);
  recognition.onend = () => setListeningState(false);
}

function setListeningState(val) {
  isListening = val;
  micBtn.classList.toggle("listening", val);
}

micBtn.addEventListener("click", () => {
  if (isSpeaking) {
    stopSpeaking();
    return;
  }
  if (!recognition) return;
  if (isListening) {
    recognition.stop();
    setListeningState(false);
  } else {
    stopSpeaking();
    recognition.start();
    setListeningState(true);
  }
});

/* ========================
   VOICE — SYNTHESIS
======================== */
function loadVoices() {
  voices = window.speechSynthesis.getVoices();
}
loadVoices();
if (window.speechSynthesis) {
  window.speechSynthesis.onvoiceschanged = loadVoices;
}

function getBestVoice() {
  const preferred = [
    "Google US English",
    "Google UK English Female",
    "Microsoft Jenny Online (Natural) - English (United States)",
    "Microsoft Aria Online (Natural) - English (United States)",
    "Samantha", "Karen", "Moira"
  ];
  for (const name of preferred) {
    const v = voices.find(v => v.name === name);
    if (v) return v;
  }
  return voices.find(v => v.lang.startsWith("en")) || null;
}

function cleanForSpeech(text) {
  return text
    .replace(/https?:\/\/[^\s]+/g, "")
    .replace(/\n+/g, ". ")
    .replace(/[*_~`#]/g, "")
    .replace(/\d+\.\s/g, "")
    .replace(/\s{2,}/g, " ")
    .trim();
}

function speak(text) {
  if (!window.speechSynthesis) return;
  stopSpeaking();

  const cleaned = cleanForSpeech(text);
  if (!cleaned) return;

  const CHUNK = 180;
  const sentences = cleaned.match(/[^.!?]+[.!?]*/g) || [cleaned];
  const chunks = [];
  let current = "";

  for (const s of sentences) {
    if ((current + s).length > CHUNK) {
      if (current) chunks.push(current.trim());
      current = s;
    } else {
      current += " " + s;
    }
  }
  if (current.trim()) chunks.push(current.trim());

  let idx = 0;
  isSpeaking = true;
  micBtn.classList.add("speaking");

  function speakNext() {
    if (idx >= chunks.length) {
      isSpeaking = false;
      micBtn.classList.remove("speaking");
      return;
    }
    const utter = new SpeechSynthesisUtterance(chunks[idx++]);
    utter.lang = "en-US";
    utter.rate = 0.88;
    utter.pitch = 1.05;
    utter.volume = 1.0;

    const v = getBestVoice();
    if (v) utter.voice = v;

    utter.onend = speakNext;
    utter.onerror = () => { isSpeaking = false; micBtn.classList.remove("speaking"); };
    window.speechSynthesis.speak(utter);
  }

  setTimeout(speakNext, 100);
}

function stopSpeaking() {
  window.speechSynthesis && window.speechSynthesis.cancel();
  isSpeaking = false;
  micBtn.classList.remove("speaking");
}

/* ========================
   MESSAGES
======================== */
function addMessage(role, content, meta = {}) {
  if (welcomeEl) welcomeEl.style.display = "none";

  const div = document.createElement("div");
  div.className = `message ${role}`;

  let metaHtml = "";
  if (role === "assistant" && meta.intent) {
    metaHtml = `
      <div class="meta">
        <span class="badge">${meta.intent}</span>
        ${meta.source ? `<span class="badge">${meta.source}</span>` : ""}
      </div>
    `;
  }

  div.innerHTML = `
    <div>
      <div class="bubble">${escapeHtml(content)}</div>
      ${metaHtml}
    </div>
  `;

  messagesEl.appendChild(div);
  messagesEl.scrollTop = messagesEl.scrollHeight;
}

function escapeHtml(str) {
  return str
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

function showTyping() { typingIndicator.style.display = "block"; messagesEl.scrollTop = messagesEl.scrollHeight; }
function hideTyping() { typingIndicator.style.display = "none"; }

/* ========================
   SEND MESSAGE
======================== */
async function sendMessage(text) {
  const msg = text || messageInput.value.trim();
  if (!msg) return;

  messageInput.value = "";
  sendBtn.disabled = true;
  stopSpeaking();

  addMessage("user", msg);
  conversationHistory.push({ role: "user", content: msg });
  showTyping();

  try {
    const res = await fetch(`${API_BASE}/api/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        message: msg,
        conversationHistory: conversationHistory.slice(-10)
      })
    });

    const data = await res.json();
    hideTyping();

    const reply = data.reply || "I didn't get a response.";
    addMessage("assistant", reply, { intent: data.intent, source: data.source });
    conversationHistory.push({ role: "assistant", content: reply });

    setTimeout(() => speak(reply), 200);
  } catch (err) {
    hideTyping();
    addMessage("assistant", "Something went wrong. Please try again.");
  } finally {
    sendBtn.disabled = false;
    messageInput.focus();
  }
}

inputForm.addEventListener("submit", (e) => {
  e.preventDefault();
  sendMessage();
});

messageInput.addEventListener("keydown", (e) => {
  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault();
    sendMessage();
  }
});

/* Suggestion buttons */
document.querySelectorAll(".suggestion-btn").forEach(btn => {
  btn.addEventListener("click", () => sendMessage(btn.textContent));
});
