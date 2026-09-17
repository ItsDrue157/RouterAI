from fastapi import FastAPI
#precisa para funcionar o app.add ali
from fastapi.middleware.cors import CORSMiddleware
#
from pydantic import BaseModel

#
import sqlite3

from teste import router, processar_mensagem


app = FastAPI()

#precisa disso pra rodar no local
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5500",
        "http://localhost:5500",
        "http://127.0.0.1:5000",
        "http://localhost:5000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],)


class ChatRequest(BaseModel):
    chat_id: int
    input: str

@app.post("/chat")
def create_new_chat(data: ChatRequest):


    reply_chat =data.input 

    router(reply_chat)

    # con fora da rota da erro de thread
    con = sqlite3.connect('users.db')
    cursor = con.cursor()

    #se n tiver vai gerar none
    cursor.execute(
    "SELECT chat_id FROM chats WHERE chat_id = ?",
    (data.chat_id,)
    )
    chat = cursor.fetchone()
    #colocando o id no banco
    if chat is None:
        agente = 'router'

        cursor.execute(
            "INSERT INTO chats (chat_id, agente) VALUES (?, ?)",
            (data.chat_id, agente)
        )

        con.commit()

    _,reply = processar_mensagem(reply_chat)
    return {
        "chat_id": data.chat_id,
        "reply": reply
    }

@app.post("/chat/message")
def read_message(data: ChatRequest):
    reply_chat =data.input
    _,reply = processar_mensagem(reply_chat)
    #rota,_ = processar_mensagem(reply_chat)
    mapa_de_agentes = {
        0:'router',
        1:'matematico',
        2:'coder'
    }
    find_agente = router(reply)
    agente = mapa_de_agentes.get(find_agente)
    print(agente+ "debug")
    #
    con = sqlite3.connect('users.db')
    cursor = con.cursor()
    cursor.execute(
        "UPDATE chats SET agente = ? WHERE chat_id = ?",(agente, data.chat_id )
    )
    con.commit()
    #

    return {"reply": reply}