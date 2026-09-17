# RouterAI

Backend local que recebe uma mensagem, identifica o tipo de tarefa e manda para o agente mais adequado.

O projeto usa modelos pequenos rodando no LM Studio, salva os chats em SQLite e tem scripts para preparar os bancos e iniciar o sistema no Windows.

## Por que esse projeto existe

Eu tenho vários *small language models* (SLMs), com até 12 bilhões de parâmetros, mas meu hardware é limitado. Em vez de usar um modelo grande para fazer tudo, a ideia é ter um único chat que escolhe um modelo menor de acordo com o que eu preciso.

Uma mensagem de programação pode ir para um agente de código, uma conta pode ir para o agente de matemática e uma pergunta comum pode continuar no agente geral. Assim dá para aproveitar melhor os modelos que rodam na minha máquina.

## Features

- Roteamento automático por tipo de mensagem.
- Modelos executados localmente pelo LM Studio.
- Agentes geral, matemático e de programação.
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
| `qwen/qwen3-1.7b` | Roteador que classifica a mensagem. | `routers/router.py` |
| `qwen/qwen3-4b-2507` | Respostas dos agentes geral, matemático e de programação. | `routers/router.py` e `main.py` |

Os IDs dos modelos ainda ficam direto no código e podem ser alterados conforme os modelos disponíveis no LM Studio.

## Estrutura do projeto

```text
RouterAI/
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
│   └── router.py       # Roteamento e execução dos agentes
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

Se outros modelos forem usados, os IDs também precisam ser atualizados em `routers/router.py` e `main.py`.

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

## Personalizar o prompt do roteador

O prompt atual fica na função `router()` em `routers/router.py`. Ele pode ser trocado, mas precisa manter um contrato mínimo para continuar funcionando com o restante da aplicação:

- Conhecer o número e o significado de todas as rotas.
- Escolher apenas uma rota válida.
- Não responder à pergunta do usuário durante a classificação.
- Retornar somente o campo `rota`, no formato esperado pelo `RouterResponse`.
- Manter `{reply}` no ponto em que a mensagem do usuário será inserida.

Template mínimo:

```text
Você é o roteador de uma aplicação com vários agentes.

Classifique a mensagem em uma destas rotas:
0 = geral
1 = matemática
2 = programação
3 = raciocínio

Escolha somente uma rota válida.
Não responda à mensagem do usuário.
Retorne somente o campo "rota" no formato solicitado.

Mensagem:
{reply}
```

A pessoa pode adicionar exemplos, regras e novas categorias, desde que atualize também `RouterResponse`, `mapa_de_funcoes` e `mapa_de_agentes` quando mudar as rotas.

Hoje o prompt fica dentro do código. Uma melhoria futura é mover os prompts para uma pasta `prompts/` ou para um arquivo de configuração. Assim cada pessoa consegue criar os próprios agentes sem editar a lógica da aplicação.

## Estado atual

- Os agentes matemático e de programação ainda usam o mesmo modelo.
- A rota de raciocínio existe na classificação, mas ainda não está ligada a um agente.
- Os modelos, prompts e a URL do LM Studio ainda estão definidos direto no código.
- O frontend gera os IDs de chat localmente, então dois navegadores podem tentar usar o mesmo ID.
- Autenticação e usuários ainda não foram implementados.

## V2 — TODO

- [ ] Permitir trocar de agente no meio de um chat já criado, sem perder o histórico da conversa.
- [ ] Adicionar uma seleção de agente parecida com a troca de modelo do ChatGPT ou Gemini.
- [ ] Criar login e gerenciamento básico de usuários.
- [ ] Vincular cada chat a uma conta.
- [ ] Mostrar o histórico de chats da conta, não apenas as mensagens da conversa atual.
- [ ] Carregar modelos e prompts por configuração, sem precisar alterar o código.
- [ ] Permitir prompts personalizados para novos agentes.

SQLite continua sendo suficiente para a proposta local e para poucos usuários. Se o projeto virar um serviço com muitos acessos simultâneos, aí passa a fazer sentido migrar para PostgreSQL ou outro banco servidor.
