const API_URL = "http://127.0.0.1:8000"; // FastAPI backend URL

// Automatically create a unique session ID per user
const sessionId =
  localStorage.getItem("chatSessionId") ||
  `session-${Date.now()}-${Math.floor(Math.random() * 1000)}`;
localStorage.setItem("chatSessionId", sessionId);

const chatBox = document.getElementById("chat-box");
const sendBtn = document.getElementById("send-btn");
const userInput = document.getElementById("user-input");

// Load previous chat history on page load
async function loadHistory() {
  try {
    const res = await fetch(`${API_URL}/history/${sessionId}`);
    if (!res.ok) {
      console.warn("No previous history found");
      return;
    }

    const history = await res.json();
    if (Array.isArray(history)) {
      history.forEach((msg) => addMessage(msg.role, msg.content));
    }
  } catch (err) {
    console.error("Error loading history:", err);
  }
}

// Function to add messages to chat box
function addMessage(role, content) {
  const msgDiv = document.createElement("div");
  msgDiv.classList.add("message", role === "user" ? "user" : "bot");
  msgDiv.innerText = content;
  chatBox.appendChild(msgDiv);
  chatBox.scrollTop = chatBox.scrollHeight;
}

// Function to send message to backend
async function sendMessage() {
  const message = userInput.value.trim();
  if (!message) return;

  // Show user message immediately
  addMessage("user", message);
  userInput.value = "";

  try {
    const res = await fetch(`${API_URL}/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message, session_id: sessionId }),
    });

    if (!res.ok) throw new Error(`HTTP error ${res.status}`);

    const data = await res.json();
    addMessage("bot", data.reply);
  } catch (err) {
    console.error("Error sending message:", err);
    addMessage("bot", "⚠️ Error connecting to the server. Please try again.");
  }
}


// Event listeners
sendBtn.addEventListener("click", sendMessage);
userInput.addEventListener("keypress", (e) => {
  if (e.key === "Enter") sendMessage();
});

// Load history when page opens
window.addEventListener("load", loadHistory);



