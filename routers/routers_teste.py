"""Roteamento ativo baseado em ``agents/modelos.json``.

O módulo foi mantido separado de ``routers/router.py`` para preservar a
implementação anterior e permitir sua comparação.
"""

import json
from pathlib import Path
from typing import Literal

import lmstudio as lms
from pydantic import BaseModel


BASE_DIR = Path(__file__).resolve().parent.parent
CONFIG_PATH = BASE_DIR / "agents" / "modelos.json"

ROTA_PARA_AGENTE = {
    0: "router",
    1: "matematico",
    2: "coder",
}


class RouterResponse(BaseModel):
    rota: Literal[0, 1, 2, 3]


def _carregar_modelos() -> dict[str, dict[str, str]]:
    """Lê a configuração mais recente dos agentes."""
    with CONFIG_PATH.open("r", encoding="utf-8") as arquivo:
        return json.load(arquivo)


def _obter_configuracao(agente: str) -> dict[str, str]:
    """Retorna e valida a configuração mínima de um agente."""
    modelos = _carregar_modelos()

    if agente not in modelos:
        raise ValueError(
            f"Agente '{agente}' não encontrado em {CONFIG_PATH}."
        )

    configuracao = modelos[agente]
    campos_ausentes = {
        campo
        for campo in ("model", "prompt", "no_think")
        if not configuracao.get(campo)
    }

    if campos_ausentes:
        campos = ", ".join(sorted(campos_ausentes))
        raise ValueError(
            f"Configuração do agente '{agente}' sem os campos: {campos}."
        )

    return configuracao


def _adicionar_comando_final(texto: str, comando: str) -> str:
    """Adiciona o comando final definido na configuração do agente."""
    texto = texto.rstrip()
    comando = comando.strip()
    if not comando or texto.endswith(comando):
        return texto
    return f"{texto}\n\n{comando}"


def _gerar_resposta(reply: str, agente: str, usar_prompt: bool = True) -> str:
    """Gera uma resposta com o modelo configurado para o agente."""
    configuracao = _obter_configuracao(agente)
    model = lms.llm(configuracao["model"])
    comando_final = configuracao["no_think"]

    if usar_prompt:
        conversa = lms.Chat()
        conversa.add_system_prompt(configuracao["prompt"])
        conversa.add_user_message(
            _adicionar_comando_final(reply, comando_final)
        )
        entrada = conversa
    else:
        entrada = _adicionar_comando_final(reply, comando_final)

    resposta = ""
    for fragmento in model.respond_stream(entrada):
        resposta += fragmento.content

    return resposta


def router(reply: str) -> int:
    """Classifica a mensagem com o modelo e o prompt da chave ``router``."""
    configuracao = _obter_configuracao("router")
    model = lms.llm(configuracao["model"])
    prompt = configuracao["prompt"].format(reply=reply)

    result = model.respond(
        prompt,
        response_format=RouterResponse,
        config={
            "temperature": 0,
            "maxTokens": 20,
        },
    )

    if isinstance(result.parsed, RouterResponse):
        return result.parsed.rota

    return RouterResponse(**result.parsed).rota


def general(reply: str) -> str:
    """Responde pela rota geral usando o modelo da chave ``router``."""
    # O prompt da chave router serve apenas para classificação. Por isso, a
    # resposta geral reutiliza o modelo dessa chave, mas não o prompt.
    return _gerar_resposta(reply, "router", usar_prompt=False)


def router_coding(reply: str, agente: str = "coder") -> str:
    """Executa um agente especializado configurado no JSON."""
    if agente not in {"coder", "matematico"}:
        raise ValueError(
            "router_coding aceita apenas os agentes 'coder' e 'matematico'."
        )

    return _gerar_resposta(reply, agente)


def processar_mensagem(reply: str) -> tuple[int, str]:
    """Classifica a mensagem e executa o agente associado à rota."""
    rota = router(reply)
    agente = ROTA_PARA_AGENTE.get(rota)

    if agente is None:
        raise ValueError(
            f"Rota {rota} sem agente correspondente em agents/modelos.json."
        )

    if agente == "router":
        resposta = general(reply)
    else:
        resposta = router_coding(reply, agente)

    return rota, resposta
