/* ── Send message ─────────────────────────────────────────── */
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
    const res = await fetch("/api/chat", {   // No API_BASE needed
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
    } catch (jsonErr) {
      throw new Error("Invalid response from server");
    }

    removeElement(typingId);

    if (res.ok && data.reply) {
      appendAIMessage({
        reply: data.reply,
        source: data.source || "",
        show_images: data.show_images || false,
        show_video: data.show_video || false,
        images: data.images || [],
        video_url: data.video_url || ""
      });
      chatHistory.push({ role: "assistant", content: data.reply });
    } else {
      throw new Error(data.reply || "Server returned error");
    }

  } catch (err) {
    console.error("Chat error:", err);
    removeElement(typingId);
    appendSimpleAIMessage(
      "Sorry, I couldn't connect to the server right now. Please try again in a moment.", 
      "System"
    );
  }

  scrollBottom();
}