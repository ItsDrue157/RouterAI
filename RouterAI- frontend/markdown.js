// Markdown local: não depende de CDN ou de alterações no backend.
(() => {
  const escapeHtml = text => text.replace(/[&<>"']/g, character => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;",
  })[character]);

  const parser = window.marked ? new window.marked.Marked({
    gfm: true,
    breaks: true,
    renderer: {
      // HTML literal e imagens recebidos ficam como texto, sem conteúdo ativo.
      html({ text }) { return escapeHtml(text); },
      image({ text }) { return escapeHtml(text || "Imagem"); },
    },
  }) : null;

  window.renderAssistantMarkdown = (container, source) => {
    // Se algum arquivo não carregar, mantém a resposta legível como texto.
    container.textContent = source;
    if (!parser || !window.DOMPurify?.isSupported) return;
    try {
      const fragment = window.DOMPurify.sanitize(parser.parse(source), {
        RETURN_DOM_FRAGMENT: true,
        ALLOWED_TAGS: [
          "p", "br", "strong", "em", "del", "s", "h1", "h2", "h3", "h4", "h5", "h6",
          "ul", "ol", "li", "blockquote", "pre", "code", "hr", "a",
          "table", "thead", "tbody", "tr", "th", "td", "input",
        ],
        ALLOWED_ATTR: ["href", "title", "start", "align", "type", "checked", "disabled"],
        ALLOW_DATA_ATTR: false,
        ALLOW_ARIA_ATTR: false,
        ALLOWED_URI_REGEXP: /^(?:https?:|mailto:)/i,
      });
      fragment.querySelectorAll("a[href]").forEach(link => {
        link.target = "_blank";
        link.rel = "noopener noreferrer";
      });
      fragment.querySelectorAll("input").forEach(checkbox => {
        checkbox.type = "checkbox";
        checkbox.disabled = true;
        checkbox.setAttribute("aria-label", checkbox.checked ? "Concluído" : "Pendente");
      });
      fragment.querySelectorAll("table").forEach(table => {
        const wrapper = document.createElement("div");
        wrapper.className = "markdown-table";
        wrapper.tabIndex = 0;
        wrapper.setAttribute("role", "region");
        wrapper.setAttribute("aria-label", "Tabela da resposta; role para ver todas as colunas");
        table.replaceWith(wrapper);
        wrapper.append(table);
      });
      fragment.querySelectorAll("pre").forEach(block => {
        block.tabIndex = 0;
        block.setAttribute("aria-label", "Bloco de código");
      });
      container.replaceChildren(fragment);
      container.classList.add("markdown");
    } catch (error) {
      console.warn("[RouterAI] Markdown indisponível; exibindo texto simples.", error);
    }
  };
})();
