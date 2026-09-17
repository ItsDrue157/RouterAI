# RouterAI

Front-end leve em HTML, CSS e JavaScript, sem frameworks, fontes externas ou instalação de pacotes.

## Abrir

Na pasta destes arquivos, inicie um servidor estático, por exemplo:

```sh
python -m http.server 5500 --bind 127.0.0.1
```

Abra http://127.0.0.1:5500 e mantenha seu backend rodando. Também é possível abrir `index.html` diretamente, mas alguns backends bloqueiam requisições de páginas `file://`; prefira o servidor local.

## Conectar ao backend

No início de `app.js`, altere:

```js
const API_CONFIG = {
  baseUrl: "http://127.0.0.1:8000",
  createChatPath: "/chat",
  sendMessagePath: "/chat/message",
  timeoutMs: 60000,
};
```

As duas rotas usam **POST**. O mesmo botão Enviar escolhe a rota automaticamente:

| Situação | Rota | Corpo JSON |
| --- | --- | --- |
| Primeira mensagem do primeiro chat | `/chat` | `{ "chat_id": 1, "input": "Olá!" }` |
| Próxima mensagem nesse chat | `/chat/message` | `{ "chat_id": 1, "input": "Me ajuda com um código?" }` |
| Primeira mensagem após Nova conversa | `/chat` | `{ "chat_id": 2, "input": "Outra dúvida" }` |

Resposta esperada em ambas as rotas:

```json
{ "chat_id": 1, "reply": "Olá! Como posso ajudar?" }
```

O backend pode omitir `chat_id` na resposta. Se retornar esse campo, ele deve corresponder ao ID enviado. O front aceita `reply`, `response`, `output` ou `text` como texto da resposta. Para outros nomes ou respostas aninhadas, ajuste `readApiResponse()`. Para mudar corpo, cabeçalhos, autenticação ou método, ajuste `requestReply()`.

Se front e backend estiverem em origens diferentes, configure o **CORS no backend** para permitir `http://127.0.0.1:5500`, método `POST` e cabeçalho `Content-Type`, incluindo a resposta ao preflight `OPTIONS`. Se abrir por `localhost`, permita essa origem também.

## IDs e criação do chat

O primeiro ID é reservado antes da primeira mensagem, começando em 1. Cada clique em **Nova conversa** reserva e incrementa o próximo número: 2, 3 etc. As mensagens de uma mesma conversa reutilizam esse ID.

O último número fica em `localStorage` na chave `routerai.lastChatId.v1`, sobrevivendo a atualizações e novas visitas na mesma origem do navegador. O front usa Web Locks, quando disponíveis, para coordenar a reserva entre abas; em navegadores sem esse recurso, use uma aba por vez. O armazenamento local deve estar habilitado para reservar IDs.

Este é um contador **para testes locais**, não uma sequência global: outro navegador, outra origem (como trocar `localhost` por `127.0.0.1`) ou limpar os dados pode reiniciar a numeração e causar conflitos com chats existentes no backend. Se o backend já tiver IDs numéricos, alinhe o contador local ao maior ID existente antes de criar chats.

Para vários usuários, o banco deve gerar o ID incremental. Se a primeira mensagem precisa já incluir esse ID, o fluxo recomendado é reservar o chat antes, por exemplo `POST /chats` retornando `{ "chat_id": 42 }`, e então enviar `{ "chat_id": 42, "input": "Olá" }` para `/chat`. Essa reserva no backend ainda não está implementada neste front.

O front monta explicitamente o corpo de todas as chamadas como `JSON.stringify({ chat_id, input })`. No console do navegador, o log `[RouterAI] Enviando mensagem` mostra a URL e o corpo enviado. Ele só troca para `/chat/message` depois de uma resposta de criação bem-sucedida. Em erro de conexão ou HTTP, conserva o ID e continua usando `/chat` na tentativa seguinte. Em caso de timeout, a criação pode ter ocorrido no servidor: o backend deve tratar uma repetição de criação com o mesmo ID sem duplicar o chat nem sobrescrever outro chat. O ID não substitui autenticação ou autorização.

## Comportamento

- A página sempre abre no modo escuro, inclusive ao atualizar. O botão de lua/sol no topo permite alternar para claro durante o uso. `theme.js` cuida da alternância, e a paleta escura fica em `styles.css`.
- Enter envia; Shift + Enter insere uma linha. As sugestões apenas preenchem o campo.
- Durante a resposta, aparece um indicador de carregamento e os controles de envio ficam bloqueados.
- Histórico e `chat_id` ficam em `sessionStorage`, sobrevivendo à atualização da página na mesma aba. Não existe uma lista permanente de conversas.
- “Nova conversa” limpa o histórico local e faz a próxima mensagem criar outro chat. Não exclui dados no backend.
- As respostas da IA exibem Markdown: negrito, itálico, riscado, títulos, listas, links, citações, código e tabelas. O histórico salvo também recebe a formatação ao recarregar. As mensagens do usuário continuam em texto simples.
- Erros aparecem na página e o texto volta ao campo. Não há reenvio automático: após um timeout, o backend pode já ter recebido a mensagem.
- O backend continua responsável por persistir o chat, associar o agente ao `chat_id` e recuperar o contexto.

Os endpoints são um contrato de integração proposto; ajuste-os à API real. Nenhuma resposta é simulada no aplicativo.

## Formatação das respostas

O backend continua retornando uma string no campo `reply`, por exemplo:

```json
{ "chat_id": 1, "reply": "**Olá!** Posso ajudar com:\n\n- Python\n- JavaScript" }
```

`markdown.js` usa [Marked](https://marked.js.org/) 17.0.5 e [DOMPurify](https://github.com/cure53/DOMPurify) 3.4.15, incluídos na pasta `vendor` com suas licenças. As bibliotecas são locais: não há CDN nem instalação de pacotes. Mantenha essa pasta junto aos demais arquivos ao copiar o site.

HTML literal é exibido como texto. O resultado do Markdown passa por sanitização antes de entrar na página; links aceitam HTTP, HTTPS e e-mail, e imagens aparecem apenas como descrição. Blocos de código preservam a indentação e tabelas largas têm rolagem horizontal. Se alguma biblioteca não carregar, a resposta continua aparecendo como texto simples.
