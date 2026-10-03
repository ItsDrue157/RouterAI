import sqlite3  # Banco de dados local (histórico e chats)
from pathlib import Path  # Resolução dos caminhos dos bancos
from fastapi import FastAPI, HTTPException  # Criação e rotas da API
from fastapi.middleware.cors import CORSMiddleware  # Libera requisições do frontend (CORS)
from pydantic import BaseModel  # Validação dos dados da requisição (ChatRequest)
from openai import OpenAI  # Conexão com os modelos no LM Studio
from dotenv import load_dotenv
from routers.router import router  # Roteamento e execução dos agentes, precisa ser antes pois deu erro de api :)
import json
import logging
import os
import openai
#


BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

#VARIAVEIS NO .ENV
base_url = os.getenv("base_url")
api_key  = os.getenv("api_key")

# Caminhos dos bancos de dados dentro da pasta db/
DB_USERS = BASE_DIR / "db" / "users.db"
DB_MESSAGES = BASE_DIR / "db" / "messages.db"
LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

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
        logging.FileHandler(LOG_DIR / "routerai.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)
logging.getLogger("watchfiles.main").setLevel(logging.WARNING)

log = logging.getLogger(__name__)


class ChatRequest(BaseModel):
    chat_id: int
    input: str
    modelo: str | None = None


def buscar_modelo_padrao(agente):
    with open("agents/modelos.json", "r", encoding="utf-8") as arquivo:
        modelos = json.load(arquivo)

    modelo = modelos[agente]['model']

    return modelo




def buscar_historico(chat_id) -> list:
    """
        busca na tabela messages as mensagens com o identificador: chat_id
    """
    con = sqlite3.connect(DB_MESSAGES)
    cursor = con.cursor()

    with con:
        cursor.execute("SELECT role, content FROM messages WHERE chat_id=? ORDER BY id", (chat_id,))
        historico = cursor.fetchall()
    log.info(f'O historico do {chat_id}, foi encontrado com sucesso.')
    return historico

def montar_historico(historico):
    """Converte as mensagens do banco em uma lista para enviar ao modelo."""
    messages = []
    for role, content in historico:
        messages.append({'role':role, 'content':content})
    
    return messages




def enviar_modelo(agente,chat_id, modelo):
    """Envia o histórico do chat ao modelo do agente e retorna a resposta."""
    client = OpenAI(base_url=base_url, api_key=api_key)
    with open ("agents/modelos.json","r", encoding="utf-8") as arquivo:
        modelos = json.load(arquivo)

    #model_id = modelos[agente]['model']
    contexto = montar_historico(buscar_historico(chat_id))
    
    contexto.insert(0,{
        "role":"system",
        "content":modelos[agente]['prompt']
    })

    payload = client.chat.completions.create(
        model=modelo,
        messages=contexto, 
        temperature=0.7,
        timeout=180
    )

    return payload.choices[0].message.content.strip()

    

def salvar_mensagem(chat_id, role, content):
    """Salva uma mensagem do usuário ou do assistente no histórico do chat."""
    con = sqlite3.connect(DB_MESSAGES)
    cursor = con.cursor()

    #salva automaticamente, se n tiver erro
    with con:
        cursor.execute("INSERT INTO messages (chat_id, role, content) VALUES (?,?,?)", (chat_id, role,content))
        return True






@app.post("/chat")
def create_new_chat(data: ChatRequest):
    """Cria o chat se necessário, escolhe o agente e responde à primeira mensagem."""
    input_chat = data.input
    chat_id = data.chat_id
    

    con = sqlite3.connect(DB_USERS)
    cursor = con.cursor()

    # se n tiver vai gerar none
    with con:
        cursor.execute(
            "SELECT chat_id FROM chats WHERE chat_id = ?",
            (chat_id,)
        )
        chat = cursor.fetchone()

    # buscar o agente 
    agente = router(input_chat)
    log.info(f'o agente: {agente} foi escolhido para o chat_id: {chat_id}')


    modelo = buscar_modelo_padrao(agente)
    if data.modelo is not None:
        modelo = data.modelo

    
    # colocando o id no banco
    if chat is None:
        cursor.execute(
            "INSERT INTO chats (chat_id, agente, modelo) VALUES (?, ?, ?)",
            (chat_id, agente, modelo),
        )
        con.commit()
    log.info(f'o {chat_id}, o agente: {agente}, e o modelo: {modelo}, foram adicionados na tabema chats com sucesso.')



    # mensagem de resposta do usuario hardcoded
    salvar_mensagem(
        chat_id=chat_id,
        role='user',
        content=input_chat
    )

    #resposta a ser enviada ao usuario
    reply = enviar_modelo(agente, chat_id, modelo)
    
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
    """Responde a uma nova mensagem usando o agente associado ao chat."""
    input_chat =data.input
    chat_id = data.chat_id

    con = sqlite3.connect(DB_USERS)
    cursor = con.cursor()

    #verificar se o chat_id existe no banco
    try:
        with con:
                cursor.execute("SELECT agente, modelo from chats WHERE chat_id=?",(chat_id,))
                agente = cursor.fetchone()

                if agente is None:
                    log.error(f'A consulta do agente para o chat_id: {chat_id}, não obteve resultado.')
                    raise HTTPException(status_code=404, detail="chat não encontrado")
                #desempacota o agente q é uma tupla
                agente, modelo = agente

        log.info(f'o agente: {agente} e o modelo: {modelo} foram escolhidos para o chat_id: {chat_id}')

    

    except sqlite3.Error as e:
        log.error(f'Error a consultar o sqlite para o chat_id: {chat_id}, error: {e}')
        raise e

    if data.modelo is not None and data.modelo != modelo:
            modelo = data.modelo
            with con:
                cursor.execute("UPDATE chats SET modelo=? WHERE chat_id=?",(modelo, chat_id))
                
    


    if agente == 'general':
        
        agente_novo = router(input_chat)

        log.info(f'Novo agente: {agente_novo}, do chat: {chat_id}.')

        if agente_novo != 'general':
            with con:
                cursor.execute('UPDATE chats SET agente=? WHERE chat_id=?',(agente_novo, chat_id))

        salvar_mensagem(chat_id=chat_id, role='user',              content=input_chat)

        reply = enviar_modelo(agente_novo, chat_id, modelo)

        salvar_mensagem(chat_id=chat_id, role='assistant',         content=reply)

        return {"reply": reply}
    
    else:
        match agente:
            case 'coder':
                salvar_mensagem(chat_id=chat_id, role='user',      content=input_chat)
                reply = enviar_modelo(agente, chat_id, modelo)
                salvar_mensagem(chat_id=chat_id, role='assistant', content=reply)
                return {"reply": reply}
            
            case 'matematico':
                salvar_mensagem(chat_id=chat_id, role='user',      content=input_chat)
                reply = enviar_modelo(agente, chat_id, modelo)
                salvar_mensagem(chat_id=chat_id, role='assistant', content=reply)
                return {"reply": reply}
            
            case 'general':
                salvar_mensagem(chat_id=chat_id, role='user',      content=input_chat)
                reply = enviar_modelo(agente, chat_id, modelo)
                salvar_mensagem(chat_id=chat_id, role='assistant', content=reply)
                return {"reply":reply}


@app.get("/models")
def get_models():
    """Lista os modelos disponíveis no servidor configurado."""
    client = OpenAI(base_url=base_url, api_key=api_key)

    modelos = client.models.list()

    return {
        "models": [
            modelo.id for modelo in modelos.data 
        ]
    }
