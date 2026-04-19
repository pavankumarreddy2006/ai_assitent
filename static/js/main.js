"use strict";

let conversationHistory = [];
let isListening = false;
let isSpeaking = false;
let recognition = null;
let voices = [];
let finalTranscript = "";
let sliderInterval = null;
let isRequestInFlight = false;
let continuousListeningEnabled = false;
let shouldKeepListening = false;
let wakeWordDetected = false;
let pendingCommandTimeout = null;
let mediaBlockingWake = false;
const WAKE_WORDS = ["hello ideal ai", "hello idol ai", "hello ideal a i"];

const API_BASE = "/assistant-api";
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

  if (window.speechSynthesis) window.speechSynthesis.onvoiceschanged = loadVoices;
  if (infoToggle) infoToggle.addEventListener("click", () => infoPanel && infoPanel.classList.add("open"));
  if (infoClose) infoClose.addEventListener("click", () => infoPanel && infoPanel.classList.remove("open"));
  if (stopSpeakBtn) stopSpeakBtn.addEventListener("click", stopSpeaking);
  if (micBtn) {
    micBtn.addEventListener("click", handleMicClick);
    micBtn.addEventListener("dblclick", (e) => {
      e.preventDefault();
      toggleContinuousListening();
    });
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
    setVoiceText("Voice not supported", "Use suggestion chips or a Chromium-based browser.");
  } else {
    setVoiceText("Wake mode active", "Say \"Hello Ideal AI\"");
    startWakeListening();
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

  try {
    if (isListening) {
      shouldKeepListening = false;
      recognition.stop();
    } else {
      stopSpeaking();
      shouldKeepListening = continuousListeningEnabled;
      recognition.start();
    }
  } catch {
    setListeningState(false);
    showToast("Voice could not start. Please try again.");
  }
}

function toggleContinuousListening() {
  continuousListeningEnabled = !continuousListeningEnabled;
  shouldKeepListening = continuousListeningEnabled;
  const status = continuousListeningEnabled ? "Continuous mode ON" : "Continuous mode OFF";
  setVoiceText(status, "Double-click the mic to toggle continuous listening.");
  showToast(continuousListeningEnabled ? "Continuous listening enabled" : "Continuous listening disabled");
}

async function checkHealth() {
  try {
    const res = await fetch(`${API_BASE}/healthz`, { cache: "no-store" });
    if (!res.ok) throw new Error("Health failed");
    const data = await res.json();

    if (statusDot && data.status === "ok") statusDot.classList.add("active");
    if (sysStatusEl && data.status === "ok") sysStatusEl.textContent = "";
  } catch {
    if (statusDot) statusDot.classList.remove("active");
    if (sysStatusEl) sysStatusEl.textContent = "Reconnecting to server…";
  }
}

async function loadCollegeInfo() {
  if (!infoContent) return;
  try {
    const res = await fetch(`${API_BASE}/college-info`, { cache: "no-store" });
    if (!res.ok) throw new Error("College info failed");
    const data = await res.json();

    infoContent.innerHTML = `
      <div class="info-section">
        <div class="info-label">About this assistant</div>
        <p class="ai-copy">Ideal AI answers college questions, weather, news, and general queries in English or Telugu — voice-first.</p>
      </div>
      <div class="info-section">
        <div class="info-label">Language</div>
        <div class="ai-rule">Telugu question → Telugu answer.</div>
        <div class="ai-rule">English question → English answer.</div>
      </div>
      <div class="info-section">
        <div class="info-label">Media</div>
        <div class="ai-rule">Ask for <strong>college photos</strong> or <strong>college video</strong> for an instant full-screen preview.</div>
      </div>
      <div class="info-section">
        <div class="info-label">Contact</div>
        <div class="contact-row">${escapeHtml(data.contact || "0884-2384382 / 0884-2384381")}</div>
        <div class="contact-row">${escapeHtml(data.email || "idealcolleges@gmail.com")}</div>
        <div class="contact-row"><a class="info-link" href="${escapeAttribute(data.website || "https://idealcollege.edu.in")}" target="_blank" rel="noopener noreferrer">${escapeHtml(data.website || "https://idealcollege.edu.in")}</a></div>
      </div>`;
  } catch {
    infoContent.innerHTML = `<p class="info-loading">Could not load campus desk.</p>`;
  }
}

async function loadNews() {
  if (!newsContent) return;
  try {
    const res = await fetch(`${API_BASE}/news?query=latest%20India%20education`, { cache: "no-store" });
    if (!res.ok) throw new Error("News failed");

    const { articles } = await res.json();

    if (!Array.isArray(articles) || articles.length === 0) {
      newsContent.innerHTML = `<p class="info-loading">No news available.</p>`;
      return;
    }

    newsContent.innerHTML = "";

    articles.slice(0, 5).forEach((article) => {
      const item = document.createElement("div");
      item.className = "news-item";

      const title = document.createElement("div");
      title.className = "news-title";
      title.textContent = article.title || "Untitled";

      const source = document.createElement("div");
      source.className = "news-source";
      source.textContent = article.source || "Unknown";

      item.appendChild(title);
      item.appendChild(source);

      if (article.url) {
        item.addEventListener("click", () => window.open(article.url, "_blank", "noopener,noreferrer"));
      }

      newsContent.appendChild(item);
    });
  } catch {
    newsContent.innerHTML = `<p class="info-loading">Could not fetch news.</p>`;
  }
}

function setupSpeechRecognition() {
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (!SpeechRecognition) return;

  recognition = new SpeechRecognition();
  recognition.lang = "en-IN";
  recognition.continuous = true;
  recognition.interimResults = false;
  recognition.maxAlternatives = 3;

  recognition.onstart = () => {
    setListeningState(true);
    setVizActive(true);
    setVoiceText("Listening", wakeWordDetected ? "Ask your question now." : "Say \"Hello Ideal AI\"");
  };

  recognition.onresult = (event) => {
    for (let i = event.resultIndex; i < event.results.length; i += 1) {
      if (!event.results[i].isFinal) continue;
      const transcript = (event.results[i][0].transcript || "").trim();
      if (!transcript) continue;

      if (!wakeWordDetected) {
        if (containsWakeWord(transcript)) {
          wakeWordDetected = true;
          resetPendingCommandWindow();
          setVoiceText("Wake word detected", "Listening for your question…");
        }
        continue;
      }

      wakeWordDetected = false;
      clearPendingCommandWindow();
      setVoiceText("Processing", transcript);
      sendMessage(transcript);
    }
  };

  recognition.onerror = (event) => {
    setListeningState(false);
    setVizActive(false);
    shouldKeepListening = false;

    if (event.error === "no-speech") {
      setVoiceText("No speech detected", "Tap the mic and try again");
    } else {
      setVoiceText("Voice error", "Please try again");
    }
  };

  recognition.onend = () => {
    setListeningState(false);
    setVizActive(false);
    if (mediaBlockingWake) return;
    if (!isSpeaking) startWakeListening();
  };
}

function containsWakeWord(text) {
  const normalized = (text || "").toLowerCase().replace(/[^\w\s]/g, " ").replace(/\s+/g, " ").trim();
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
  }, 8000);
}

function startWakeListening() {
  if (!recognition || isListening || isSpeaking || mediaBlockingWake) return;
  try {
    recognition.start();
  } catch {
    setTimeout(startWakeListening, 800);
  }
}

function stopWakeListening() {
  if (!recognition || !isListening) return;
  try {
    recognition.stop();
  } catch {
    /* ignore */
  }
}

function setVoiceText(status, transcript) {
  if (voiceStatus) voiceStatus.textContent = status || "";
  if (voiceTranscript) voiceTranscript.textContent = transcript || "";
}

function setListeningState(val) {
  isListening = val;
  if (micBtn) {
    micBtn.classList.toggle("listening", val);
    micBtn.classList.toggle("continuous", continuousListeningEnabled);
  }
  if (val && !isSpeaking) setVizActive(true);
  if (!val && !isSpeaking) setVizActive(false);
}

function loadVoices() {
  voices = window.speechSynthesis ? window.speechSynthesis.getVoices() : [];
}

function isTeluguText(text) {
  return /[\u0C00-\u0C7F]/.test(text || "");
}

function getBestVoice(isTeluguReply) {
  if (!voices.length) return null;

  const femaleNames = [
    "heera", "swara", "neural", "jenny", "aria", "zira", "samantha",
    "karen", "moira", "victoria", "female",
  ];

  if (isTeluguReply) {
    return (
      voices.find((v) => v.lang === "te-IN" && femaleNames.some((n) => v.name.toLowerCase().includes(n)))
      || voices.find((v) => v.lang && v.lang.startsWith("te"))
      || voices.find((v) => v.lang === "hi-IN" && femaleNames.some((n) => v.name.toLowerCase().includes(n)))
      || voices.find((v) => v.lang === "en-IN")
      || null
    );
  }

  return (
    voices.find((v) => v.lang === "en-IN" && femaleNames.some((n) => v.name.toLowerCase().includes(n)))
    || voices.find((v) => v.lang && v.lang.startsWith("en") && femaleNames.some((n) => v.name.toLowerCase().includes(n)))
    || voices.find((v) => v.lang && v.lang.startsWith("en"))
    || null
  );
}

function cleanForSpeech(text) {
  return String(text || "")
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

  stopWakeListening();
  if (window.speechSynthesis) window.speechSynthesis.cancel();

  const cleaned = cleanForSpeech(text);
  if (!cleaned) return;

  const sentences = cleaned.match(/[^.!?।]+[.!?।]*/g) || [cleaned];
  const chunks = [];
  let current = "";

  sentences.forEach((sentence) => {
    if ((current + sentence).length > 220) {
      if (current.trim()) chunks.push(current.trim());
      current = sentence;
    } else {
      current += ` ${sentence}`;
    }
  });

  if (current.trim()) chunks.push(current.trim());

  let index = 0;
  isSpeaking = true;

  if (micBtn) micBtn.classList.add("speaking");

  showSpeakerAnim(true);
  setVizActive(true);
  setVoiceText("Speaking", cleaned.slice(0, 140) + (cleaned.length > 140 ? "…" : ""));

  function speakNext() {
    if (index >= chunks.length) {
      finishSpeaking("Wake mode active", "Say \"Hello Ideal AI\"");
      return;
    }

    const chunk = chunks[index++];
    const chunkIsTe = isTeluguText(chunk);
    const utter = new SpeechSynthesisUtterance(chunk);

    utter.lang = chunkIsTe ? "te-IN" : "en-IN";
    utter.rate = chunkIsTe ? 0.82 : 0.88;
    utter.pitch = 1.12;
    utter.volume = 1.0;

    const voice = getBestVoice(chunkIsTe);
    if (voice) utter.voice = voice;

    utter.onend = speakNext;
    utter.onerror = () => finishSpeaking("Wake mode active", "Voice interrupted");

    window.speechSynthesis.speak(utter);
  }

  setTimeout(speakNext, 80);
}

function finishSpeaking(status, transcript) {
  isSpeaking = false;

  if (micBtn) micBtn.classList.remove("speaking");

  showSpeakerAnim(false);
  setVizActive(false);
  setVoiceText(status, transcript);
  if (!mediaBlockingWake) startWakeListening();
}

function stopSpeaking() {
  if (window.speechSynthesis) window.speechSynthesis.cancel();

  finishSpeaking("Wake mode active", "Say \"Hello Ideal AI\"");
}

function showSpeakerAnim(show) {
  if (speakerAnim) speakerAnim.style.display = show ? "block" : "none";
}

function addMessage(role, content) {
  if (welcomeEl) welcomeEl.style.display = "none";
  if (!messagesEl) return;

  const div = document.createElement("div");
  div.className = `message ${role}`;

  const wrapper = document.createElement("div");
  wrapper.className = "msg-wrapper";

  const bubble = document.createElement("div");
  bubble.className = "bubble";
  bubble.textContent = content || "";

  wrapper.appendChild(bubble);
  div.appendChild(wrapper);
  messagesEl.appendChild(div);

  messagesEl.scrollTop = messagesEl.scrollHeight;
}

function showToast(msg, duration = 2400) {
  if (!toastEl) return;

  toastEl.textContent = msg;
  toastEl.style.display = "block";

  setTimeout(() => {
    if (toastEl) toastEl.style.display = "none";
  }, duration);
}

function escapeHtml(str) {
  return String(str || "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

function escapeAttribute(str) {
  return escapeHtml(str).replace(/'/g, "&#39;");
}

function showTyping() {
  if (!typingIndicator || !messagesEl) return;

  typingIndicator.style.display = "flex";
  messagesEl.scrollTop = messagesEl.scrollHeight;
}

function hideTyping() {
  if (typingIndicator) typingIndicator.style.display = "none";
}

function fallbackReplyForCurrentLanguage(msg) {
  return isTeluguText(msg)
    ? "సర్వర్ సమస్య. దయచేసి మళ్లీ ప్రయత్నించండి."
    : "Connection error. Please try again.";
}

function clearMediaOverlay() {
  if (sliderInterval) {
    clearInterval(sliderInterval);
    sliderInterval = null;
  }

  if (mediaContent) mediaContent.innerHTML = "";
}

function closeMediaOverlay() {
  clearMediaOverlay();

  if (mediaOverlay) {
    mediaOverlay.classList.add("hidden");
    mediaOverlay.setAttribute("aria-hidden", "true");
  }

  mediaBlockingWake = false;
  setVoiceText("Wake mode active", "Say \"Hello Ideal AI\"");
  if (!isSpeaking) startWakeListening();
}

function openMediaOverlay() {
  if (!mediaOverlay) return;
  mediaBlockingWake = true;
  stopWakeListening();
  mediaOverlay.classList.remove("hidden");
  mediaOverlay.setAttribute("aria-hidden", "false");
}

function showImagesOverlay(images) {
  if (!mediaOverlay || !mediaContent || !Array.isArray(images) || images.length === 0) return;

  clearMediaOverlay();
  openMediaOverlay();

  const img = document.createElement("img");
  img.className = "media-image";
  img.alt = "Campus photo";
  img.decoding = "async";
  img.fetchPriority = "high";

  mediaContent.appendChild(img);

  let index = 0;

  function setImage() {
    img.style.opacity = "0";
    const nextSrc = images[index];
    requestAnimationFrame(() => {
      img.src = nextSrc;
      img.alt = `Campus photo ${index + 1}`;
      requestAnimationFrame(() => {
        img.style.opacity = "1";
      });
    });
  }

  setImage();

  sliderInterval = setInterval(() => {
    index += 1;
    if (index >= images.length) {
      closeMediaOverlay();
    } else {
      setImage();
    }
  }, 3200);
}

function showVideoOverlay(videoUrl) {
  if (!mediaOverlay || !mediaContent || !videoUrl) {
    showToast("Video is not available right now");
    return;
  }

  clearMediaOverlay();
  openMediaOverlay();

  const video = document.createElement("video");
  video.className = "media-video";
  video.src = videoUrl;
  video.setAttribute("playsinline", "");
  video.setAttribute("webkit-playsinline", "");
  video.preload = "auto";
  video.controls = true;
  video.playsInline = true;

  video.addEventListener("ended", () => closeMediaOverlay());
  video.addEventListener("error", () => {
    closeMediaOverlay();
    showToast("Video could not be played");
  });

  mediaContent.appendChild(video);

  video.load();
  const playAttempt = video.play();
  if (playAttempt && typeof playAttempt.catch === "function") {
    playAttempt.catch(() => {
      /* autoplay blocked — user can press play */
    });
  }
}

function handleApiResponse(data) {
  if (!data || typeof data !== "object") return false;

  if (data.show_images === true && Array.isArray(data.images) && data.images.length > 0) {
    showImagesOverlay(data.images);
    return true;
  }

  const videoUrl = data.video_url || data.video;

  if (data.show_video === true && typeof videoUrl === "string" && videoUrl) {
    showVideoOverlay(videoUrl);
    return true;
  }

  return false;
}

async function sendMessage(msg) {
  if (!msg || isRequestInFlight) return;
  const trimmedMessage = String(msg).trim();
  if (!trimmedMessage) return;
  isRequestInFlight = true;

  stopSpeaking();
  setVoiceText("Processing", trimmedMessage);
  addMessage("user", trimmedMessage);

  conversationHistory.push({ role: "user", content: trimmedMessage });
  showTyping();

  try {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 20000);
    const res = await fetch(`${API_BASE}/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: trimmedMessage, conversationHistory: conversationHistory.slice(-12) }),
      signal: controller.signal,
    });
    clearTimeout(timeoutId);

    let data = null;
    try {
      data = await res.json();
    } catch {
      data = {};
    }
    if (!res.ok) throw new Error(data.error || "Chat request failed");

    hideTyping();

    const reply = data.reply || (
      isTeluguText(trimmedMessage)
        ? "సమాధానం రాలేదు. మళ్లీ ప్రయత్నించండి."
        : "I did not get a response. Please try again."
    );

    addMessage("assistant", reply);
    conversationHistory.push({ role: "assistant", content: reply });

    const showedMedia = handleApiResponse(data);
    const isVideo = Boolean(data.show_video && (data.video_url || data.video));

    if (showedMedia) {
      requestAnimationFrame(() => {
        requestAnimationFrame(() => {
          if (isVideo) return;
          speak(reply);
        });
      });
    } else {
      setTimeout(() => speak(reply), 120);
    }
  } catch {
    hideTyping();

    const reply = fallbackReplyForCurrentLanguage(trimmedMessage);
    addMessage("assistant", reply);
    speak(reply);
  } finally {
    isRequestInFlight = false;
  }
}

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", initializeDomReferencesAndHandlers);
} else {
  initializeDomReferencesAndHandlers();
}
