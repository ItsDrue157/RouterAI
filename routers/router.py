from pydantic import BaseModel
from os.path  import join, dirname
from typing   import Literal
from dotenv   import load_dotenv
from openai   import OpenAI
import json
import os

#CARREGAR O .ENV
dotenv_path = join(dirname(dirname(__file__)), '.env')
load_dotenv(dotenv_path)

#VARIAVEIS NO .ENV
base_url = os.getenv("base_url")
api_key  = os.getenv("api_key")


with open("agents/modelos.json", "r", encoding='utf-8') as arquivo:
    modelos = json.load(arquivo)

class RouterResponse(BaseModel):
    rota: Literal[0, 1, 2]


def router(reply: str) -> str:
    """Classifica a mensagem e retorna o nome do agente correspondente."""
    client = OpenAI(base_url=base_url, api_key=api_key)

    model = modelos['router']['model']

    prompt_base = modelos["router"]["prompt"]
    prompt = prompt_base.format(reply=reply)

    result = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": "RouterResponse",
                "schema": RouterResponse.model_json_schema(),
            },
        },
        temperature=0,
        max_tokens=20,
    )

    _modelos = {
        0:"general",
        1:"matematico",
        2:"coder"
    }
    rota = RouterResponse.model_validate_json(result.choices[0].message.content).rota
    modelo = _modelos.get(rota)

    return modelo
