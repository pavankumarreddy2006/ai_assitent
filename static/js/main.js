"use strict";

/* ========================
   STATE
======================== */
let conversationHistory = [];
let isListening = false;
let isSpeaking = false;
let recognition = null;
let voices = [];
let editingHistoryIndex = null;

const API_BASE = "";

/* ========================
   DOM REFS
======================== */
const messagesEl      = document.getElementById("messages");
const welcomeEl       = document.getElementById("welcome");
const inputForm       = document.getElementById("inputForm");
const messageInput    = document.getElementById("messageInput");
const sendBtn         = document.getElementById("sendBtn");
const micBtn          = document.getElementById("micBtn");
const typingIndicator = document.getElementById("typingIndicator");
const greetingEl      = document.getElementById("greeting");
const statusDot       = document.getElementById("statusDot");
const sysStatusEl     = document.getElementById("sysStatus");
const infoPanel       = document.getElementById("infoPanel");
const infoToggle      = document.getElementById("infoToggle");
const infoClose       = document.getElementById("infoClose");
const infoContent     = document.getElementById("infoContent");
const newsContent     = document.getElementById("newsContent");
const speakerAnim     = document.getElementById("speakerAnim");
const stopSpeakBtn    = document.getElementById("stopSpeakBtn");
const toastEl         = document.getElementById("toast");

/* ========================
   GREETING
======================== */
function getGreeting() {
  const h = new Date().getHours();
  if (h >= 5  && h < 12) return "Good Morning";
  if (h >= 12 && h < 16) return "Good Afternoon";
  if (h >= 16 && h < 20) return "Good Evening";
  return "Good Night";
}

function updateGreeting() {
  if (greetingEl) greetingEl.textContent = getGreeting();
}

updateGreeting();
setInterval(updateGreeting, 60000);

/* ========================
   HEALTH CHECK
======================== */
async function checkHealth() {
  try {
    const res  = await fetch(`${API_BASE}/api/healthz`);
    const data = await res.json();
    if (data.status === "ok") {
      statusDot.classList.add("active");
      if (sysStatusEl) sysStatusEl.textContent = "";
    }
  } catch {
    statusDot.classList.remove("active");
  }
}

checkHealth();
setInterval(checkHealth, 30000);

/* ========================
   COLLEGE INFO PANEL
======================== */
async function loadCollegeInfo() {
  try {
    const res  = await fetch(`${API_BASE}/api/college-info`);
    const data = await res.json();

    infoContent.innerHTML = `
      <div class="info-section">
        <div class="info-label">Key Courses</div>
        <div class="tags">
          ${data.courses.map(c => `<span class="tag">${escapeHtml(c)}</span>`).join("")}
        </div>
      </div>
      <div class="info-section">
        <div class="info-label">Facilities</div>
        <div class="tags">
          ${data.facilities.map(f => `<span class="tag">${escapeHtml(f)}</span>`).join("")}
        </div>
      </div>
      <div class="info-section">
        <div class="info-label">Contact</div>
        <div class="contact-row">
          <span class="contact-icon">&#9742;</span>
          <span>${escapeHtml(data.contact)}</span>
        </div>
        <div class="contact-row">
          <span class="contact-icon">&#9993;</span>
          <span>${escapeHtml(data.email || "idealcolleges@gmail.com")}</span>
        </div>
        <div class="contact-row">
          <a class="info-link" href="${escapeHtml(data.website)}" target="_blank">
            &#127760; ${escapeHtml(data.website)}
          </a>
        </div>
      </div>
      <div class="info-section">
        <div class="info-label">Timings</div>
        <div class="contact-row">
          <span class="contact-icon">&#9200;</span>
          <span>9:30 AM – 3:45 PM (Mon–Sat)</span>
        </div>
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

    if (!articles || articles.length === 0) {
      newsContent.innerHTML = `<p class="info-loading">No news available.</p>`;
      return;
    }

    newsContent.innerHTML = articles.slice(0, 5).map(a => {
      const url = escapeHtml(a.url || "");
      return `
        <div class="news-item" onclick="${url ? `window.open('${url}','_blank')` : ''}">
          <div class="news-title">${escapeHtml(a.title || "")}</div>
          <div class="news-source">${escapeHtml(a.source || "Unknown")}</div>
        </div>
      `;
    }).join("");
  } catch {
    newsContent.innerHTML = `<p class="info-loading">Could not fetch news.</p>`;
  }
}

loadCollegeInfo();
loadNews();

/* ========================
   PANEL TOGGLE (MOBILE)
======================== */
if (infoToggle) {
  infoToggle.addEventListener("click", () => infoPanel.classList.add("open"));
}
if (infoClose) {
  infoClose.addEventListener("click", () => infoPanel.classList.remove("open"));
}

/* ========================
   VOICE — RECOGNITION
   Only activates when user presses mic button
======================== */
const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

if (SpeechRecognition) {
  recognition = new SpeechRecognition();
  recognition.lang = "te-IN";
  recognition.continuous = false;
  recognition.interimResults = true;

  recognition.onresult = (e) => {
    let interim = "";
    let final_text = "";
    for (let i = e.resultIndex; i < e.results.length; i++) {
      const t = e.results[i][0].transcript;
      if (e.results[i].isFinal) {
        final_text += t;
      } else {
        interim += t;
      }
    }
    if (interim) messageInput.value = interim;
    if (final_text.trim()) {
      messageInput.value = final_text.trim();
      setListeningState(false);
      sendMessage(final_text.trim());
    }
  };

  recognition.onerror = (e) => {
    setListeningState(false);
    if (e.error === "no-speech") showToast("No speech detected. Try again.");
  };
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
  if (!recognition) {
    showToast("Voice not supported in this browser");
    return;
  }
  if (isListening) {
    recognition.stop();
    setListeningState(false);
  } else {
    stopSpeaking();
    recognition.start();
    setListeningState(true);
    showToast("Listening... speak now (Telugu or English)");
  }
});

/* ========================
   VOICE — SYNTHESIS (TTS)
   Auto-speaks AI responses in correct language
======================== */
function loadVoices() {
  voices = window.speechSynthesis ? window.speechSynthesis.getVoices() : [];
}

loadVoices();
if (window.speechSynthesis) {
  window.speechSynthesis.onvoiceschanged = loadVoices;
}

function isTeluguText(text) {
  return /[\u0C00-\u0C7F]/.test(text);
}

function getBestVoice(isTeluguReply) {
  if (!voices.length) return null;

  if (isTeluguReply) {
    const teIN = voices.find(v => v.lang === "te-IN");
    if (teIN) return teIN;
    const te = voices.find(v => v.lang.startsWith("te"));
    if (te) return te;
    const indiaFemale = voices.find(v =>
      (v.lang === "hi-IN" || v.lang === "en-IN") &&
      v.name.toLowerCase().includes("female")
    );
    if (indiaFemale) return indiaFemale;
    const india = voices.find(v => v.lang === "en-IN" || v.lang === "hi-IN");
    if (india) return india;
  }

  const preferred = [
    "Microsoft Heera - Telugu (India)",
    "Google हिन्दी",
    "Google UK English Female",
    "Microsoft Jenny Online (Natural) - English (United States)",
    "Microsoft Aria Online (Natural) - English (United States)",
    "Microsoft Zira - English (United States)",
    "Google US English",
    "Samantha", "Karen", "Moira", "Victoria"
  ];

  for (const name of preferred) {
    const v = voices.find(vv => vv.name === name);
    if (v) return v;
  }

  return voices.find(v => v.lang === "en-IN")
      || voices.find(v => v.lang.startsWith("en") && v.name.toLowerCase().includes("female"))
      || voices.find(v => v.lang.startsWith("en"))
      || null;
}

function cleanForSpeech(text) {
  return text
    .replace(/https?:\/\/[^\s]+/g, "")
    .replace(/[\r\n]+/g, ". ")
    .replace(/[*_~`#\[\]]/g, "")
    .replace(/\d+\.\s+/g, "")
    .replace(/\.\s*\.\s*\./g, ".")
    .replace(/\s{2,}/g, " ")
    .trim();
}

function speak(text) {
  if (!window.speechSynthesis) return;
  stopSpeaking();

  const cleaned = cleanForSpeech(text);
  if (!cleaned) return;

  const CHUNK = 200;
  const sentences = cleaned.match(/[^.!?।]+[.!?।]*/g) || [cleaned];
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
  showSpeakerAnim(true);

  const isTe = isTeluguText(text);

  function speakNext() {
    if (idx >= chunks.length) {
      isSpeaking = false;
      micBtn.classList.remove("speaking");
      showSpeakerAnim(false);
      return;
    }

    const chunk = chunks[idx++];
    const chunkIsTe = isTeluguText(chunk);
    const utter = new SpeechSynthesisUtterance(chunk);
    utter.lang  = chunkIsTe ? "te-IN" : "en-IN";
    utter.rate  = chunkIsTe ? 0.82 : 0.88;
    utter.pitch = 1.05;
    utter.volume = 1.0;

    const v = getBestVoice(chunkIsTe);
    if (v) utter.voice = v;

    utter.onend   = speakNext;
    utter.onerror = () => {
      isSpeaking = false;
      micBtn.classList.remove("speaking");
      showSpeakerAnim(false);
    };

    window.speechSynthesis.speak(utter);
  }

  setTimeout(speakNext, 80);
}

function stopSpeaking() {
  if (window.speechSynthesis) window.speechSynthesis.cancel();
  isSpeaking = false;
  micBtn.classList.remove("speaking");
  showSpeakerAnim(false);
}

if (stopSpeakBtn) {
  stopSpeakBtn.addEventListener("click", stopSpeaking);
}

/* ========================
   WAVEFORM ANIMATION
======================== */
function showSpeakerAnim(show) {
  if (!speakerAnim) return;
  speakerAnim.style.display = show ? "block" : "none";
}

/* ========================
   MESSAGES
======================== */
function addMessage(role, content, meta = {}) {
  if (welcomeEl) welcomeEl.style.display = "none";

  const div = document.createElement("div");
  div.className = `message ${role}`;

  let actionsHtml = "";
  const historyIdx = conversationHistory.length;
  if (role === "user") {
    actionsHtml = `
      <div class="msg-actions">
        <button class="edit-btn" data-text="${escapeAttr(content)}" data-idx="${historyIdx}">
          &#9998; Edit
        </button>
      </div>
    `;
  }

  div.innerHTML = `
    <div class="msg-wrapper">
      <div class="bubble">${escapeHtml(content)}</div>
      ${actionsHtml}
    </div>
  `;

  const editBtn = div.querySelector(".edit-btn");
  if (editBtn) {
    editBtn.addEventListener("click", () => {
      const text = editBtn.getAttribute("data-text");
      const idx  = parseInt(editBtn.getAttribute("data-idx"), 10);
      startEdit(text, idx, div);
    });
  }

  messagesEl.appendChild(div);
  messagesEl.scrollTop = messagesEl.scrollHeight;
  return div;
}

/* ========================
   EDIT MESSAGE
======================== */
function startEdit(text, historyIndex, msgDiv) {
  messageInput.value = text;
  messageInput.focus();

  inputForm.classList.add("editing");

  let label = document.getElementById("editingLabel");
  if (!label) {
    label = document.createElement("div");
    label.id = "editingLabel";
    label.className = "editing-label visible";
    label.textContent = "Editing message — press Enter or Send to resend";
    inputForm.parentElement.insertBefore(label, inputForm);
  } else {
    label.className = "editing-label visible";
  }

  const allMsgs = messagesEl.querySelectorAll(".message");
  let found = false;
  allMsgs.forEach(m => {
    if (m === msgDiv) { found = true; }
    if (found) m.remove();
  });

  conversationHistory = conversationHistory.slice(0, historyIndex - 1);
  editingHistoryIndex = historyIndex;
  showToast("Message loaded for editing");
}

function clearEditMode() {
  inputForm.classList.remove("editing");
  const label = document.getElementById("editingLabel");
  if (label) label.className = "editing-label";
  editingHistoryIndex = null;
}

/* ========================
   TOAST
======================== */
let toastTimer = null;
function showToast(msg, duration = 2200) {
  if (!toastEl) return;
  toastEl.textContent = msg;
  toastEl.style.display = "block";
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => { toastEl.style.display = "none"; }, duration);
}

/* ========================
   ESCAPE HELPERS
======================== */
function escapeHtml(str) {
  if (!str) return "";
  return String(str)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

function escapeAttr(str) {
  if (!str) return "";
  return String(str)
    .replace(/&/g, "&amp;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#39;");
}

/* ========================
   TYPING
======================== */
function showTyping() {
  typingIndicator.style.display = "flex";
  messagesEl.scrollTop = messagesEl.scrollHeight;
}

function hideTyping() {
  typingIndicator.style.display = "none";
}

/* ========================
   SEND MESSAGE
======================== */
async function sendMessage(text) {
  const msg = (text || messageInput.value).trim();
  if (!msg) return;

  messageInput.value = "";
  sendBtn.disabled   = true;
  stopSpeaking();
  clearEditMode();

  addMessage("user", msg);
  conversationHistory.push({ role: "user", content: msg });
  showTyping();

  try {
    const res = await fetch(`${API_BASE}/api/chat`, {
      method:  "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        message: msg,
        conversationHistory: conversationHistory.slice(-12)
      })
    });

    const data = await res.json();
    hideTyping();

    const reply = data.reply || "I didn't get a response. Please try again.";
    addMessage("assistant", reply, { intent: data.intent, source: data.source });
    conversationHistory.push({ role: "assistant", content: reply });

    setTimeout(() => speak(reply), 150);

  } catch (err) {
    hideTyping();
    addMessage("assistant", "Connection error. Please check your network and try again.");
    console.error("[Chat Error]", err);
  } finally {
    sendBtn.disabled = false;
    messageInput.focus();
  }
}

/* ========================
   FORM & KEYBOARD EVENTS
======================== */
inputForm.addEventListener("submit", (e) => {
  e.preventDefault();
  sendMessage();
});

messageInput.addEventListener("keydown", (e) => {
  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault();
    sendMessage();
  }
  if (e.key === "Escape") {
    clearEditMode();
    messageInput.value = "";
  }
});

document.querySelectorAll(".suggestion-btn").forEach(btn => {
  btn.addEventListener("click", () => sendMessage(btn.textContent.trim()));
});
