"use strict";

let conversationHistory = [];
let isListening = false;
let isSpeaking = false;
let recognition = null;
let voices = [];
let finalTranscript = "";

const API_BASE = "";
const messagesEl = document.getElementById("messages");
const welcomeEl = document.getElementById("welcome");
const micBtn = document.getElementById("micBtn");
const typingIndicator = document.getElementById("typingIndicator");
const greetingEl = document.getElementById("greeting");
const statusDot = document.getElementById("statusDot");
const sysStatusEl = document.getElementById("sysStatus");
const infoPanel = document.getElementById("infoPanel");
const infoToggle = document.getElementById("infoToggle");
const infoClose = document.getElementById("infoClose");
const infoContent = document.getElementById("infoContent");
const newsContent = document.getElementById("newsContent");
const speakerAnim = document.getElementById("speakerAnim");
const stopSpeakBtn = document.getElementById("stopSpeakBtn");
const toastEl = document.getElementById("toast");
const voiceStatus = document.getElementById("voiceStatus");
const voiceTranscript = document.getElementById("voiceTranscript");

function getGreeting() {
  const h = new Date().getHours();
  if (h >= 5 && h < 12) return "Good Morning";
  if (h >= 12 && h < 16) return "Good Afternoon";
  if (h >= 16 && h < 20) return "Good Evening";
  return "Good Night";
}

function updateGreeting() {
  if (greetingEl) greetingEl.textContent = getGreeting();
}

updateGreeting();
setInterval(updateGreeting, 60000);

async function checkHealth() {
  try {
    const res = await fetch(`${API_BASE}/api/healthz`);
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

async function loadCollegeInfo() {
  try {
    const res = await fetch(`${API_BASE}/api/college-info`);
    const data = await res.json();
    infoContent.innerHTML = `
      <div class="info-section">
        <div class="info-label">About this AI</div>
        <p class="ai-copy">Ideal AI answers college questions, general questions, weather, web search, and latest news through voice.</p>
      </div>
      <div class="info-section">
        <div class="info-label">Language rule</div>
        <div class="ai-rule">User Telugu lo matladithe Telugu answer.</div>
        <div class="ai-rule">User English lo matladithe English answer.</div>
        <div class="ai-rule">Translation first kaadu. Direct same-language response.</div>
      </div>
      <div class="info-section">
        <div class="info-label">Voice mode</div>
        <div class="ai-rule">Tap Jarvis mic, speak, and listen to the full answer in a sweet female voice when available.</div>
      </div>
      <div class="info-section">
        <div class="info-label">College contact</div>
        <div class="contact-row"><span>${escapeHtml(data.contact)}</span></div>
        <div class="contact-row"><span>${escapeHtml(data.email || "idealcolleges@gmail.com")}</span></div>
        <div class="contact-row"><a class="info-link" href="${escapeHtml(data.website)}" target="_blank">${escapeHtml(data.website)}</a></div>
      </div>
    `;
  } catch {
    infoContent.innerHTML = `<p class="info-loading">Could not load AI info.</p>`;
  }
}

async function loadNews() {
  try {
    const res = await fetch(`${API_BASE}/api/news?query=latest%20India%20education`);
    const { articles } = await res.json();
    if (!articles || articles.length === 0) {
      newsContent.innerHTML = `<p class="info-loading">No news available.</p>`;
      return;
    }
    newsContent.innerHTML = articles.slice(0, 5).map(a => {
      const url = escapeHtml(a.url || "");
      const click = url ? `window.open('${url}','_blank')` : "";
      return `<div class="news-item" onclick="${click}"><div class="news-title">${escapeHtml(a.title || "")}</div><div class="news-source">${escapeHtml(a.source || "Unknown")}</div></div>`;
    }).join("");
  } catch {
    newsContent.innerHTML = `<p class="info-loading">Could not fetch news.</p>`;
  }
}

loadCollegeInfo();
loadNews();

if (infoToggle) infoToggle.addEventListener("click", () => infoPanel.classList.add("open"));
if (infoClose) infoClose.addEventListener("click", () => infoPanel.classList.remove("open"));

const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

if (SpeechRecognition) {
  recognition = new SpeechRecognition();
  recognition.lang = "te-IN";
  recognition.continuous = false;
  recognition.interimResults = true;
  recognition.maxAlternatives = 3;

  recognition.onstart = () => {
    finalTranscript = "";
    setListeningState(true);
    setVoiceText("Listening... Telugu or English lo matladandi", "Speak now");
  };

  recognition.onresult = (e) => {
    let interim = "";
    for (let i = e.resultIndex; i < e.results.length; i++) {
      const text = e.results[i][0].transcript;
      if (e.results[i].isFinal) finalTranscript += text;
      else interim += text;
    }
    const shown = (finalTranscript || interim).trim();
    if (shown) setVoiceText("Listening...", shown);
  };

  recognition.onerror = (e) => {
    setListeningState(false);
    if (e.error === "no-speech") setVoiceText("No speech detected", "Tap mic and try again");
    else setVoiceText("Voice error", "Please try again");
  };

  recognition.onend = () => {
    setListeningState(false);
    const msg = finalTranscript.trim();
    if (msg) sendMessage(msg);
    else if (!isSpeaking) setVoiceText("Tap the Jarvis mic and speak", "No message box. Voice only.");
  };
}

function setVoiceText(status, transcript) {
  if (voiceStatus) voiceStatus.textContent = status;
  if (voiceTranscript) voiceTranscript.textContent = transcript;
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
    showToast("Voice is not supported in this browser");
    return;
  }
  if (isListening) recognition.stop();
  else {
    stopSpeaking();
    recognition.start();
  }
});

function loadVoices() {
  voices = window.speechSynthesis ? window.speechSynthesis.getVoices() : [];
}

loadVoices();
if (window.speechSynthesis) window.speechSynthesis.onvoiceschanged = loadVoices;

function isTeluguText(text) {
  return /[\u0C00-\u0C7F]/.test(text);
}

function getBestVoice(isTeluguReply) {
  if (!voices.length) return null;
  const femaleNames = ["heera", "swara", "neural", "jenny", "aria", "zira", "samantha", "karen", "moira", "victoria", "female"];
  if (isTeluguReply) {
    return voices.find(v => v.lang === "te-IN" && femaleNames.some(n => v.name.toLowerCase().includes(n)))
      || voices.find(v => v.lang.startsWith("te"))
      || voices.find(v => v.lang === "hi-IN" && femaleNames.some(n => v.name.toLowerCase().includes(n)))
      || voices.find(v => v.lang === "en-IN" && femaleNames.some(n => v.name.toLowerCase().includes(n)))
      || voices.find(v => v.lang === "en-IN")
      || null;
  }
  return voices.find(v => v.lang === "en-IN" && femaleNames.some(n => v.name.toLowerCase().includes(n)))
    || voices.find(v => v.lang.startsWith("en") && femaleNames.some(n => v.name.toLowerCase().includes(n)))
    || voices.find(v => v.lang === "en-IN")
    || voices.find(v => v.lang.startsWith("en"))
    || null;
}

function cleanForSpeech(text) {
  return text
    .replace(/https?:\/\/[^\s]+/g, "")
    .replace(/[\r\n]+/g, ". ")
    .replace(/[*_~`#[\]]/g, "")
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
  const sentences = cleaned.match(/[^.!?।]+[.!?।]*/g) || [cleaned];
  const chunks = [];
  let current = "";
  for (const sentence of sentences) {
    if ((current + sentence).length > 220) {
      if (current.trim()) chunks.push(current.trim());
      current = sentence;
    } else current += " " + sentence;
  }
  if (current.trim()) chunks.push(current.trim());
  let index = 0;
  isSpeaking = true;
  micBtn.classList.add("speaking");
  showSpeakerAnim(true);
  setVoiceText("AI is speaking full answer", cleaned.slice(0, 120) + (cleaned.length > 120 ? "..." : ""));

  function speakNext() {
    if (index >= chunks.length) {
      isSpeaking = false;
      micBtn.classList.remove("speaking");
      showSpeakerAnim(false);
      setVoiceText("Tap the Jarvis mic and speak", "No message box. Voice only.");
      return;
    }
    const chunk = chunks[index++];
    const chunkIsTe = isTeluguText(chunk);
    const utter = new SpeechSynthesisUtterance(chunk);
    utter.lang = chunkIsTe ? "te-IN" : "en-IN";
    utter.rate = chunkIsTe ? 0.82 : 0.86;
    utter.pitch = 1.14;
    utter.volume = 1.0;
    const voice = getBestVoice(chunkIsTe);
    if (voice) utter.voice = voice;
    utter.onend = speakNext;
    utter.onerror = () => {
      isSpeaking = false;
      micBtn.classList.remove("speaking");
      showSpeakerAnim(false);
      setVoiceText("Tap the Jarvis mic and speak", "Voice stopped");
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

if (stopSpeakBtn) stopSpeakBtn.addEventListener("click", stopSpeaking);

function showSpeakerAnim(show) {
  if (speakerAnim) speakerAnim.style.display = show ? "block" : "none";
}

function addMessage(role, content) {
  if (welcomeEl) welcomeEl.style.display = "none";
  const div = document.createElement("div");
  div.className = `message ${role}`;
  div.innerHTML = `<div class="msg-wrapper"><div class="bubble">${escapeHtml(content)}</div></div>`;
  messagesEl.appendChild(div);
  messagesEl.scrollTop = messagesEl.scrollHeight;
}

function showToast(msg, duration = 2200) {
  if (!toastEl) return;
  toastEl.textContent = msg;
  toastEl.style.display = "block";
  setTimeout(() => { toastEl.style.display = "none"; }, duration);
}

function escapeHtml(str) {
  if (!str) return "";
  return String(str).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
}

function showTyping() {
  typingIndicator.style.display = "flex";
  messagesEl.scrollTop = messagesEl.scrollHeight;
}

function hideTyping() {
  typingIndicator.style.display = "none";
}

function fallbackReplyForCurrentLanguage(msg) {
  return isTeluguText(msg) ? "సంబంధం సమస్య వచ్చింది. దయచేసి మళ్లీ ప్రయత్నించండి." : "Connection error. Please try again.";
}

async function sendMessage(msg) {
  if (!msg) return;
  stopSpeaking();
  setVoiceText("Processing your question", msg);
  addMessage("user", msg);
  conversationHistory.push({ role: "user", content: msg });
  showTyping();
  try {
    const res = await fetch(`${API_BASE}/api/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: msg, conversationHistory: conversationHistory.slice(-12) })
    });
    const data = await res.json();
    hideTyping();
    const reply = data.reply || (isTeluguText(msg) ? "సమాధానం రాలేదు. మళ్లీ ప్రయత్నించండి." : "I did not get a response. Please try again.");
    addMessage("assistant", reply);
    conversationHistory.push({ role: "assistant", content: reply });
    setTimeout(() => speak(reply), 150);
  } catch {
    hideTyping();
    const reply = fallbackReplyForCurrentLanguage(msg);
    addMessage("assistant", reply);
    speak(reply);
  }
}

document.querySelectorAll(".suggestion-btn").forEach(btn => {
  btn.addEventListener("click", () => sendMessage(btn.textContent.trim()));
});
