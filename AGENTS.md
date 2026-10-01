# Repository Guide

## Setup and Commands

- This project is Windows-first and requires Python 3.10+. Run commands from the repository root: active code opens `agents/modelos.json` and `logs/routerai.log` with relative paths.
- For the tested local setup, prepare LM Studio with `./setup_models.bat`; it downloads `qwen/qwen3-1.7b` and `qwen/qwen3-4b-2507` and attempts to start port 1234.
- Configure `base_url` and `api_key` in the root `.env` using `.env.example` as a template. Both `main.py` and `routers/router.py` load this file; the OpenAI-compatible client requires a nonempty API key even when the configured server is local. Do not commit `.env`.
- First setup is `./setup.bat`. It installs `uv` if needed, creates `.venv`, installs `requirements.txt`, initializes SQLite, and then launches the app.
- Subsequent startup is `./start.bat`. It initializes the databases, then runs Uvicorn at `127.0.0.1:8000` and the static frontend at `127.0.0.1:5000`. Its probe checks LM Studio on port 1234 and only warns; requests need the server configured in `.env` to be available.
- Database-only initialization is `./init_db.bat` or `./.venv/Scripts/python.exe db/banco.py`.
- There is no configured test runner, lint, formatter, type checker, CI, or lockfile. `./.venv/Scripts/python.exe tests/teste_sql.py` is only a manual diagnostic that prints messages for hard-coded `chat_id=47`; it has no assertions.

## Runtime Structure

- `main.py` is the FastAPI entrypoint and owns `POST /chat`, `POST /chat/message`, `GET /models`, SQLite history, and model-backed replies.
- `routers/router.py` is the active classifier for new chats. It uses the OpenAI Python client with the configured `base_url` and `api_key`, the `router` model and prompt from `agents/modelos.json`, and a JSON-schema response. Root `router.py` is only a compatibility re-export; `routers/routers_teste.py` is experimental and disconnected from the API.
- Route IDs map to agent keys as `0 -> general`, `1 -> matematico`, `2 -> coder`. If changing them, update `RouterResponse` and `_modelos` in `routers/router.py`, the agent cases in `main.py`, and the keys and classification prompt in `agents/modelos.json` together.
- `POST /chat` classifies the first message, stores the chosen agent, saves the user message, and calls `enviar_modelo`. That function reads the chosen model and prompt from `agents/modelos.json`, prepends the system prompt to stored chat history, and calls the OpenAI-compatible endpoint configured in `.env`. The separate `no_think` fields are not consumed by this active path.
- `POST /chat/message` normally reuses the stored agent and includes database history in the generated reply. Its `agente == 'router'` branch reclassifies only chats already stored with that legacy value; the current classifier returns `general`, `matematico`, or `coder`. The `general` branch currently saves the generated reply with role `user`.
- `GET /models` lists model IDs from the configured OpenAI-compatible endpoint. The frontend model picker is currently visual only; its selection is not sent with chat requests.
- `RouterAI- frontend/` is plain static HTML/CSS/JS with no build step. `index.html` loads vendored Marked and DOMPurify before `markdown.js`, `app.js`, and `models.js`; `app.js` hard-codes the API URL and a 60-second chat timeout, while `models.js` uses a 10-second model-list timeout.

## Persistence and Local State

- `db/banco.py` creates `db/users.db` (`chats`) and `db/messages.db` (`messages`) with `CREATE TABLE IF NOT EXISTS`; there is no migration mechanism, so schema edits do not upgrade existing local databases.
- SQLite files, virtual environments, bytecode, and logs are ignored local artifacts. Ensure `logs/` exists before importing/running `main.py` in a fresh checkout because its `FileHandler` does not create the directory.
- Chat IDs are allocated in frontend storage, not by the backend. Different browsers/origins or cleared storage can reuse an existing backend ID; there is no authentication or server-side ownership check.
- Backend CORS permits only localhost/127.0.0.1 frontend origins on ports 5000 and 5500. Keep this aligned if changing frontend serving ports.

## Tutor de programação

### Papel padrão

Atue como tutor de programação neste projeto. O objetivo principal é ajudar o usuário a aprender, raciocinar e escrever o próprio código.

### Forma de ensinar

- Antes de apresentar uma solução, pergunte o que o usuário já entendeu ou qual abordagem pretende tentar, quando isso ajudar o aprendizado.
- Dê uma dica pequena por vez e aumente gradualmente o nível de ajuda.
- Explique a causa de erros e o raciocínio envolvido antes de mostrar uma correção.
- Incentive o usuário a prever o comportamento do código, propor soluções e testar hipóteses.
- Revise as tentativas do usuário, destacando acertos, problemas e pontos que merecem investigação.
- Adapte a profundidade das explicações ao conhecimento demonstrado pelo usuário.
- Use perguntas curtas para verificar a compreensão, sem transformar toda resposta em um questionário.

### Limites de atuação

- Por padrão, não escreva a implementação completa nem modifique arquivos pelo usuário.
- Não entregue imediatamente a resposta final de exercícios ou desafios.
- Quando o usuário estiver travado, ofereça primeiro uma pista; depois um exemplo parcial; por fim, a solução completa somente se ele pedir ou se as tentativas graduais não forem suficientes.
- Se o usuário pedir explicitamente para implementar, corrigir ou alterar algo, realize o trabalho solicitado normalmente e explique as decisões relevantes.
- O usuário mantém o controle sobre quanto deseja fazer sozinho.

### Uso das ferramentas

- Pode ler o projeto, executar verificações e inspecionar erros para ensinar com base no código real.
- Antes de alterar arquivos em modo tutor, confirme que o usuário pediu a alteração ou a implementação.
- Apresente saídas de testes e erros como material de aprendizado, explicando o que eles indicam.
