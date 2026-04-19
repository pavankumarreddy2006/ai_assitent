"use strict";

const API_BASE = "/assistant-api";
const DEFAULT_ENGLISH = "en-IN";
const DEFAULT_TELUGU = "te-IN";
const WAKE_WORDS = [
  "hello ideal college ai",
  "hello ideal ai",
  "ideal college ai",
  "hi ideal college ai",
  "jarvis",
  "hello jarvis",
  "hi jarvis",
  "\u0c39\u0c32\u0c4b \u0c10\u0c21\u0c3f\u0c2f\u0c32\u0c4d \u0c15\u0c3e\u0c32\u0c47\u0c1c\u0c4d \u0c0f\u0c10",
  "\u0c10\u0c21\u0c3f\u0c2f\u0c32\u0c4d \u0c15\u0c3e\u0c32\u0c47\u0c1c\u0c4d \u0c0f\u0c10"
];
const IMAGE_HIDE_MS = 6000;
const VIDEO_HIDE_MS = 18000;

let recognition = null;
let voices = [];
let isListening = false;
let isSpeaking = false;
let isRequestInFlight = false;
let wakeWordDetected = false;
let pendingCommandTimeout = null;
let mediaBlockingWake = false;
let mediaTimer = null;
let lastDetectedLanguage = "en";
let selectedRecognitionLang = DEFAULT_ENGLISH;

let messagesEl;
let welcomeEl;
let micBtn;
let typingIndicator;
let statusDot;
let sysStatusEl;
let infoPanel;
let infoToggle;
let infoClose;
let infoContent;
let newsContent;
let speakerAnim;
let stopSpeakBtn;
let toastEl;
let voiceStatus;
let voiceTranscript;
let mediaOverlay;
let mediaContent;
let mediaCloseBtn;
let langDisplay;

const conversationHistory = [];

function initializeDomReferencesAndHandlers() {
  messagesEl = document.getElementById("messages");
  welcomeEl = document.getElementById("welcome");
  micBtn = document.getElementById("micBtn");
  typingIndicator = document.getElementById("typingIndicator");
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
  langDisplay = document.getElementById("langDisplay");

  setupSpeechRecognition();
  loadVoices();
  updateLanguagePill("en");
  checkHealth();
  loadCollegeInfo();
  loadNews();

  if (window.speechSynthesis) {
    window.speechSynthesis.onvoiceschanged = loadVoices;
  }

  if (infoToggle && infoPanel) {
    infoToggle.addEventListener("click", () => infoPanel.classList.add("open"));
  }
  if (infoClose && infoPanel) {
    infoClose.addEventListener("click", () => infoPanel.classList.remove("open"));
  }
  if (stopSpeakBtn) {
    stopSpeakBtn.addEventListener("click", stopSpeaking);
  }
  if (micBtn) {
    micBtn.addEventListener("click", handleMicClick);
    micBtn.setAttribute("aria-label", "Tap microphone to talk to Ideal College AI");
  }
  if (mediaOverlay) {
    mediaOverlay.addEventListener("click", (event) => {
      if (event.target === mediaOverlay) {
        closeMediaOverlay();
      }
    });
  }
  if (mediaCloseBtn) {
    mediaCloseBtn.addEventListener("click", (event) => {
      event.stopPropagation();
      closeMediaOverlay();
    });
  }

  document.querySelectorAll(".suggestion-btn").forEach((button) => {
    button.addEventListener("click", () => sendMessage(button.textContent.trim()));
  });

  setInterval(checkHealth, 30000);
  setInterval(loadNews, 300000);

  if (!recognition) {
    setVoiceText("Voice not supported", "Open this in Chrome or Edge to use speech.");
    return;
  }

  setVoiceText("Wake mode active", 'Say "Hello Ideal College AI"');
  startListening();
}

function setupSpeechRecognition() {
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (!SpeechRecognition) {
    recognition = null;
    return;
  }

  recognition = new SpeechRecognition();
  recognition.lang = selectedRecognitionLang;
  recognition.continuous = true;
  recognition.interimResults = true;
  recognition.maxAlternatives = 1;

  recognition.onstart = () => {
    isListening = true;
    if (micBtn) {
      micBtn.classList.add("listening");
    }
  };

  recognition.onresult = (event) => {
    let interimTranscript = "";
    for (let index = event.resultIndex; index < event.results.length; index += 1) {
      const transcript = normalizeSpeechText(event.results[index][0].transcript);
      if (!transcript) {
        continue;
      }
      if (event.results[index].isFinal) {
        handleRecognizedText(transcript);
      } else {
        interimTranscript += ` ${transcript}`;
      }
    }

    const interim = interimTranscript.trim();
    if (!wakeWordDetected && containsWakeWord(interim)) {
      wakeWordDetected = true;
      setVoiceText("Listening", getPromptByLanguage(lastDetectedLanguage));
      resetPendingCommandWindow();
      showToast(lastDetectedLanguage === "te" ? "\u0c28\u0c47\u0c28\u0c41 \u0c35\u0c3f\u0c28\u0c41\u0c24\u0c41\u0c28\u0c4d\u0c28\u0c3e\u0c28\u0c41." : "I'm listening.");
    }
  };

  recognition.onerror = (event) => {
    isListening = false;
    if (micBtn) {
      micBtn.classList.remove("listening");
    }
    if (event.error === "not-allowed") {
      setVoiceText("Mic blocked", "Allow microphone access and try again.");
      showToast("Microphone permission is required.");
      return;
    }
    if (event.error !== "aborted") {
      setVoiceText("Voice issue", "Trying to listen again...");
    }
  };

  recognition.onend = () => {
    isListening = false;
    if (micBtn) {
      micBtn.classList.remove("listening");
    }
    if (!isSpeaking && !mediaBlockingWake) {
      window.setTimeout(() => startListening(), 350);
    }
  };
}

function normalizeSpeechText(text) {
  return String(text || "").trim().replace(/\s+/g, " ").toLowerCase();
}

function containsWakeWord(text) {
  const normalized = normalizeSpeechText(text);
  return WAKE_WORDS.some((phrase) => normalized.includes(phrase));
}

function stripWakeWord(text) {
  const normalized = normalizeSpeechText(text);
  const matchedPhrase = WAKE_WORDS.find((phrase) => normalized.startsWith(phrase));
  if (!matchedPhrase) {
    return normalized;
  }
  return normalized.slice(matchedPhrase.length).trim();
}

function detectSpokenLanguage(text) {
  if (/[\u0C00-\u0C7F]/.test(text)) {
    return "te";
  }

  const normalized = normalizeSpeechText(text);
  const romanTeluguWords = [
    "nenu", "meeru", "cheppu", "cheppandi", "enti", "emiti", "ela", "ekkada",
    "telugu", "varthalu", "vartalu", "vathavaranam", "vaatavaranam", "chupinchu",
    "aadinchu", "video", "photo", "college", "kavali", "undi", "unnayi"
  ];
  const englishWords = [
    "what", "when", "where", "who", "how", "play", "show", "tell", "course",
    "courses", "admission", "college", "weather", "news", "video", "image"
  ];

  const words = normalized.split(/\s+/).filter(Boolean);
  const teluguHits = words.filter((word) => romanTeluguWords.includes(word)).length;
  const englishHits = words.filter((word) => englishWords.includes(word)).length;

  if (teluguHits >= 2 && teluguHits >= englishHits) {
    return "te";
  }
  return "en";
}

function applyRecognitionLanguage(language) {
  const targetLang = language === "te" ? DEFAULT_TELUGU : DEFAULT_ENGLISH;
  if (selectedRecognitionLang === targetLang) {
    return;
  }

  selectedRecognitionLang = targetLang;
  if (recognition) {
    recognition.lang = targetLang;
    if (isListening) {
      recognition.stop();
    }
  }
}

function updateLanguagePill(language) {
  if (!langDisplay) {
    return;
  }
  langDisplay.textContent = language === "te" ? "TELUGU LIVE" : "ENGLISH LIVE";
}

function getPromptByLanguage(language) {
  return language === "te" ? "\u0c2e\u0c40 \u0c2a\u0c4d\u0c30\u0c36\u0c4d\u0c28 \u0c1a\u0c46\u0c2a\u0c4d\u0c2a\u0c02\u0c21\u0c3f." : "Please say your question.";
}

function handleRecognizedText(text) {
  if (!text) {
    return;
  }

  const language = detectSpokenLanguage(text);
  lastDetectedLanguage = language;
  updateLanguagePill(language);

  if (!wakeWordDetected) {
    if (containsWakeWord(text)) {
      wakeWordDetected = true;
      const directCommand = stripWakeWord(text);
      if (directCommand) {
        clearPendingCommandWindow();
        setVoiceText(language === "te" ? "\u0c2a\u0c4d\u0c30\u0c3e\u0c38\u0c46\u0c38\u0c4d \u0c1a\u0c47\u0c38\u0c4d\u0c24\u0c41\u0c28\u0c4d\u0c28\u0c3e\u0c28\u0c41" : "Processing", directCommand);
        sendMessage(directCommand, language);
      } else {
        setVoiceText("Listening", getPromptByLanguage(language));
        resetPendingCommandWindow();
      }
    }
    return;
  }

  wakeWordDetected = false;
  clearPendingCommandWindow();
  setVoiceText(language === "te" ? "\u0c2a\u0c4d\u0c30\u0c3e\u0c38\u0c46\u0c38\u0c4d \u0c1a\u0c47\u0c38\u0c4d\u0c24\u0c41\u0c28\u0c4d\u0c28\u0c3e\u0c28\u0c41" : "Processing", text);
  sendMessage(text, language);
}

function resetPendingCommandWindow() {
  clearPendingCommandWindow();
  pendingCommandTimeout = window.setTimeout(() => {
    wakeWordDetected = false;
    setVoiceText("Wake mode active", 'Say "Hello Ideal College AI"');
  }, 10000);
}

function clearPendingCommandWindow() {
  if (pendingCommandTimeout) {
    window.clearTimeout(pendingCommandTimeout);
    pendingCommandTimeout = null;
  }
}

function setVoiceText(status, transcript) {
  if (voiceStatus) {
    voiceStatus.textContent = status || "";
  }
  if (voiceTranscript) {
    voiceTranscript.textContent = transcript || "";
  }
}

function startListening() {
  if (!recognition || isListening || isSpeaking || mediaBlockingWake || isRequestInFlight) {
    return;
  }
  try {
    recognition.lang = selectedRecognitionLang;
    recognition.start();
  } catch (error) {
    window.setTimeout(() => startListening(), 500);
  }
}

function handleMicClick() {
  if (!recognition) {
    showToast("Voice is not supported in this browser.");
    return;
  }

  if (isSpeaking) {
    stopSpeaking();
    return;
  }

  if (isListening) {
    recognition.stop();
    setVoiceText("Mic paused", "Tap again to continue.");
    return;
  }

  wakeWordDetected = true;
  setVoiceText("Listening", getPromptByLanguage(lastDetectedLanguage));
  startListening();
}

function loadVoices() {
  voices = window.speechSynthesis ? window.speechSynthesis.getVoices() : [];
}

function getBestVoice(language) {
  if (!voices.length) {
    return null;
  }

  if (language === "te") {
    return voices.find((voice) => /^te(-|$)/i.test(voice.lang))
      || voices.find((voice) => /telugu/i.test(voice.name))
      || voices.find((voice) => /^hi(-|$)/i.test(voice.lang))
      || voices[0];
  }

  return voices.find((voice) => /^en-in$/i.test(voice.lang))
    || voices.find((voice) => /^en(-|$)/i.test(voice.lang))
    || voices[0];
}

function speak(text, language) {
  if (!window.speechSynthesis || !text) {
    startListening();
    return;
  }

  const resolvedLanguage = language || detectSpokenLanguage(text);
  lastDetectedLanguage = resolvedLanguage;
  updateLanguagePill(resolvedLanguage);

  window.speechSynthesis.cancel();
  isSpeaking = true;
  showSpeakerAnim(true);

  const utterance = new SpeechSynthesisUtterance(text);
  utterance.voice = getBestVoice(resolvedLanguage);
  utterance.lang = resolvedLanguage === "te" ? DEFAULT_TELUGU : DEFAULT_ENGLISH;
  utterance.rate = resolvedLanguage === "te" ? 0.82 : 0.96;
  utterance.pitch = resolvedLanguage === "te" ? 0.95 : 1;
  utterance.volume = 1;

  utterance.onend = () => {
    isSpeaking = false;
    showSpeakerAnim(false);
    applyRecognitionLanguage(resolvedLanguage);
    startListening();
  };

  utterance.onerror = () => {
    isSpeaking = false;
    showSpeakerAnim(false);
    applyRecognitionLanguage(resolvedLanguage);
    startListening();
  };

  window.speechSynthesis.speak(utterance);
}

function stopSpeaking() {
  if (window.speechSynthesis) {
    window.speechSynthesis.cancel();
  }
  isSpeaking = false;
  showSpeakerAnim(false);
  startListening();
}

function showSpeakerAnim(show) {
  if (speakerAnim) {
    speakerAnim.style.display = show ? "flex" : "none";
  }
  if (micBtn) {
    micBtn.classList.toggle("speaking", Boolean(show));
  }
}

function addMessage(role, content) {
  if (welcomeEl) {
    welcomeEl.style.display = "none";
  }
  if (!messagesEl) {
    return;
  }

  const container = document.createElement("div");
  container.className = `message ${role}`;
  container.innerHTML = `<div class="msg-wrapper"><div class="bubble">${escapeHtml(content)}</div></div>`;
  messagesEl.appendChild(container);
  messagesEl.scrollTop = messagesEl.scrollHeight;
}

function escapeHtml(text) {
  const node = document.createElement("div");
  node.textContent = text == null ? "" : String(text);
  return node.innerHTML;
}

function escapeAttribute(text) {
  return escapeHtml(text).replace(/"/g, "&quot;");
}

function showTyping() {
  if (typingIndicator) {
    typingIndicator.style.display = "flex";
  }
}

function hideTyping() {
  if (typingIndicator) {
    typingIndicator.style.display = "none";
  }
}

function showToast(message) {
  if (!toastEl) {
    return;
  }
  toastEl.textContent = message;
  toastEl.classList.add("visible");
  window.setTimeout(() => toastEl.classList.remove("visible"), 2500);
}

async function checkHealth() {
  try {
    const response = await fetch(`${API_BASE}/healthz`, { cache: "no-store" });
    const data = await response.json();
    if (statusDot) {
      statusDot.classList.toggle("active", data.status === "ok");
    }
    if (sysStatusEl) {
      sysStatusEl.textContent = "";
    }
  } catch (error) {
    if (statusDot) {
      statusDot.classList.remove("active");
    }
    if (sysStatusEl) {
      sysStatusEl.textContent = "Server offline";
    }
  }
}

async function loadCollegeInfo() {
  if (!infoContent) {
    return;
  }
  try {
    const response = await fetch(`${API_BASE}/college-info`, { cache: "no-store" });
    const data = await response.json();
    infoContent.innerHTML = `
      <div class="info-section">
        <div class="info-label">Assistant</div>
        <p class="ai-copy">Ideal College AI speaks with students in English and Telugu.</p>
      </div>
      <div class="info-section">
        <div class="info-label">Contact</div>
        <div class="contact-row">${escapeHtml(data.contact || "0884-2384382")}</div>
        <div class="contact-row">${escapeHtml(data.email || "idealcolleges@gmail.com")}</div>
        <div class="contact-row"><a class="info-link" href="${escapeAttribute(data.website || "https://idealcollege.edu.in")}" target="_blank" rel="noreferrer">${escapeHtml(data.website || "idealcollege.edu.in")}</a></div>
      </div>
    `;
  } catch (error) {
    infoContent.innerHTML = `<p class="info-loading">Information is temporarily unavailable.</p>`;
  }
}

async function loadNews() {
  if (!newsContent) {
    return;
  }
  try {
    const response = await fetch(`${API_BASE}/news`, { cache: "no-store" });
    const data = await response.json();
    if (!data.articles || !data.articles.length) {
      newsContent.innerHTML = `<p class="info-loading">No recent news right now.</p>`;
      return;
    }
    newsContent.innerHTML = data.articles.slice(0, 4).map((article) => `
      <div class="news-item" data-url="${escapeAttribute(article.url)}">
        <div class="news-title">${escapeHtml(article.title)}</div>
        <div class="news-source">${escapeHtml(article.source)}</div>
      </div>
    `).join("");

    newsContent.querySelectorAll(".news-item").forEach((item) => {
      item.addEventListener("click", () => {
        const url = item.getAttribute("data-url");
        if (url) {
          window.open(url, "_blank", "noopener");
        }
      });
    });
  } catch (error) {
    newsContent.innerHTML = `<p class="info-loading">News feed unavailable.</p>`;
  }
}

async function sendMessage(message, languageHint) {
  const content = String(message || "").trim();
  if (!content || isRequestInFlight) {
    return;
  }

  const requestedLanguage = languageHint || detectSpokenLanguage(content);
  lastDetectedLanguage = requestedLanguage;
  updateLanguagePill(requestedLanguage);
  applyRecognitionLanguage(requestedLanguage);

  isRequestInFlight = true;
  stopSpeaking();
  addMessage("user", content);
  conversationHistory.push({ role: "user", content });
  showTyping();

  try {
    const response = await fetch(`${API_BASE}/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        message: content,
        conversationHistory: conversationHistory.slice(-10)
      })
    });
    const data = await response.json();
    hideTyping();

    if (!response.ok) {
      throw new Error(data.error || "Server error");
    }

    const reply = data.reply || (requestedLanguage === "te"
      ? "\u0c15\u0c4d\u0c37\u0c2e\u0c3f\u0c02\u0c1a\u0c02\u0c21\u0c3f, \u0c28\u0c47\u0c28\u0c41 \u0c38\u0c2e\u0c3e\u0c27\u0c3e\u0c28\u0c02 \u0c38\u0c3f\u0c26\u0c4d\u0c27\u0c02 \u0c1a\u0c47\u0c2f\u0c32\u0c47\u0c15\u0c2a\u0c4b\u0c2f\u0c3e\u0c28\u0c41."
      : "Sorry, I could not prepare a reply.");
    const replyLanguage = data.language || requestedLanguage;

    addMessage("assistant", reply);
    conversationHistory.push({ role: "assistant", content: reply });

    if (data.show_images) {
      showImagesOverlay(data.images, data.media_duration);
    } else if (data.show_video) {
      showVideoOverlay(data.video_url, data.media_duration);
    } else {
      closeMediaOverlay(true);
    }

    speak(reply, replyLanguage);
  } catch (error) {
    hideTyping();
    const fallback = requestedLanguage === "te"
      ? "\u0c15\u0c4d\u0c37\u0c2e\u0c3f\u0c02\u0c1a\u0c02\u0c21\u0c3f, server \u0c24\u0c4b connection problem \u0c35\u0c1a\u0c4d\u0c1a\u0c3f\u0c02\u0c26\u0c3f."
      : "Sorry, I am having trouble connecting to the server.";
    addMessage("assistant", fallback);
    speak(fallback, requestedLanguage);
  } finally {
    isRequestInFlight = false;
  }
}

function clearMediaTimer() {
  if (mediaTimer) {
    window.clearTimeout(mediaTimer);
    mediaTimer = null;
  }
}

function showImagesOverlay(images, durationSeconds) {
  if (!mediaOverlay || !mediaContent || !Array.isArray(images) || !images.length) {
    return;
  }
  clearMediaTimer();
  mediaBlockingWake = true;
  mediaOverlay.classList.remove("hidden");
  mediaOverlay.setAttribute("aria-hidden", "false");
  mediaContent.innerHTML = `<img src="${escapeAttribute(images[0])}" class="media-image" alt="Campus view">`;
  mediaTimer = window.setTimeout(closeMediaOverlay, Math.max(1000, (durationSeconds || 0) * 1000 || IMAGE_HIDE_MS));
}

function showVideoOverlay(url, durationSeconds) {
  if (!mediaOverlay || !mediaContent || !url) {
    return;
  }
  clearMediaTimer();
  mediaBlockingWake = true;
  mediaOverlay.classList.remove("hidden");
  mediaOverlay.setAttribute("aria-hidden", "false");
  mediaContent.innerHTML = `<video src="${escapeAttribute(url)}" class="media-video" controls autoplay playsinline></video>`;

  const video = mediaContent.querySelector("video");
  if (video) {
    video.addEventListener("ended", closeMediaOverlay, { once: true });
  }

  mediaTimer = window.setTimeout(closeMediaOverlay, Math.max(3000, (durationSeconds || 0) * 1000 || VIDEO_HIDE_MS));
}

function closeMediaOverlay(silent) {
  clearMediaTimer();
  if (mediaOverlay) {
    mediaOverlay.classList.add("hidden");
    mediaOverlay.setAttribute("aria-hidden", "true");
  }
  if (mediaContent) {
    mediaContent.innerHTML = "";
  }
  mediaBlockingWake = false;
  if (!silent) {
    startListening();
  }
}

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", initializeDomReferencesAndHandlers);
} else {
  initializeDomReferencesAndHandlers();
}
