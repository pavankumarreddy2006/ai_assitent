"use strict";

let conversationHistory = [];
let isListening = false;
let isSpeaking = false;
let recognition = null;
let voices = [];
let finalTranscript = "";
let sliderInterval = null;
let isRequestInFlight = false;
let continuousMode = false;
let wakeWordDetected = false;
let pendingCommandTimeout = null;
let mediaBlockingWake = false;
let selectedLang = "en-IN"; // Default language

const WAKE_WORDS = ["hello ideal ai", "hello idol ai", "hello ideal a i", "హలో ఐడియల్ ఏఐ"];

const API_BASE = "/assistant-api";

// DOM References
let messagesEl = null;
let welcomeEl = null;
let micBtn = null;
let typingIndicator = null;
let greetingEl = null;
let statusDot = null;
let sysStatusEl = null;
let infoPanel = null;
let infoToggle = null;
let infoClose = null;
let infoContent = null;
let newsContent = null;
let speakerAnim = null;
let stopSpeakBtn = null;
let toastEl = null;
let voiceStatus = null;
let voiceTranscript = null;
let mediaOverlay = null;
let mediaContent = null;
let mediaCloseBtn = null;
let vizBars = null;

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

function setVizActive(on) {
  if (vizBars) vizBars.classList.toggle("active", Boolean(on));
}

function initializeDomReferencesAndHandlers() {
  messagesEl = document.getElementById("messages");
  welcomeEl = document.getElementById("welcome");
  micBtn = document.getElementById("micBtn");
  typingIndicator = document.getElementById("typingIndicator");
  greetingEl = document.getElementById("greeting");
  statusDot = document.getElementById("statusDot");
  sysStatusEl = document.getElementById("sysStatus");
  infoPanel = document.getElementById("infoPanel");
  infoToggle = document.getElementById("infoToggle");
  infoClose = document.getElementById("infoClose");
  infoContent = document.getElementById("infoContent");
  newsContent = document.getElementById("newsContent");
  speakerAnim = document.getElementById("speakerAnim");
  stopSpeakBtn = document.getElementById("stopSpeakBtn");
  toastEl = document.getElementById("toast");
  voiceStatus = document.getElementById("voiceStatus");
  voiceTranscript = document.getElementById("voiceTranscript");
  mediaOverlay = document.getElementById("mediaOverlay");
  mediaContent = document.getElementById("mediaContent");
  mediaCloseBtn = document.getElementById("mediaCloseBtn");
  vizBars = document.getElementById("vizBars");

  updateGreeting();
  setInterval(updateGreeting, 60000);
  checkHealth();
  setInterval(checkHealth, 30000);
  loadCollegeInfo();
  loadNews();
  setupSpeechRecognition();
  loadVoices();

  if (window.speechSynthesis) {
    window.speechSynthesis.onvoiceschanged = loadVoices;
  }

  if (infoToggle) infoToggle.addEventListener("click", () => infoPanel && infoPanel.classList.add("open"));
  if (infoClose) infoClose.addEventListener("click", () => infoPanel && infoPanel.classList.remove("open"));
  if (stopSpeakBtn) stopSpeakBtn.addEventListener("click", stopSpeaking);

  if (micBtn) {
    micBtn.addEventListener("click", handleMicClick);
    micBtn.setAttribute("aria-label", "Microphone — tap to toggle listening");
  }

  if (mediaOverlay) {
    mediaOverlay.addEventListener("click", (e) => {
      if (e.target === mediaOverlay) closeMediaOverlay();
    });
  }
  if (mediaCloseBtn) mediaCloseBtn.addEventListener("click", (e) => {
    e.stopPropagation();
    closeMediaOverlay();
  });

  document.querySelectorAll(".suggestion-btn").forEach((btn) => {
    btn.addEventListener("click", () => sendMessage(btn.textContent.trim()));
  });

  if (!recognition) {
    setVoiceText("Voice not supported", "Please use a modern browser like Chrome or Edge.");
  } else {
    setVoiceText("Wake mode active", "Say \"Hello Ideal AI\" to start.");
    startListening(); 
  }
}

function handleMicClick() {
  if (isSpeaking) {
    stopSpeaking();
    return;
  }

  if (!recognition) {
    showToast("Voice is not supported in this browser");
    return;
  }

  if (isListening) {
    recognition.stop();
    setVoiceText("Mic toggled OFF", "Tap to start listening again.");
  } else {
    wakeWordDetected = true; // Manual trigger treats it as if wake word was said
    startListening();
    setVoiceText("Mic toggled ON", "How can I help you?");
  }
}

async function checkHealth() {
  try {
    const res = await fetch(`${API_BASE}/healthz`, { cache: "no-store" });
    const data = await res.json();
    if (statusDot) statusDot.classList.toggle("active", data.status === "ok");
    if (sysStatusEl) sysStatusEl.textContent = "";
  } catch {
    if (statusDot) statusDot.classList.remove("active");
    if (sysStatusEl) sysStatusEl.textContent = "Server connection lost";
  }
}

async function loadCollegeInfo() {
  if (!infoContent) return;
  try {
    const res = await fetch(`${API_BASE}/college-info`, { cache: "no-store" });
    const data = await res.json();
    infoContent.innerHTML = `
      <div class="info-section">
        <div class="info-label">Assistant Status</div>
        <p class="ai-copy">Official Voice AI for Ideal College of Arts & Sciences. Available in English & Telugu.</p>
      </div>
      <div class="info-section">
        <div class="info-label">Contact Details</div>
        <div class="contact-row">📞 ${escapeHtml(data.contact || "0884-2384382")}</div>
        <div class="contact-row">📧 ${escapeHtml(data.email || "idealcolleges@gmail.com")}</div>
        <div class="contact-row">🌐 <a class="info-link" href="${escapeAttribute(data.website || "https://idealcollege.edu.in")}" target="_blank">${escapeHtml(data.website || "idealcollege.edu.in")}</a></div>
      </div>`;
  } catch {
    infoContent.innerHTML = `<p class="info-loading">Information offline</p>`;
  }
}

async function loadNews() {
  if (!newsContent) return;
  try {
    const res = await fetch(`${API_BASE}/news`, { cache: "no-store" });
    const { articles } = await res.json();
    if (!articles?.length) {
      newsContent.innerHTML = `<p class="info-loading">No recent news</p>`;
      return;
    }
    newsContent.innerHTML = articles.slice(0, 4).map(a => `
      <div class="news-item" onclick="window.open('${escapeAttribute(a.url)}', '_blank')">
        <div class="news-title">${escapeHtml(a.title)}</div>
        <div class="news-source">${escapeHtml(a.source)}</div>
      </div>
    `).join("");
  } catch {
    newsContent.innerHTML = `<p class="info-loading">News feed unavailable</p>`;
  }
}

function setupSpeechRecognition() {
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (!SpeechRecognition) return;

  recognition = new SpeechRecognition();
  recognition.lang = selectedLang;
  recognition.continuous = true;
  recognition.interimResults = true; // Use interim for faster wake word detection

  recognition.onstart = () => {
    isListening = true;
    if (micBtn) micBtn.classList.add("listening");
    setVizActive(true);
  };

  recognition.onresult = (event) => {
    let interimTranscript = "";
    for (let i = event.resultIndex; i < event.results.length; i++) {
        const transcriptChunk = event.results[i][0].transcript.toLowerCase();
        if (event.results[i].isFinal) {
            finalTranscript = transcriptChunk.trim();
            handleTranscript(finalTranscript);
        } else {
            interimTranscript += transcriptChunk;
        }
    }
    
    // Check for wake word in interim if not already detected
    if (!wakeWordDetected && containsWakeWord(interimTranscript)) {
        wakeWordDetected = true;
        setVoiceText("Listening...", "How can I help you?");
        showToast("Hello! I'm listening.");
        resetPendingCommandWindow();
    }
  };

  recognition.onerror = (event) => {
    console.error("Speech recognition error:", event.error);
    isListening = false;
    if (micBtn) micBtn.classList.remove("listening");
    setVizActive(false);
    
    if (event.error === "not-allowed") {
        showToast("Microphone access denied.");
        setVoiceText("Mic Error", "Please allow mic access.");
    }
  };

  recognition.onend = () => {
    isListening = false;
    if (micBtn) micBtn.classList.remove("listening");
    setVizActive(false);
    // Auto-restart unless speaking or media is playing
    if (!isSpeaking && !mediaBlockingWake) {
        setTimeout(startListening, 500);
    }
  };
}

function startListening() {
    if (!recognition || isListening || isSpeaking || mediaBlockingWake) return;
    try {
        recognition.start();
    } catch (e) {
        console.warn("Recognition start failed, retrying...", e);
        setTimeout(startListening, 1000);
    }
}

function handleTranscript(text) {
    if (!text) return;

    if (!wakeWordDetected) {
        if (containsWakeWord(text)) {
            wakeWordDetected = true;
            setVoiceText("Listening...", "Say your question.");
            resetPendingCommandWindow();
        }
        return;
    }

    // Process question
    wakeWordDetected = false;
    clearPendingCommandWindow();
    setVoiceText("Processing", text);
    sendMessage(text);
}

function containsWakeWord(text) {
  const normalized = (text || "").toLowerCase();
  return WAKE_WORDS.some((phrase) => normalized.includes(phrase));
}

function clearPendingCommandWindow() {
  if (pendingCommandTimeout) {
    clearTimeout(pendingCommandTimeout);
    pendingCommandTimeout = null;
  }
}

function resetPendingCommandWindow() {
  clearPendingCommandWindow();
  pendingCommandTimeout = setTimeout(() => {
    wakeWordDetected = false;
    setVoiceText("Wake mode active", "Say \"Hello Ideal AI\"");
  }, 10000);
}

function setVoiceText(status, transcript) {
  if (voiceStatus) voiceStatus.textContent = status || "";
  if (voiceTranscript) voiceTranscript.textContent = transcript || "";
}

function loadVoices() {
  voices = window.speechSynthesis ? window.speechSynthesis.getVoices() : [];
}

function isTeluguText(text) {
  return /[\u0C00-\u0C7F]/.test(text || "");
}

function getBestVoice(isTelugu) {
  if (!voices.length) return null;
  if (isTelugu) {
    return voices.find(v => v.lang.startsWith("te")) || voices.find(v => v.lang.startsWith("hi")) || voices[0];
  }
  return voices.find(v => v.name.includes("Google") && v.lang.startsWith("en-IN")) ||
         voices.find(v => v.lang.startsWith("en")) || voices[0];
}

function speak(text) {
  if (!window.speechSynthesis || !text) return;

  window.speechSynthesis.cancel();
  isSpeaking = true;
  showSpeakerAnim(true);
  setVizActive(true);

  const isTe = isTeluguText(text);
  const utter = new SpeechSynthesisUtterance(text);
  utter.voice = getBestVoice(isTe);
  utter.rate = isTe ? 0.9 : 1.0;
  utter.pitch = 1.0;
  utter.lang = isTe ? "te-IN" : "en-IN";

  utter.onend = () => {
    isSpeaking = false;
    showSpeakerAnim(false);
    setVizActive(false);
    startListening();
  };

  utter.onerror = (e) => {
    console.error("Speech error", e);
    isSpeaking = false;
    showSpeakerAnim(false);
    setVizActive(false);
    startListening();
  };

  window.speechSynthesis.speak(utter);
}

function stopSpeaking() {
  if (window.speechSynthesis) window.speechSynthesis.cancel();
  isSpeaking = false;
  showSpeakerAnim(false);
  setVizActive(false);
  startListening();
}

function showSpeakerAnim(show) {
  if (speakerAnim) speakerAnim.style.display = show ? "block" : "none";
}

function addMessage(role, content) {
  if (welcomeEl) welcomeEl.style.display = "none";
  if (!messagesEl) return;

  const div = document.createElement("div");
  div.className = `message ${role}`;
  div.innerHTML = `<div class="msg-wrapper"><div class="bubble">${escapeHtml(content)}</div></div>`;
  
  messagesEl.appendChild(div);
  messagesEl.scrollTop = messagesEl.scrollHeight;
}

function showToast(msg) {
  if (!toastEl) return;
  toastEl.textContent = msg;
  toastEl.classList.add("visible");
  setTimeout(() => toastEl.classList.remove("visible"), 3000);
}

function escapeHtml(str) {
  const p = document.createElement('p');
  p.textContent = str;
  return p.innerHTML;
}

function escapeAttribute(str) {
  return escapeHtml(str).replace(/"/g, "&quot;");
}

function showTyping() {
  if (typingIndicator) typingIndicator.style.display = "flex";
  if (messagesEl) messagesEl.scrollTop = messagesEl.scrollHeight;
}

function hideTyping() {
  if (typingIndicator) typingIndicator.style.display = "none";
}

async function sendMessage(msg) {
  if (!msg || isRequestInFlight) return;
  isRequestInFlight = true;

  stopSpeaking();
  addMessage("user", msg);
  conversationHistory.push({ role: "user", content: msg });
  showTyping();

  try {
    const res = await fetch(`${API_BASE}/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ 
        message: msg, 
        conversationHistory: conversationHistory.slice(-10) 
      }),
    });

    const data = await res.json();
    hideTyping();

    if (!res.ok) throw new Error(data.error || "Server error");

    const reply = data.reply || "I couldn't process that.";
    addMessage("assistant", reply);
    conversationHistory.push({ role: "assistant", content: reply });

    if (data.show_images) showImagesOverlay(data.images);
    else if (data.show_video) showVideoOverlay(data.video_url);

    speak(reply);
  } catch (err) {
    hideTyping();
    const fallback = isTeluguText(msg) ? "క్షమించండి, సర్వర్ సమస్య వచ్చింది." : "Sorry, I'm having trouble connecting.";
    addMessage("assistant", fallback);
    speak(fallback);
  } finally {
    isRequestInFlight = false;
  }
}

function showImagesOverlay(images) {
    if (!mediaOverlay || !images?.length) return;
    mediaBlockingWake = true;
    mediaOverlay.classList.remove("hidden");
    mediaContent.innerHTML = `<img src="${images[0]}" class="media-image">`;
}

function showVideoOverlay(url) {
    if (!mediaOverlay || !url) return;
    mediaBlockingWake = true;
    mediaOverlay.classList.remove("hidden");
    mediaContent.innerHTML = `
      <video src="${url}" class="media-video" controls autoplay></video>
    `;
}

function closeMediaOverlay() {
    mediaOverlay.classList.add("hidden");
    mediaContent.innerHTML = "";
    mediaBlockingWake = false;
    startListening();
}

// Global start
if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", initializeDomReferencesAndHandlers);
} else {
  initializeDomReferencesAndHandlers();
}
