import sqlite3  # Banco de dados local (histórico e chats)
from pathlib import Path  # Resolução dos caminhos dos bancos
from fastapi import FastAPI  # Criação e rotas da API
from fastapi.middleware.cors import CORSMiddleware  # Libera requisições do frontend (CORS)
from pydantic import BaseModel  # Validação dos dados da requisição (ChatRequest)
from openai import OpenAI  # Conexão com os modelos no LM Studio
from routers.router import processar_mensagem  # Roteamento de mensagens e agentes

# Caminhos dos bancos de dados dentro da pasta db/
BASE_DIR = Path(__file__).resolve().parent
DB_USERS = BASE_DIR / "db" / "users.db"
DB_MESSAGES = BASE_DIR / "db" / "messages.db"

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



def buscar_historico(chat_id)-> list:
    """
        busca na tabela messages as mensagem com o parametro chat_id
    """
    con = sqlite3.connect(DB_MESSAGES)
    cursor = con.cursor()

    with con:
        cursor.execute("SELECT role, content FROM messages WHERE chat_id=? ORDER BY id", (chat_id,))
        historico = cursor.fetchall()
    return historico

def montar_historico(historico):
    messages = []
    
    for role, content in historico:
        messages.append({'role':role, 'content':content})
    return messages

def enviar_modelo(agente,chat_id ):
    client = OpenAI(base_url="http://localhost:1234/v1", api_key="lm-studio")

    mapa_de_modelos = {
        'coder':'qwen/qwen3-4b-2507',
        'matematico':'qwen/qwen3-4b-2507'
    }
    model_id = mapa_de_modelos.get(agente)
    contexto = montar_historico(buscar_historico(chat_id))
    playload = client.chat.completions.create(
        model=model_id,
        messages=contexto, 
        temperature=0.7
    )

    return playload.choices[0].message.content.strip()

    

def salvar_mensagem(chat_id, role, content):


    con = sqlite3.connect(DB_MESSAGES)
    cursor = con.cursor()

    #salva automaticamente, se n tiver erro
    with con:
        cursor.execute("INSERT INTO messages (chat_id, role, content) VALUES (?,?,?)", (chat_id, role,content))
        return True






@app.post("/chat")
def create_new_chat(data: ChatRequest):
    reply_chat = data.input

    con = sqlite3.connect(DB_USERS)
    cursor = con.cursor()

    with con:
        # se n tiver vai gerar none
        cursor.execute(
            "SELECT chat_id FROM chats WHERE chat_id = ?",
            (data.chat_id,)
        )
        chat = cursor.fetchone()

    mapa_de_agentes = {
        0: 'router',
        1: 'matematico',
        2: 'coder'
    }

    rota, reply = processar_mensagem(reply_chat)

    agente = mapa_de_agentes.get(rota)
    print(agente + "debug")

    # colocando o id no banco
    if chat is None:
        cursor.execute(
            "INSERT INTO chats (chat_id, agente) VALUES (?, ?)",
            (data.chat_id, agente)
        )
        con.commit()

    # role hardcoded
    salvar_mensagem(
        chat_id=data.chat_id,
        role='user',
        content=reply_chat
    )

    # role hardcoded
    salvar_mensagem(
        chat_id=data.chat_id,
        role='assistant',
        content=reply
    )

    return {
        "chat_id": data.chat_id,
        "reply": reply
    }




@app.post("/chat/message")
def read_message(data: ChatRequest):
    reply_chat =data.input
    chat_id = data.chat_id
    con = sqlite3.connect(DB_USERS)
    cursor = con.cursor()

    with con:
        cursor.execute("SELECT agente from chats WHERE chat_id=?",(data.chat_id,))
        agente = cursor.fetchone()
        agente = agente[0]
        
    print(agente+'debuggggggg')

    if agente =='router':
        mapa_de_agentes = {
                0: 'router',
                1: 'matematico',
                2: 'coder'
            }
        rota, reply = processar_mensagem(reply_chat)

        print("ROTA RETORNADA:", rota)
        print("TIPO DA ROTA:", type(rota))

        agente = mapa_de_agentes.get(rota)

        print("AGENTE NOVO:", agente)

        if agente != 'router':
            with con:
                cursor.execute('UPDATE chats SET agente=? WHERE chat_id=?',(agente,chat_id))
        salvar_mensagem(chat_id=data.chat_id, role='user',      content=reply_chat)
        salvar_mensagem(chat_id=data.chat_id, role='assistant', content=reply)
        return {"reply": reply}
    else:
        match agente:
            case 'coder':
                salvar_mensagem(chat_id=data.chat_id, role='user',      content=reply_chat)
                reply = enviar_modelo(agente,chat_id)
                salvar_mensagem(chat_id=data.chat_id, role='assistant', content=reply)
                return {"reply": reply}
            
            case 'matematico':
                salvar_mensagem(chat_id=data.chat_id, role='user',      content=reply_chat)
                reply = enviar_modelo(agente,chat_id)
                salvar_mensagem(chat_id=data.chat_id, role='assistant', content=reply)
                return {"reply": reply}
