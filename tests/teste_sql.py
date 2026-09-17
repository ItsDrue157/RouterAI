import sqlite3
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

DB_PATH = Path(__file__).resolve().parent.parent / "db" / "messages.db"

def buscar_historico(chat_id):
    con = sqlite3.connect(DB_PATH)
    cursor = con.cursor()

    with con:
        cursor.execute("SELECT role, content FROM messages WHERE chat_id=? ORDER BY id", (chat_id,))
        historico = cursor.fetchall()
    return historico

    # with con:
    #     cursor.execute("SELECT agente from chats WHERE chat_id=?",(chat_id,))
    #     agente = cursor.fetchall()
    #     print (agente)

def montar_historico(historico):
    messages = []
    
    for role, content in historico:
        messages.append({'role':role, 'content':content})
    return messages
    
#buscar_historico(chat_id=48)
#montar_historico(buscar_historico(chat_id=47))
contexto = montar_historico(buscar_historico(chat_id=47))
print(contexto)
