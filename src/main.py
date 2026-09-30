import sqlite3  # Banco de dados local (histórico e chats)
from pathlib import Path  # Resolução dos caminhos dos bancos
from fastapi import FastAPI  # Criação e rotas da API
from fastapi.middleware.cors import CORSMiddleware  # Libera requisições do frontend (CORS)
from pydantic import BaseModel  # Validação dos dados da requisição (ChatRequest)
from openai import OpenAI  # Conexão com os modelos no LM Studio
from routers.router import router  # Roteamento e execução dos agentes
from os.path import join, dirname
from dotenv import load_dotenv
import json
import logging
import os
#


dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

#VARIAVEIS NO .ENV
base_url = os.getenv("base_url")
api_key  = os.getenv("api_key")

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

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    handlers=[
        logging.FileHandler("logs/routerai.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)
logging.getLogger("watchfiles.main").setLevel(logging.WARNING)

log = logging.getLogger(__name__)


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
    log.info(f'O historico do {chat_id}, foi encontrado com sucesso.')
    return historico

def montar_historico(historico):
    messages = []
    for role, content in historico:
        messages.append({'role':role, 'content':content})
    
    return messages




def enviar_modelo(agente,chat_id ):
    client = OpenAI(base_url=base_url, api_key=api_key)
    with open ("agents/modelos.json","r", encoding="utf-8") as arquivo:
        modelos = json.load(arquivo)

    model_id = modelos[agente]['model']
    contexto = montar_historico(buscar_historico(chat_id))
    
    contexto.insert(0,{
        "role":"system",
        "content":modelos[agente]['prompt']
    })

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
    input_chat = data.input
    chat_id = data.chat_id

    con = sqlite3.connect(DB_USERS)
    cursor = con.cursor()

    with con:
        # se n tiver vai gerar none
        cursor.execute(
            "SELECT chat_id FROM chats WHERE chat_id = ?",
            (chat_id,)
        )
        chat = cursor.fetchone()

    # buscar o agente 
    agente = router(input_chat)
    log.info(f'o agente: {agente}, foi escolhido para o chat_id: {chat_id}')
    
    
    # colocando o id no banco
    if chat is None:
        cursor.execute(
            "INSERT INTO chats (chat_id, agente) VALUES (?, ?)",
            (chat_id, agente),

        )
        con.commit()
    log.info(f'o {chat_id} foi adiciona ao banco de dados chats com sucesso.')


    # mensagem de resposta do usuario hardcoded
    salvar_mensagem(
        chat_id=chat_id,
        role='user',
        content=input_chat
    )

    #resposta a ser enviada ao usuario
    reply = enviar_modelo(agente, chat_id)
    
    # mensagem de resposta da ia hardcoded
    salvar_mensagem(
        chat_id=chat_id,
        role='assistant',
        content=reply
    )

    #enviando a resposta ao usuario
    return {
        "chat_id": chat_id,
        "reply": reply
    }




@app.post("/chat/message")
def read_message(data: ChatRequest):
    input_chat =data.input
    chat_id = data.chat_id
    con = sqlite3.connect(DB_USERS)
    cursor = con.cursor()

    with con:
        cursor.execute("SELECT agente from chats WHERE chat_id=?",(chat_id,))
        agente = cursor.fetchone()
        agente = agente[0]
        
    log.info(f'o agente: {agente}, foi escolhido para o chat_id: {chat_id}')

    if agente == 'router':
        
        agente_novo = router(input_chat)


    
        log.info(f'Novo agente: {agente_novo}, do chat: {chat_id}.')

        if agente != 'router':
            with con:
                cursor.execute('UPDATE chats SET agente=? WHERE chat_id=?',(agente_novo,chat_id))

        salvar_mensagem(chat_id=chat_id, role='user',              content=input_chat)

        reply = enviar_modelo(agente_novo, chat_id)

        salvar_mensagem(chat_id=chat_id, role='assistant',         content=reply)

        return {"reply": reply}
    
    else:
        match agente:
            case 'coder':
                salvar_mensagem(chat_id=chat_id, role='user',      content=input_chat)
                reply = enviar_modelo(agente,chat_id)
                salvar_mensagem(chat_id=chat_id, role='assistant', content=reply)
                return {"reply": reply}
            
            case 'matematico':
                salvar_mensagem(chat_id=chat_id, role='user',      content=input_chat)
                reply = enviar_modelo(agente,chat_id)
                salvar_mensagem(chat_id=chat_id, role='assistant', content=reply)
                return {"reply": reply}
            case 'general':
                salvar_mensagem(chat_id=chat_id, role='user',      content=input_chat)
                reply = enviar_modelo(agente,chat_id)
                salvar_mensagem(chat_id=chat_id,role='user', content=reply)
                return {"reply":reply}
