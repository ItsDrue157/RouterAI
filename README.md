# RouterAI

RouterAI é um chat de IA que identifica o tipo de tarefa e direciona a mensagem para um agente geral, de matemática ou de programação.

O projeto nasceu da ideia de aproveitar modelos de linguagem pequenos (SLMs) em hardware limitado. O propósito é reunir esses modelos em uma única interface e escolher o agente adequado para cada tarefa.

## Features

- Roteamento automático entre agentes.
- Conversas com histórico usado como contexto.
- Interface de chat com respostas em Markdown.
- Lista de modelos disponíveis no servidor de IA.

## Stack utilizada

- **Backend:** Python, FastAPI, Pydantic, Uvicorn e SDKs OpenAI e LM Studio.
- **Frontend:** HTML, CSS, JavaScript, Marked e DOMPurify.

## Como funciona

1. Você envia uma mensagem pelo chat.
2. O roteador identifica a tarefa e escolhe o agente.
3. O agente gera a resposta usando seu modelo e prompt.
4. As próximas mensagens continuam com o agente escolhido e o histórico da conversa.

## Requisitos

- Windows, Git e Python 3.10 ou superior.
- Um launcher de LLM com servidor compatível com a API da OpenAI e os modelos do projeto disponíveis.
- Endpoint e chave de acesso definidos em `.env`, seguindo o exemplo de `.env.example`.

A geração de respostas usa a API compatível com OpenAI; o roteador atual ainda depende do SDK do LM Studio até a reestruturação do core.

## Como executar

Clone o repositório e execute a configuração inicial:

```powershell
git clone https://github.com/ItsDrue157/RouterAI.git
cd RouterAI
.\setup.bat
```

Nas próximas execuções:

```powershell
.\start.bat
```

Abra o chat em [http://127.0.0.1:5000](http://127.0.0.1:5000).

## API Reference

URL base: `http://127.0.0.1:8000`. Documentação interativa em [`/docs`](http://127.0.0.1:8000/docs).

As rotas de chat recebem JSON com estes campos:

| Campo | Tipo | Descrição |
| --- | --- | --- |
| `chat_id` | `integer` | Identificador do chat. |
| `input` | `string` | Mensagem do usuário. |

### Criar um chat — `POST /chat`

Escolhe o agente e gera a primeira resposta.

Requisição (`Content-Type: application/json`):

```json
{
  "chat_id": 1,
  "input": "Como faço uma API em Python?"
}
```

Resposta:

```json
{
  "chat_id": 1,
  "reply": "Resposta gerada pelo agente"
}
```

### Continuar um chat — `POST /chat/message`

Envia uma nova mensagem para um chat existente, usando o histórico como contexto.

Requisição (`Content-Type: application/json`):

```json
{
  "chat_id": 1,
  "input": "Agora adiciona uma rota de login"
}
```

Resposta:

```json
{
  "reply": "Resposta gerada pelo agente"
}
```

### Listar modelos — `GET /models`

Retorna os IDs dos modelos disponibilizados pelo servidor de IA.

```json
{
  "models": ["id-do-modelo"]
}
```

## V2

- [x] ✅ Criar o seletor visual de modelos na interface.
- [x] ✅ Mover o endpoint e a chave de API para o `.env`.
- [ ] Usar o modelo selecionado na geração das respostas.
- [ ] Criar login e vincular chats e histórico a cada conta.
- [ ] Reestruturar o core e integrar o novo fluxo de roteamento.
- [ ] Permitir prompts personalizados para novos agentes.
- [ ] Exibir indicadores de desempenho dos modelos com benchmarks locais.
- [ ] Validar APIs externas e adicionar fallback entre modelos.
- [ ] Ajustar o contexto ao limite de cada modelo e selecionar o histórico relevante.
