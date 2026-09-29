from typing import Literal
from pydantic import BaseModel
import lmstudio as lms
import json

with open("agents/modelos.json", "r", encoding='utf-8') as arquivo:
    modelos = json.load(arquivo)

class RouterResponse(BaseModel):
    rota: Literal[0, 1, 2]


def router(reply: str) -> str:

    model = lms.llm(modelos['router']['model'])

    prompt_base = modelos["router"]["prompt"]
    prompt = prompt_base.format(reply=reply)

    result = model.respond(
        prompt,
        response_format=RouterResponse,
        config={
            "temperature": 0,
            "maxTokens": 20
        }
    )

    _modelos = {
        0:"general",
        1:"matematico",
        2:"coder"
    }
    modelo = _modelos.get(result.parsed["rota"])

    return modelo
