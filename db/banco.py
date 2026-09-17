"""
Módulo de inicialização e verificação das bases de dados SQLite do RouterAI.
Cria 'users.db' e 'messages.db' com seus respectivos schemas caso ainda não existam.
"""

import sqlite3
from pathlib import Path

# Diretório e caminhos dos bancos de dados
DB_DIR = Path(__file__).resolve().parent
DB_USERS = DB_DIR / "users.db"
DB_MESSAGES = DB_DIR / "messages.db"

# Schema do banco users.db
SCHEMA_USERS = """
CREATE TABLE IF NOT EXISTS chats (
    chat_id TEXT PRIMARY KEY,
    agente TEXT NOT NULL,
    criado_em DATETIME DEFAULT CURRENT_TIMESTAMP
);
"""

# Schema do banco messages.db
SCHEMA_MESSAGES = """
CREATE TABLE IF NOT EXISTS messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    chat_id TEXT NOT NULL,
    role TEXT NOT NULL,
    content TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
"""


def criar_bancos():
    """Garante a existência do diretório e das tabelas em users.db e messages.db."""
    DB_DIR.mkdir(parents=True, exist_ok=True)

    # 1. Inicializa users.db
    with sqlite3.connect(DB_USERS) as conn_users:
        conn_users.execute(SCHEMA_USERS)
        conn_users.commit()
    print(f"[OK] users.db verificado/criado com sucesso: {DB_USERS}")

    # 2. Inicializa messages.db
    with sqlite3.connect(DB_MESSAGES) as conn_messages:
        conn_messages.execute(SCHEMA_MESSAGES)
        conn_messages.commit()
    print(f"[OK] messages.db verificado/criado com sucesso: {DB_MESSAGES}")


if __name__ == "__main__":
    criar_bancos()
