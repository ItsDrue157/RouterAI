# RouterAI

Backend local que recebe uma mensagem, identifica o tipo de tarefa e manda para o agente mais adequado.

O projeto usa modelos pequenos rodando no LM Studio, salva os chats em SQLite e tem scripts para preparar os bancos e iniciar o sistema no Windows. O roteador original continua ativo; `routers_teste.py` é uma implementação experimental desconectada.

## Por que esse projeto existe

Eu tenho vários *small language models* (SLMs), com até 12 bilhões de parâmetros, mas meu hardware é limitado. Em vez de usar um modelo grande para fazer tudo, a ideia é ter um único chat que escolhe um modelo menor de acordo com o que eu preciso.

Uma mensagem de programação pode ir para um agente de código, uma conta pode ir para o agente de matemática e uma pergunta comum pode continuar no agente geral. Assim dá para aproveitar melhor os modelos que rodam na minha máquina.

## Features

- Roteamento automático por tipo de mensagem.
- Modelos executados localmente pelo LM Studio.
- Agentes geral, matemático e de programação.
- Modelo e prompt do roteador configuráveis por JSON.
- Modelos e prompts dos agentes especializados configuráveis por JSON.
- Agente selecionado salvo por chat.
- Histórico de mensagens persistido em SQLite.
- Contexto anterior enviado nas próximas mensagens do agente.
- Criação e verificação automática dos bancos.
- Launcher para iniciar backend e frontend.
- API com documentação automática pelo FastAPI.
- CORS configurado para o frontend local.

## Como funciona

1. O frontend envia a mensagem para a API.
2. O modelo roteador classifica a mensagem.
3. A API executa o agente daquela rota.
4. O chat e o agente selecionado são salvos.
5. As mensagens do usuário e do assistente são adicionadas ao histórico.
6. Nas próximas mensagens, o histórico é usado como contexto.

Quando o chat continua no modo geral, ele pode passar novamente pelo roteador. Quando um agente especializado é escolhido, esse agente fica ligado ao chat.

O agente geral também é selecionado automaticamente: quando o modelo roteador retorna a rota `0`, `processar_mensagem()` executa a função `general()`. A chave `router` de `agents/modelos.json` configura tanto o modelo classificador quanto o modelo que gera a resposta geral. O prompt dessa chave é usado somente para a classificação.

## Stack

### Backend

- Python
- FastAPI
- Pydantic
- LM Studio
- LM Studio Python SDK
- OpenAI Python SDK
- SQLite
- Uvicorn
- uv

### Frontend

- HTML
- CSS
- JavaScript
- Marked
- DOMPurify

## Modelos atuais

O código usa estes IDs exatos no LM Studio:

| ID do modelo | Uso | Configurado em |
| --- | --- | --- |
| `qwen/qwen3-1.7b` | Modelo roteador que classifica a mensagem, inclusive para a rota geral. | `agents/modelos.json`, chave `router` |
| `qwen/qwen3-4b-2507` | Respostas dos agentes matemático e de programação. | `agents/modelos.json`, chaves `matematico` e `coder` |

O roteador original carrega seu modelo e prompt da chave `router` de `agents/modelos.json`. Quando ele retorna `0`, o agente geral é chamado automaticamente. As continuações dos agentes especializados consultam suas configurações no JSON; a primeira resposta continua sendo executada pelo fluxo original de `routers/router.py`.

## Estrutura do projeto

```text
RouterAI/
├── agents/
│   └── modelos.json    # Modelos, nomes e prompts dos agentes
├── RouterAI- frontend/ # Interface web
│   ├── vendor/         # Marked e DOMPurify
│   ├── app.js
│   ├── index.html
│   └── styles.css
├── db/
│   ├── __init__.py
│   └── banco.py        # Criação e verificação dos bancos
├── docs/               # Rascunhos e testes
├── routers/
│   ├── router.py        # Implementação ativa original
│   └── routers_teste.py # Implementação experimental desconectada
├── tests/              # Testes locais
├── init_db.bat         # Inicializa somente os bancos
├── main.py             # API e persistência do histórico
├── requirements.txt
├── router.py           # Compatibilidade de importação
├── setup.bat           # Faz a primeira instalação e inicia tudo
├── setup_models.bat    # Baixa os modelos pelo LM Studio CLI
└── start.bat           # Inicia o sistema completo
```

Os arquivos `.db` são locais e ficam fora do Git.

## Backend e frontend

O frontend está dentro do mesmo repositório, na pasta `RouterAI- frontend/`. Isso permite clonar e preparar o sistema inteiro de uma vez.

```text
RouterAI/
├── RouterAI- frontend/
├── main.py
└── start.bat
```

O launcher também reconhece uma pasta chamada `frontend/` e, por compatibilidade, um frontend em uma pasta irmã chamada `RouterAI- frontend/`.

## Requisitos

- Windows
- Git
- Python 3.10 ou mais recente
- LM Studio instalado
- Modelos usados pelo projeto baixados no LM Studio
- Servidor local do LM Studio rodando em `http://localhost:1234`

Não é necessário instalar o `uv` manualmente. O `setup.bat` verifica e instala pelo PyPI quando ele não está disponível.

## LM Studio e modelos

Links oficiais:

- [Baixar o LM Studio](https://lmstudio.ai/download)
- [Qwen3 1.7B](https://lmstudio.ai/models/qwen/qwen3-1.7b), usado como roteador
- [Qwen3 4B Instruct 2507](https://lmstudio.ai/models/qwen/qwen3-4b-2507), usado para gerar as respostas
- [Documentação do comando `lms`](https://lmstudio.ai/docs/cli)

Depois de instalar o LM Studio, abra o aplicativo pelo menos uma vez. Em seguida, os modelos podem ser preparados pelo script opcional:

```powershell
.\setup_models.bat
```

Esse script:

1. Procura o comando `lms` instalado com o LM Studio.
2. Baixa `qwen/qwen3-1.7b`.
3. Baixa `qwen/qwen3-4b-2507`.
4. Tenta iniciar o servidor local na porta `1234`.

O LM Studio pode pedir a escolha de uma quantização durante o download. Essa escolha depende da RAM e da VRAM disponíveis na máquina.

Também é possível fazer isso manualmente:

```powershell
lms get qwen/qwen3-1.7b
lms get qwen/qwen3-4b-2507
lms server start --port 1234
```

Para trocar os modelos do roteador, do agente geral, do agente matemático ou do agente de programação, altere `agents/modelos.json`. O agente geral usa o modelo da chave `router`.

## Instalação em um passo

Depois de preparar o LM Studio e os modelos, execute:

```powershell
git clone <URL_DO_REPOSITORIO> && cd RouterAI && .\setup.bat
```

Se o projeto já estiver clonado:

```powershell
.\setup.bat
```

Na primeira execução, o script:

1. Verifica se o Python está instalado.
2. Instala o `uv` pelo PyPI se ele não estiver disponível.
3. Cria o ambiente virtual `.venv`.
4. Instala os pacotes do `requirements.txt`.
5. Cria ou verifica os bancos SQLite.
6. Inicia a API e o servidor do frontend em janelas separadas.

A primeira configuração precisa de internet para baixar o `uv` e as dependências Python. O script não instala o LM Studio nem baixa os modelos.

Quando terminar, acesse:

- Frontend: `http://127.0.0.1:5000`
- API: `http://127.0.0.1:8000`
- Swagger: `http://127.0.0.1:8000/docs`

## Próximas execuções

Depois que o ambiente estiver configurado, use:

```powershell
.\start.bat
```

O `start.bat` verifica os bancos e inicia backend e frontend sem reinstalar as dependências.

Para encerrar o RouterAI, feche as duas janelas abertas pelos servidores.

## Instalação manual

Se o `setup.bat` não funcionar, a configuração também pode ser feita manualmente.

Crie e ative o ambiente virtual:

```powershell
python -m pip install --user uv
python -m uv venv .venv
.\.venv\Scripts\Activate.ps1
```

Instale as dependências:

```powershell
python -m uv pip install -r requirements.txt
```

Prepare o banco e inicie o sistema:

```powershell
python db\banco.py
.\start.bat
```

## Inicializar somente os bancos

```powershell
.\init_db.bat
```

Também é possível rodar direto pelo Python:

```powershell
python db\banco.py
```

O script pode ser executado mais de uma vez. As tabelas são criadas com `IF NOT EXISTS`.

## Rodar somente o backend

```powershell
.\.venv\Scripts\python.exe -m fastapi dev main.py
```

URLs locais:

- API: `http://127.0.0.1:8000`
- Swagger: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`

## Bancos de dados

O projeto cria dois arquivos dentro de `db/`:

| Arquivo | Tabela | Conteúdo |
| --- | --- | --- |
| `users.db` | `chats` | ID do chat, agente selecionado e data de criação. |
| `messages.db` | `messages` | Mensagens, autor, chat relacionado e data de criação. |

Apesar do nome `users.db`, a versão atual ainda não possui contas de usuário. O login faz parte da V2.

## API Reference

URL base:

```text
http://127.0.0.1:8000
```

As rotas recebem JSON com este formato:

| Campo | Tipo | Descrição |
| --- | --- | --- |
| `chat_id` | `integer` | Identificador do chat. |
| `input` | `string` | Mensagem do usuário. |

### Criar um chat

```http
POST /chat
Content-Type: application/json
```

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

Na primeira mensagem, o roteador escolhe o agente, cria o chat se ele ainda não existir e salva as duas mensagens.

### Continuar um chat

```http
POST /chat/message
Content-Type: application/json
```

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

Essa rota busca o agente do chat, salva a nova mensagem e usa o histórico como contexto quando o chat está com um agente especializado.

## Configurar modelos e prompts

Na V1.1, a configuração do roteador e dos agentes especializados foi organizada em `agents/modelos.json`. O projeto ativo continua usando `routers/router.py`; `routers_teste.py` contém uma alternativa experimental. Cada entrada possui:

| Campo | Descrição |
| --- | --- |
| `name` | Nome do agente mantido como metadado; ainda não é usado pela interface. |
| `model` | ID exato do modelo disponível no LM Studio. |
| `prompt` | Instrução usada pelo agente. |
| `no_think` | Comando final usado para impedir o retorno do raciocínio interno. |

Estrutura resumida:

```json
{
  "router": {
    "name": "router",
    "model": "qwen/qwen3-1.7b",
    "prompt": "Classifique a mensagem: {reply}",
    "no_think": "/no_think"
  },
  "coder": {
    "name": "coder",
    "model": "qwen/qwen3-4b-2507",
    "prompt": "You are a great coding teacher",
    "no_think": "/no_think"
  },
  "matematico": {
    "name": "matemático",
    "model": "qwen/qwen3-4b-2507",
    "prompt": "You are a great coding teacher",
    "no_think": "/no_think"
  }
}
```

As chaves `router`, `coder` e `matematico` são identificadores usados pela aplicação e não devem ser renomeadas sem atualizar o código. A chave `router` fornece o modelo classificador e o modelo da resposta geral. Seu prompt é usado somente na classificação e precisa manter `{reply}`, que é substituído pela mensagem recebida. O campo `no_think` define o comando enviado ao modelo em todas as respostas.

No fluxo ativo, o roteador lê sua configuração ao ser carregado e `main.py` consulta o arquivo nas continuações com `coder` ou `matematico`. A implementação experimental consulta o arquivo a cada chamada e não está conectada à API.

O prompt do roteador também precisa manter um contrato mínimo:

- Conhecer o número e o significado de todas as rotas.
- Escolher apenas uma rota válida.
- Não responder à pergunta do usuário durante a classificação.
- Retornar somente o campo `rota`, no formato esperado pelo `RouterResponse`.

É possível adicionar exemplos, regras e novas categorias ao prompt. Se as rotas forem alteradas, também será necessário atualizar `RouterResponse`, `ROTA_PARA_AGENTE` e `mapa_de_agentes` no código.

## Estado atual

- Os agentes matemático e de programação ainda usam o mesmo modelo.
- A rota de raciocínio existe na classificação, mas ainda não está ligada a um agente.
- O roteador original está ativo; `routers_teste.py` permanece desconectado para análise.
- As continuações dos agentes especializados carregam seus modelos e prompts do JSON.
- A URL do LM Studio ainda está definida diretamente no código.
- O frontend gera os IDs de chat localmente, então dois navegadores podem tentar usar o mesmo ID.
- Autenticação e usuários ainda não foram implementados.

## V2 — TODO

- [ ] Permitir trocar de agente no meio de um chat já criado, sem perder o histórico da conversa.
- [ ] Adicionar uma seleção de agente parecida com a troca de modelo do ChatGPT ou Gemini.
- [ ] Criar login e gerenciamento básico de usuários.
- [ ] Vincular cada chat a uma conta.
- [ ] Mostrar o histórico de chats da conta, não apenas as mensagens da conversa atual.
- [ ] Integrar a implementação experimental baseada em JSON após revisão.
- [ ] Mover a URL do LM Studio para o arquivo de configuração.
- [ ] Permitir prompts personalizados para novos agentes.
- [ ] Exibir os modelos disponíveis com um indicador de desempenho (verde, laranja ou vermelho), inicialmente estimado e futuramente baseado em benchmarks executados na máquina do usuário.
- [ ] Permitir usar uma API de IA externa como modelo, com suporte à seleção manual e a fallback quando um modelo local não estiver disponível ou não for adequado.
- [ ] Calcular dinamicamente o orçamento de contexto conforme o limite do modelo selecionado, sem depender de um modelo predefinido no LM Studio, e enviar apenas a parte relevante do histórico tanto para modelos locais quanto para APIs externas.

SQLite continua sendo suficiente para a proposta local e para poucos usuários. Se o projeto virar um serviço com muitos acessos simultâneos, aí passa a fazer sentido migrar para PostgreSQL ou outro banco servidor.
