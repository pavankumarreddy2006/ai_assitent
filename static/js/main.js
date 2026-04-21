// static/js/main.js
"use strict";

let chatInput, sendBtn, messagesArea, welcomeScreen, micBtn, transcriptPreview;
let chatHistory = [];
let recognition = null;
let isListening = false;

function esc(str) {
  return String(str ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");
}

function scrollBottom() {
  messagesArea.scrollTop = messagesArea.scrollHeight;
}

function formatReply(text) {
  if (!text) return "";
  return esc(text)
    .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")
    .replace(/\n/g, "<br>");
}

////////////////////////////////////////////////////////////
// 🔥 SWEET FEMALE VOICE MODULE (ADDED ONLY)
////////////////////////////////////////////////////////////

function speak(text) {
  if (!("speechSynthesis" in window)) return;

  speechSynthesis.cancel();

  const utterance = new SpeechSynthesisUtterance(text);

  const isTelugu = /[\u0C00-\u0C7F]/.test(text);
  utterance.lang = isTelugu ? "te-IN" : "en-US";

  const voices = speechSynthesis.getVoices();

  let voice = null;

  const preferredVoices = [
    "Google UK English Female",
    "Google US English",
    "Microsoft Zira",
    "Microsoft Aria",
    "Samantha"
  ];

  if (isTelugu) {
    voice = voices.find(v => v.lang.includes("te"));
  }

  if (!voice) {
    for (let name of preferredVoices) {
      voice = voices.find(v => v.name.includes(name));
      if (voice) break;
    }
  }

  if (!voice) {
    voice = voices.find(v => v.lang.includes("en"));
  }

  if (voice) utterance.voice = voice;

  utterance.rate = 0.9;   // smooth
  utterance.pitch = 1.3;  // feminine tone
  utterance.volume = 1;

  speechSynthesis.speak(utterance);
}

// load voices properly
speechSynthesis.onvoiceschanged = () => {
  speechSynthesis.getVoices();
};

////////////////////////////////////////////////////////////

function appendAIMessage(data) {
  const reply = data?.reply ?? "";
  const showImages = Boolean(data?.show_images);
  const showVideo = Boolean(data?.show_video);
  const images = Array.isArray(data?.images) ? data.images : [];
  const videoUrl = data?.video_url ?? "";

  let mediaHtml = "";

  if (showVideo && videoUrl) {
    mediaHtml = `
      <div class="media-frame">
        <video class="media-video" controls autoplay muted playsinline>
          <source src="${esc(videoUrl)}" type="video/mp4">
          Your browser does not support video.
        </video>
      </div>`;
  }

  if (showImages && images.length) {
    const id = "slider-" + Date.now();
    mediaHtml = `
      <div class="media-frame">
        <div class="image-slider" id="${id}">
          <button class="slide-btn prev" onclick="changeSlide('${id}',-1)">&#8249;</button>
          <div class="slides">
            ${images.map((s, i) => `<img src="${esc(s)}" class="slide${i === 0 ? " active" : ""}" alt="campus" loading="lazy"/>`).join("")}
          </div>
          <button class="slide-btn next" onclick="changeSlide('${id}',1)">&#8250;</button>
        </div>
      </div>`;
  }

  const div = document.createElement("div");
  div.className = "message ai-message";
  div.innerHTML = `
    <div class="ai-avatar">IC</div>
    <div class="message-bubble ai-bubble">
      <div>${formatReply(reply)}</div>
      ${mediaHtml}
    </div>`;
  messagesArea.appendChild(div);

  ////////////////////////////////////////////////////////////
  // 🔥 VOICE RESPONSE TRIGGER (ADDED ONLY)
  ////////////////////////////////////////////////////////////
  speak(reply);

  scrollBottom();
}

function changeSlide(id, dir) {
  const slider = document.getElementById(id);
  if (!slider) return;
  const slides = slider.querySelectorAll(".slide");
  let cur = 0;
  slides.forEach((s, i) => { if (s.classList.contains("active")) cur = i; });
  slides[cur].classList.remove("active");
  let next = (cur + dir + slides.length) % slides.length;
  slides[next].classList.add("active");
}

function appendTyping() {
  const id = "typing-" + Date.now();
  const div = document.createElement("div");
  div.id = id;
  div.className = "message ai-message";
  div.innerHTML = `
    <div class="ai-avatar">IC</div>
    <div class="message-bubble ai-bubble">
      <div class="typing-indicator"><span></span><span></span><span></span></div>
    </div>`;
  messagesArea.appendChild(div);
  scrollBottom();
  return id;
}

function appendUserMessage(text) {
  const div = document.createElement("div");
  div.className = "message user-message";
  div.innerHTML = `<div class="message-bubble user-bubble">${esc(text)}</div>`;
  messagesArea.appendChild(div);
  scrollBottom();
}

function removeEl(id) {
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
    try { data = await res.json(); } catch { throw new Error("Invalid JSON"); }

    removeEl(typingId);

    if (res.ok && data.reply !== undefined) {
      appendAIMessage(data);
      chatHistory.push({ role: "assistant", content: data.reply });
    } else {
      appendAIMessage({ reply: data?.reply || "Something went wrong. Please try again." });
    }
  } catch (err) {
    console.error(err);
    removeEl(typingId);
    appendAIMessage({ reply: "Connection error. Please check your network and try again." });
  } finally {
    sendBtn.disabled = false;
    scrollBottom();
  }
}

function initSpeech() {
  const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (!SR) return null;
  const rec = new SR();
  rec.lang = "en-IN";
  rec.interimResults = true;
  rec.continuous = false;

  rec.onresult = (e) => {
    let t = "";
    for (let i = e.resultIndex; i < e.results.length; i++) t += e.results[i][0].transcript;
    chatInput.value = t;
    if (transcriptPreview) transcriptPreview.textContent = t;

    const last = e.results[e.results.length - 1];
    if (last?.isFinal) {
      setTimeout(() => {
        if (transcriptPreview) transcriptPreview.textContent = "";
        sendMessage();
      }, 300);
    }
  };

  rec.onerror = rec.onend = () => {
    isListening = false;
    micBtn.classList.remove("active");
    if (transcriptPreview) transcriptPreview.textContent = "";
  };

  return rec;
}

function toggleVoice() {
  if (!recognition) recognition = initSpeech();
  if (!recognition) {
    appendAIMessage({ reply: "Voice input is not supported in this browser." });
    return;
  }

  if (isListening) {
    recognition.stop();
    isListening = false;
    micBtn.classList.remove("active");
  } else {
    try {
      recognition.start();
      isListening = true;
      micBtn.classList.add("active");
      if (transcriptPreview) transcriptPreview.textContent = "Listening...";
    } catch {
      isListening = false;
      micBtn.classList.remove("active");
    }
  }
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
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  });
});