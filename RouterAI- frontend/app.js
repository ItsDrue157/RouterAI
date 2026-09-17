// EDITE AQUI para combinar com o seu backend.
const API_CONFIG = {
  baseUrl: "http://127.0.0.1:8000",
  createChatPath: "/chat", // Primeira mensagem: { chat_id, input }
  sendMessagePath: "/chat/message", // Próximas mensagens: { chat_id, input }
  timeoutMs: 60000,
};

// Adapte aqui se o backend usar outros nomes ou um objeto aninhado.
function readApiResponse(data) {
  return {
    chatId: data.chat_id,
    reply: data.reply ?? data.response ?? data.output ?? data.text,
  };
}

const STORAGE_KEY = "routerai.conversation.v1";
const COUNTER_KEY = "routerai.lastChatId.v1";
const form = document.querySelector("#chat-form");
const input = document.querySelector("#input");
const sendButton = document.querySelector("#send");
const newChatButton = document.querySelector("#new-chat");
const messages = document.querySelector("#messages");
const conversation = document.querySelector("#conversation");
const welcome = document.querySelector("#welcome");
const loading = document.querySelector("#loading");
const errorBox = document.querySelector("#error");
const chatStatus = document.querySelector("#chat-status");
let busy = false;
let state = restoreConversation();
let lastSessionId = Number.isSafeInteger(Number(state.chatId)) ? Number(state.chatId) : 0;
let temporaryLastChatId = lastSessionId;

// O ID nasce no front. O localStorage faz o contador continuar após atualizar.
// Se o navegador bloquear esse armazenamento, a conversa ainda funciona nesta aba.
async function allocateChatId() {
  const increment = () => {
    let previous = temporaryLastChatId;
    try { previous = Math.max(previous, Number(localStorage.getItem(COUNTER_KEY) ?? 0)); }
    catch { /* Usa o contador desta aba como alternativa. */ }
    if (!Number.isSafeInteger(previous) || previous < 0) {
      previous = temporaryLastChatId;
    }
    const next = Math.max(previous, lastSessionId) + 1;
    if (!Number.isSafeInteger(next)) throw new Error("O contador local atingiu seu limite.");
    try { localStorage.setItem(COUNTER_KEY, String(next)); }
    catch { /* O ID continua válido enquanto esta aba estiver aberta. */ }
    lastSessionId = next;
    temporaryLastChatId = next;
    return next;
  };
  // Serializa a reserva entre abas da mesma origem, quando o navegador suporta.
  if (navigator.locks) return navigator.locks.request(COUNTER_KEY, increment);
  return increment();
}

function validId(value) {
  return (typeof value === "string" && value.trim().length > 0)
    || (typeof value === "number" && Number.isFinite(value));
}

function restoreConversation() {
  try {
    // Mantém o chat ao atualizar a página, apenas nesta sessão/aba.
    const saved = JSON.parse(sessionStorage.getItem(STORAGE_KEY));
    if (saved && Array.isArray(saved.messages)) {
      return {
        chatId: validId(saved.chatId) ? saved.chatId : null,
        created: validId(saved.chatId) && (typeof saved.created === "boolean" ? saved.created : true),
        messages: saved.messages.filter(message =>
          ["user", "assistant"].includes(message.role) && typeof message.content === "string"
        ).map(message => ({
          role: message.role,
          content: message.content,
          failed: Boolean(message.failed || message.pending),
        })),
      };
    }
  } catch { /* O chat funciona mesmo com armazenamento indisponível. */ }
  return { chatId: null, created: false, messages: [] };
}

function saveConversation() {
  try { sessionStorage.setItem(STORAGE_KEY, JSON.stringify(state)); }
  catch { /* Não interrompe o envio se o armazenamento estiver cheio/bloqueado. */ }
}

function scrollToLatest() {
  conversation.scrollTop = conversation.scrollHeight;
}

function appendMessage(message) {
  const article = document.createElement("article");
  article.className = `message ${message.role}${message.failed ? " failed" : ""}`;
  const label = document.createElement("p");
  label.className = "message-label";
  label.textContent = message.role === "user" ? "Você" : "RouterAI";
  if (message.failed) label.textContent += " · resposta não recebida";
  const content = document.createElement("div");
  content.className = "message-content";
  if (message.role === "assistant" && window.renderAssistantMarkdown) {
    window.renderAssistantMarkdown(content, message.content);
  } else {
    content.textContent = message.content;
  }
  article.append(label, content);
  messages.append(article);
  welcome.hidden = true;
  return article;
}

function updateStatus() {
  if (state.chatId === null) {
    chatStatus.textContent = "Nova conversa";
    chatStatus.title = "O ID será reservado antes do primeiro envio";
    return;
  }
  chatStatus.textContent = state.created ? `Chat · ${state.chatId}` : `Chat · ${state.chatId} (novo)`;
  chatStatus.title = `chat_id: ${state.chatId}`;
}

function resizeInput() {
  input.style.height = "auto";
  input.style.height = `${Math.min(input.scrollHeight, 160)}px`;
  sendButton.disabled = busy || !input.value.trim();
}

function setBusy(value) {
  busy = value;
  input.disabled = value;
  newChatButton.disabled = value;
  loading.hidden = !value;
  sendButton.disabled = value || !input.value.trim();
  form.setAttribute("aria-busy", String(value));
  scrollToLatest();
}

async function reserveCurrentChatId() {
  if (state.chatId === null) {
    state.chatId = await allocateChatId();
    saveConversation();
    updateStatus();
  }
  return state.chatId;
}

async function buildChatRequest(text) {
  const chatId = await reserveCurrentChatId();
  // Ter um ID reservado não significa que o backend já criou a conversa.
  const isNewChat = !state.created;
  const path = isNewChat ? API_CONFIG.createChatPath : API_CONFIG.sendMessagePath;
  return {
    isNewChat,
    url: `${API_CONFIG.baseUrl.replace(/\/+$/, "")}/${path.replace(/^\/+/, "")}`,
    // Este é o corpo enviado para o backend em toda mensagem.
    body: { chat_id: chatId, input: text },
  };
}

async function requestReply(text) {
  const request = await buildChatRequest(text);
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), API_CONFIG.timeoutMs);
  try {
    console.info("[RouterAI] Enviando mensagem", { url: request.url, body: request.body });
    const response = await fetch(request.url, {
      method: "POST",
      headers: { "Content-Type": "application/json", Accept: "application/json" },
      body: JSON.stringify(request.body),
      signal: controller.signal,
    });
    if (!response.ok) throw new Error(`O backend retornou um erro (HTTP ${response.status}). Confira o serviço e o endpoint configurado.`);
    let data;
    try { data = await response.json(); }
    catch (error) {
      if (error.name === "AbortError") throw error;
      throw new Error("O backend precisa retornar uma resposta JSON válida.");
    }
    if (!data || typeof data !== "object") throw new Error("O backend retornou um formato de resposta inesperado.");
    const result = readApiResponse(data);
    if (result.chatId !== undefined && String(result.chatId) !== String(state.chatId)) {
      throw new Error("O backend retornou um chat_id diferente do enviado. Confira o contrato de criação do chat.");
    }
    // Uma resposta de sucesso confirma a criação, mesmo se faltar o texto do bot.
    if (request.isNewChat) {
      state.created = true;
      saveConversation();
      updateStatus();
    }
    if (typeof result.reply !== "string" || !result.reply.trim()) {
      throw new Error("Não encontrei o texto da resposta. Ajuste readApiResponse() em app.js para o formato do seu backend.");
    }
    return result.reply;
  } catch (error) {
    if (error.name === "AbortError") throw new Error("A resposta demorou mais que o esperado. O backend ainda pode estar processando a mensagem.");
    if (error instanceof TypeError) throw new Error("Não foi possível conectar ao backend. Verifique se ele está rodando, a URL em app.js e a configuração de CORS.");
    throw error;
  } finally {
    clearTimeout(timeout);
  }
}

form.addEventListener("submit", async event => {
  event.preventDefault();
  const text = input.value.trim();
  if (!text || busy) return;
  errorBox.hidden = true;
  const userMessage = { role: "user", content: text, pending: true };
  state.messages.push(userMessage);
  const article = appendMessage(userMessage);
  saveConversation();
  input.value = "";
  resizeInput();
  setBusy(true);
  try {
    const reply = await requestReply(text);
    const assistantMessage = { role: "assistant", content: reply };
    state.messages.push(assistantMessage);
    appendMessage(assistantMessage);
  } catch (error) {
    userMessage.failed = true;
    article.classList.add("failed");
    article.querySelector(".message-label").textContent = "Você · resposta não recebida";
    errorBox.textContent = error.message;
    errorBox.hidden = false;
    input.value = text;
  } finally {
    userMessage.pending = false;
    saveConversation();
    setBusy(false);
    resizeInput();
    input.focus();
  }
});

input.addEventListener("input", resizeInput);
input.addEventListener("keydown", event => {
  if (event.key === "Enter" && !event.shiftKey && !event.isComposing) {
    event.preventDefault();
    if (!busy && input.value.trim()) form.requestSubmit();
  }
});

newChatButton.addEventListener("click", async () => {
  if (busy) return;
  newChatButton.disabled = true;
  try {
    // Ao clicar em Nova conversa, o próximo ID já fica reservado no front.
    const chatId = await allocateChatId();
    state = { chatId, created: false, messages: [] };
    saveConversation();
  } catch (error) {
    errorBox.textContent = error.message;
    errorBox.hidden = false;
    return;
  } finally {
    newChatButton.disabled = false;
  }
  messages.replaceChildren();
  welcome.hidden = false;
  errorBox.hidden = true;
  input.value = "";
  updateStatus();
  resizeInput();
  input.focus();
});

document.querySelectorAll("[data-prompt]").forEach(button => {
  button.addEventListener("click", () => {
    input.value = button.dataset.prompt;
    resizeInput();
    input.focus();
  });
});

state.messages.forEach(appendMessage);
updateStatus();
resizeInput();
scrollToLatest();
