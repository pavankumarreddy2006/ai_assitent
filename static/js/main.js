// static/js/main.js
/* ── Complete working main.js for Ideal College AI Chat ─────────────────────── */

let chatHistory = [];
let recognition = null;
let isListening = false;

document.addEventListener('DOMContentLoaded', () => {
  // DOM elements
  const chatInput = document.getElementById('chatInput');
  const sendBtn = document.getElementById('sendBtn');
  const messagesArea = document.getElementById('messagesArea');
  const welcomeScreen = document.getElementById('welcomeScreen');
  const micBtn = document.getElementById('micBtn');

  if (!chatInput || !sendBtn || !messagesArea) {
    console.error('Critical DOM elements missing');
    return;
  }

  // ====================== HELPER FUNCTIONS ======================
  function scrollBottom() {
    messagesArea.scrollTop = messagesArea.scrollHeight;
  }

  function appendUserMessage(text) {
    const div = document.createElement('div');
    div.className = 'message user-message';
    div.innerHTML = `
      <div class="message-bubble user-bubble">
        <p>${text}</p>
      </div>
    `;
    messagesArea.appendChild(div);
    scrollBottom();
  }

  function appendAIMessage(data) {
    const {
      reply = '',
      source = '',
      show_images = false,
      show_video = false,
      images = [],
      video_url = ''
    } = data;

    const div = document.createElement('div');
    div.className = 'message ai-message';

    let extraHTML = '';

    // Video
    if (show_video && video_url) {
      extraHTML += `
        <div class="media-container" style="margin: 12px 0;">
          <video src="${video_url}" controls autoplay style="width: 100%; max-height: 320px; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.3);">
            Your browser does not support the video tag.
          </video>
        </div>
      `;
    }

    // Images
    if (show_images && images && images.length > 0) {
      extraHTML += `<div class="media-container images-grid" style="margin: 12px 0; display: flex; flex-wrap: wrap; gap: 10px; justify-content: center;">`;
      images.forEach(src => {
        extraHTML += `
          <img src="${src}" alt="College Image" 
               style="max-width: 260px; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.2);">
        `;
      });
      extraHTML += `</div>`;
    }

    div.innerHTML = `
      <div class="message-bubble ai-bubble">
        <p>${reply}</p>
        ${extraHTML}
        ${source ? `<div class="message-source" style="font-size: 0.75rem; color: #666; margin-top: 8px;">${source}</div>` : ''}
      </div>
    `;
    messagesArea.appendChild(div);
    scrollBottom();
  }

  function appendSimpleAIMessage(text, source = 'System') {
    appendAIMessage({ reply: text, source });
  }

  function appendTyping() {
    const id = 'typing-' + Date.now();
    const div = document.createElement('div');
    div.id = id;
    div.className = 'message ai-message typing-message';
    div.innerHTML = `
      <div class="message-bubble ai-bubble">
        <div class="typing-indicator">
          <span></span>
          <span></span>
          <span></span>
        </div>
      </div>
    `;
    messagesArea.appendChild(div);
    scrollBottom();
    return id;
  }

  function removeElement(id) {
    const el = document.getElementById(id);
    if (el) el.remove();
  }

  // ====================== SEND MESSAGE ======================
  async function sendMessage() {
    const text = chatInput.value.trim();
    if (!text) return;

    // Hide welcome screen on first message
    if (welcomeScreen && welcomeScreen.style.display !== 'none') {
      welcomeScreen.style.display = 'none';
    }
    if (messagesArea.style.display !== 'flex') {
      messagesArea.style.display = 'flex';
    }

    appendUserMessage(text);
    chatHistory.push({ role: "user", content: text });

    chatInput.value = '';
    sendBtn.disabled = true;

    const typingId = appendTyping();

    try {
      const res = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          message: text,
          history: chatHistory.slice(-10)
        })
      });

      let data;
      try {
        data = await res.json();
      } catch (_) {
        throw new Error("Invalid JSON response");
      }

      removeElement(typingId);

      if (res.ok && data.reply !== undefined) {
        appendAIMessage(data);
        chatHistory.push({ role: "assistant", content: data.reply });
      } else {
        appendSimpleAIMessage(data.reply || "Sorry, something went wrong.", "System");
      }
    } catch (err) {
      console.error("Chat error:", err);
      removeElement(typingId);
      appendSimpleAIMessage(
        "Sorry, I couldn't connect to the server right now. Please try again.",
        "System"
      );
    }

    sendBtn.disabled = false;
    scrollBottom();
  }

  // ====================== VOICE INPUT (Web Speech API) ======================
  function initVoiceRecognition() {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) return null;

    const rec = new SpeechRecognition();
    rec.lang = 'en-US';           // Works best in Chrome/Edge. Telugu support is limited but can be 'te-IN'
    rec.interimResults = true;
    rec.maxAlternatives = 1;

    rec.onresult = (event) => {
      let transcript = '';
      for (let i = event.resultIndex; i < event.results.length; i++) {
        transcript += event.results[i][0].transcript;
      }
      chatInput.value = transcript;

      // Auto-send when final result is received
      if (event.results[0].isFinal) {
        setTimeout(() => {
          sendMessage();
        }, 300);
      }
    };

    rec.onerror = (event) => {
      console.error('Speech recognition error:', event);
      isListening = false;
      if (micBtn) micBtn.classList.remove('active', 'listening');
    };

    rec.onend = () => {
      isListening = false;
      if (micBtn) micBtn.classList.remove('active', 'listening');
    };

    return rec;
  }

  function toggleVoice() {
    if (!micBtn) return;

    if (!recognition) {
      recognition = initVoiceRecognition();
      if (!recognition) {
        alert("Voice input is not supported in your browser.\n\nPlease use Google Chrome or Microsoft Edge.");
        return;
      }
    }

    if (isListening) {
      recognition.stop();
    } else {
      try {
        recognition.start();
        isListening = true;
        micBtn.classList.add('active', 'listening');
      } catch (e) {
        console.error(e);
        isListening = false;
        micBtn.classList.remove('active', 'listening');
      }
    }
  }

  // ====================== EVENT LISTENERS ======================
  sendBtn.addEventListener('click', sendMessage);

  chatInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      sendMessage();
    }
  });

  if (micBtn) {
    micBtn.addEventListener('click', toggleVoice);
  }

  // Keyboard shortcut hint
  console.log('%c✅ Ideal College AI Chat fully initialized\nVoice: Mic button | Send: Enter', 'color:#4ade80;font-weight:700');
});