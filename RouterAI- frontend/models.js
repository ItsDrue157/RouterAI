// Seleção apenas visual nesta etapa. Não altera o corpo das mensagens do chat.
const modelPicker = document.querySelector("#model-picker");
const modelToggle = document.querySelector("#model-toggle");
const modelPanel = document.querySelector("#model-panel");
const modelLabel = document.querySelector("#model-label");
const modelList = document.querySelector("#model-list");
const modelStatus = document.querySelector("#model-status");
const modelRefresh = document.querySelector("#model-refresh");
let selectedModel = null;
let modelsLoading = false;

function closeModelPanel(returnFocus = false) {
  modelPanel.hidden = true;
  modelToggle.setAttribute("aria-expanded", "false");
  if (returnFocus) modelToggle.focus();
}

function renderModels(models) {
  modelList.replaceChildren();
  if (!models.includes(selectedModel)) selectedModel = null;
  modelLabel.textContent = selectedModel ?? "Modelos";
  modelToggle.title = selectedModel ?? "Escolher modelo";
  for (const id of models) {
    const option = document.createElement("button");
    option.type = "button";
    option.className = "model-option";
    option.setAttribute("aria-pressed", String(id === selectedModel));
    const check = document.createElement("span");
    check.className = "model-check";
    check.setAttribute("aria-hidden", "true");
    check.textContent = "✓";
    const name = document.createElement("span");
    name.className = "model-name";
    name.textContent = id;
    option.append(check, name);
    option.addEventListener("click", () => {
      selectedModel = id;
      modelLabel.textContent = id;
      modelToggle.title = id;
      for (const item of modelList.children) {
        item.setAttribute("aria-pressed", String(item === option));
      }
      closeModelPanel(true);
    });
    modelList.append(option);
  }
}

async function loadModels() {
  if (modelsLoading) return;
  modelsLoading = true;
  modelRefresh.disabled = true;
  modelList.replaceChildren();
  modelList.setAttribute("aria-busy", "true");
  modelStatus.hidden = false;
  modelStatus.textContent = "Carregando modelos…";
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), API_CONFIG.modelsTimeoutMs);
  try {
    const url = `${API_CONFIG.baseUrl.replace(/\/+$/, "")}/${API_CONFIG.modelsPath.replace(/^\/+/, "")}`;
    const response = await fetch(url, {
      headers: { Accept: "application/json" },
      cache: "no-store",
      signal: controller.signal,
    });
    if (!response.ok) throw new Error(`Não foi possível listar os modelos (HTTP ${response.status}).`);
    const data = await response.json();
    if (!data || !Array.isArray(data.models) || data.models.some(id => typeof id !== "string" || !id.trim())) {
      throw new Error("A lista de modelos recebida está em um formato inválido.");
    }
    const models = [...new Set(data.models)];
    renderModels(models);
    modelStatus.hidden = models.length > 0;
    modelStatus.textContent = models.length ? "" : "Nenhum modelo disponível.";
  } catch (error) {
    modelStatus.textContent = error.name === "AbortError"
      ? "A consulta demorou demais. Tente atualizar a lista."
      : error instanceof TypeError
        ? "Não foi possível buscar os modelos. Verifique a conexão com o backend."
        : error instanceof SyntaxError
          ? "A lista de modelos recebida está em um formato inválido."
          : error.message;
  } finally {
    clearTimeout(timeout);
    modelsLoading = false;
    modelRefresh.disabled = false;
    modelList.setAttribute("aria-busy", "false");
  }
}

modelToggle.addEventListener("click", () => {
  if (!modelPanel.hidden) {
    closeModelPanel();
    return;
  }
  modelPanel.hidden = false;
  modelToggle.setAttribute("aria-expanded", "true");
  void loadModels();
});
modelRefresh.addEventListener("click", () => void loadModels());
document.addEventListener("click", event => {
  if (!modelPicker.contains(event.target)) closeModelPanel();
});
document.addEventListener("focusin", event => {
  if (!modelPicker.contains(event.target)) closeModelPanel();
});
modelPicker.addEventListener("keydown", event => {
  if (event.key === "Escape" && !modelPanel.hidden) {
    event.preventDefault();
    closeModelPanel(true);
  }
});
