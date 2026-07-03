let currentConversationId = null;

const conversationListEl = document.getElementById("conversation-list");
const messagesEl = document.getElementById("messages");
const chatForm = document.getElementById("chat-form");
const chatInput = document.getElementById("chat-input");
const newChatBtn = document.getElementById("new-chat-btn");
const modelSelect = document.getElementById("model-select");

async function loadConversations() {
  const res = await fetch("/api/conversations");
  const conversations = await res.json();
  conversationListEl.innerHTML = "";
  for (const conv of conversations) {
    const li = document.createElement("li");
    li.className = conv.id === currentConversationId ? "active" : "";

    const titleSpan = document.createElement("span");
    titleSpan.textContent = conv.title;
    titleSpan.style.overflow = "hidden";
    titleSpan.style.textOverflow = "ellipsis";
    titleSpan.onclick = () => selectConversation(conv.id);

    const deleteBtn = document.createElement("button");
    deleteBtn.className = "delete-btn";
    deleteBtn.textContent = "✕";
    deleteBtn.onclick = async (e) => {
      e.stopPropagation();
      await fetch(`/api/conversations/${conv.id}`, { method: "DELETE" });
      if (currentConversationId === conv.id) {
        currentConversationId = null;
        messagesEl.innerHTML = "";
      }
      loadConversations();
    };

    li.appendChild(titleSpan);
    li.appendChild(deleteBtn);
    conversationListEl.appendChild(li);
  }
}

async function selectConversation(id) {
  currentConversationId = id;
  const res = await fetch(`/api/conversations/${id}`);
  const conv = await res.json();
  messagesEl.innerHTML = "";
  modelSelect.value = conv.model;
  for (const msg of conv.messages) {
    appendMessage(msg.role, msg.content);
  }
  loadConversations();
}

function appendMessage(role, content) {
  const div = document.createElement("div");
  div.className = `message ${role}`;
  div.textContent = content;
  messagesEl.appendChild(div);
  messagesEl.scrollTop = messagesEl.scrollHeight;
  return div;
}

newChatBtn.onclick = async () => {
  const res = await fetch("/api/conversations", { method: "POST" });
  const data = await res.json();
  await selectConversation(data.id);
};

modelSelect.onchange = async () => {
  if (!currentConversationId) return;
  await fetch(`/api/conversations/${currentConversationId}/model`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ model: modelSelect.value }),
  });
};

chatForm.onsubmit = async (e) => {
  e.preventDefault();
  const text = chatInput.value.trim();
  if (!text) return;

  if (!currentConversationId) {
    const res = await fetch("/api/conversations", { method: "POST" });
    const data = await res.json();
    currentConversationId = data.id;
  }

  chatInput.value = "";
  appendMessage("user", text);
  const assistantDiv = appendMessage("assistant", "");

  const res = await fetch(`/api/conversations/${currentConversationId}/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message: text }),
  });

  const reader = res.body.getReader();
  const decoder = new TextDecoder();
  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    assistantDiv.textContent += decoder.decode(value, { stream: true });
    messagesEl.scrollTop = messagesEl.scrollHeight;
  }

  loadConversations();
};

loadConversations();
