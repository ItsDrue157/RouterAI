// Toda abertura ou atualização começa no modo escuro, antes de carregar o CSS.
(() => {
  function applyTheme(theme) {
    document.documentElement.dataset.theme = theme;
    document.querySelector('meta[name="theme-color"]').content = theme === "dark" ? "#111218" : "#f7f8fc";
    const button = document.querySelector("#theme-toggle");
    if (button) {
      button.setAttribute("aria-pressed", String(theme === "dark"));
      button.title = theme === "dark" ? "Ativar modo claro" : "Ativar modo escuro";
    }
  }

  applyTheme("dark");

  document.addEventListener("DOMContentLoaded", () => {
    applyTheme("dark");
    document.querySelector("#theme-toggle").addEventListener("click", () => {
      applyTheme(document.documentElement.dataset.theme === "dark" ? "light" : "dark");
    });
  });
})();
