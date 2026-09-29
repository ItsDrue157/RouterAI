# Repository Guide

## Setup and Commands

- This project is Windows-first and requires Python 3.10+ plus LM Studio. Run commands from the repository root: active code opens `agents/modelos.json` and `logs/routerai.log` with relative paths.
- Prepare the required LM Studio models/server with `./setup_models.bat`; it downloads `qwen/qwen3-1.7b` and `qwen/qwen3-4b-2507` and attempts to start port 1234.
- First setup is `./setup.bat`. It installs `uv` if needed, creates `.venv`, installs `requirements.txt`, initializes SQLite, and then launches the app.
- Subsequent startup is `./start.bat`. It initializes the databases, then runs Uvicorn at `127.0.0.1:8000` and the static frontend at `127.0.0.1:5000`. Its LM Studio probe only warns; model-backed requests still fail if port 1234 is unavailable.
- Database-only initialization is `./init_db.bat` or `./.venv/Scripts/python.exe db/banco.py`.
- There is no configured test runner, lint, formatter, type checker, CI, or lockfile. `./.venv/Scripts/python.exe tests/teste_sql.py` is only a manual diagnostic that prints messages for hard-coded `chat_id=47`; it has no assertions.

## Runtime Structure

- `main.py` is the FastAPI entrypoint and owns `POST /chat`, `POST /chat/message`, SQLite history, and specialized-agent follow-ups.
- `routers/router.py` is the active initial-message router. Root `router.py` is only a compatibility re-export; `routers/routers_teste.py` is experimental and disconnected from the API.
- Route IDs and agent keys are coupled across code and configuration: `0 -> router`, `1 -> matematico`, `2 -> coder`. If changing them, update `RouterResponse`, both route maps in `main.py`, `mapa_de_funcoes`, and `agents/modelos.json` together.
- Do not assume every field in `agents/modelos.json` controls the active path. Initial general responses hard-code `qwen/qwen3-4b-2507`; initial math and coding routes both call `router_coding`; only specialized follow-ups load their model and prompt from JSON. Active generation does not consume `no_think` separately.
- Specialized follow-ups use the OpenAI-compatible LM Studio endpoint at `http://localhost:1234/v1` and include stored history. General follow-ups are routed again without passing database history to the generated response.
- `RouterAI- frontend/` is plain static HTML/CSS/JS with no build step. `index.html` loads vendored Marked and DOMPurify before `markdown.js` and `app.js`; `app.js` hard-codes the API URL and a 60-second timeout.

## Persistence and Local State

- `db/banco.py` creates `db/users.db` (`chats`) and `db/messages.db` (`messages`) with `CREATE TABLE IF NOT EXISTS`; there is no migration mechanism, so schema edits do not upgrade existing local databases.
- SQLite files, virtual environments, bytecode, and logs are ignored local artifacts. Ensure `logs/` exists before importing/running `main.py` in a fresh checkout because its `FileHandler` does not create the directory.
- Chat IDs are allocated in frontend storage, not by the backend. Different browsers/origins or cleared storage can reuse an existing backend ID; there is no authentication or server-side ownership check.
- Backend CORS permits only localhost/127.0.0.1 frontend origins on ports 5000 and 5500. Keep this aligned if changing frontend serving ports.
