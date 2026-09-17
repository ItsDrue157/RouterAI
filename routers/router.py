from typing import Literal
from pydantic import BaseModel
import lmstudio as lms
import json

with open("agents/modelos.json", "r", encoding='utf-8') as arquivo:
    modelos = json.load(arquivo)

class RouterResponse(BaseModel):
    rota: Literal[0, 1, 2, 3]


def router(reply: str):

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
    # teste do erro string indices must be int not ''str''
    print(prompt+'debug')
    print(result.parsed)
    print(type(result.parsed))
    return int(result.parsed["rota"])


def general(reply: str) -> str:
    """
    Executa o agente geral e retorna a resposta completa.
    """
    model = lms.llm("qwen/qwen3-4b-2507")

    resposta = ""

    for fragmento in model.respond_stream(reply):
        resposta += fragmento.content

    return resposta


def router_coding(reply: str) -> str:
    """
    Executa o agente de programação e retorna a resposta completa.
    """
    model = lms.llm("qwen/qwen3-4b-2507")

    resposta = ""

    for fragmento in model.respond_stream(reply):
        resposta += fragmento.content

    return resposta


mapa_de_funcoes = {
    0: general,
    1: router_coding,
    2: router_coding,
}


def processar_mensagem(reply: str) -> tuple[int, str]:
    """
    Recebe a mensagem, descobre a rota, executa o agente
    correspondente e retorna (rota, resposta).
    """
    rota = router(reply)

    funcao = mapa_de_funcoes.get(rota)

    if funcao is None:
        raise ValueError(f"Rota inválida retornada pelo router: {rota}")

    resposta = funcao(reply)

    return rota, resposta
