# Frontend do RouterAI

Interface em HTML, CSS e JavaScript, sem frameworks ou build. Marked e DOMPurify são vendorizados; não há dependência de CDN.

## Abrir

Na raiz do projeto, `start.bat` inicia a API na porta 8000 e o frontend na porta 5000.

Para servir somente esta pasta:

```sh
python -m http.server 5500 --bind 127.0.0.1
```

Abra [http://127.0.0.1:5500](http://127.0.0.1:5500) e mantenha a API rodando. Use um servidor HTTP para evitar problemas de origem ao abrir arquivos diretamente.

## Conectar ao backend

A configuração está no início de `app.js`:

```javascript
const API_CONFIG = {
  baseUrl: "http://127.0.0.1:8000",
  createChatPath: "/chat",
  sendMessagePath: "/chat/message",
  modelsPath: "/models",
  modelsTimeoutMs: 10000,
  timeoutMs: 180000,
};
```

O backend permite origens `localhost` e `127.0.0.1` nas portas 5000 e 5500. Mudanças na porta de serviço do frontend precisam ser alinhadas ao CORS.

As duas rotas de chat usam POST com `Content-Type: application/json`:

| Situação | Rota | Corpo JSON |
| --- | --- | --- |
| Primeira mensagem | `/chat` | `{ "chat_id": 1, "input": "Olá!", "modelo": null }` |
| Continuação com escolha | `/chat/message` | `{ "chat_id": 1, "input": "Outra pergunta", "modelo": "id-do-modelo" }` |
| Nova conversa | `/chat` | `{ "chat_id": 2, "input": "Outra dúvida", "modelo": null }` |

O frontend envia a seleção atual em cada mensagem. Na criação, `null` usa o modelo padrão do agente; na continuação, mantém o salvo. O backend conserva o agente como origem do prompt e salva o modelo de resposta separadamente.

A criação retorna `{ "chat_id": 1, "reply": "Resposta" }`; a continuação retorna `{ "reply": "Resposta" }`. O frontend também aceita `response`, `output` ou `text` como texto da resposta. Se houver `chat_id` na resposta, ele deve corresponder ao enviado.

## Seleção e cache de modelos

`models.js` consulta o endpoint `GET /models`, que já está implementado:

```json
{
  "models": ["qwen/qwen3-1.7b", "qwen/qwen3-4b-2507"]
}
```

- A primeira abertura busca a lista e a guarda em memória.
- As próximas aberturas reutilizam o cache, inclusive uma lista vazia.
- **Atualizar lista** força uma consulta; recarregar a página limpa o cache.
- IDs duplicados são removidos, preservando a ordem.
- Uma falha na atualização mantém a última lista disponível e mostra o erro.
- Sem uma consulta bem-sucedida, a próxima abertura tenta novamente.
- Uma mudança na lista não apaga automaticamente a seleção da conversa.

Selecionar marca a opção e atualiza o botão; a troca no backend acontece junto da próxima mensagem. O seletor fica bloqueado durante o envio. **Nova conversa** limpa seleção, marcações e histórico local e fecha o menu.

A lista é uma fotografia dos modelos disponíveis no momento da consulta; use **Atualizar lista** quando adicionar ou remover modelos no servidor.

## Restauração da conversa e do modelo

`selectedModel` guarda a escolha para o próximo envio. `state.modelo` guarda o modelo confirmado, persistido em `sessionStorage`.

Selecionar B enquanto a conversa usa A não salva B como modelo confirmado. Se a página for recarregada antes do envio, o menu restaura A.

Após sucesso, o frontend usa o campo `modelo` da resposta quando disponível. Por compatibilidade com a API atual, também confirma uma escolha explícita enviada quando a requisição tem sucesso. Escolhas confirmadas sobrevivem à recarga na mesma aba.

**Limitação atual:** a API ainda não devolve `modelo`. Por isso, o frontend não descobre o padrão escolhido pelo agente nem confirma uma troca salva quando a geração falha. Após uma falha, a seleção permanece na página para nova tentativa, mas uma recarga pode restaurar o último modelo confirmado anteriormente.

### Contrato já suportado, ainda pendente no backend

Para confirmar o modelo em sucesso, o frontend aceita, por exemplo:

```json
{
  "chat_id": 1,
  "reply": "Resposta",
  "modelo": "id-do-modelo-salvo"
}
```

Para uma falha de geração após salvar a escolha, aceita erro HTTP com:

```json
{
  "detail": {
    "chat_id": 1,
    "modelo": "id-do-modelo-salvo",
    "message": "Não foi possível gerar a resposta"
  }
}
```

Também aceita essas informações no nível principal do JSON. O campo `modelo` nesse contrato indica uma escolha efetivamente salva. Essa confirmação permite persistir o modelo mesmo quando a geração falha e, na criação, reconhecer que o chat já existe. Esses formatos ainda não são retornados pelo backend atual.

## IDs e criação do chat

O ID é reservado antes da primeira mensagem. **Nova conversa** incrementa o contador em `localStorage`, na chave `routerai.lastChatId.v1`. Web Locks coordenam a reserva entre abas quando disponíveis; sem armazenamento, existe um contador temporário na aba.

Esse contador serve a testes locais: diferentes navegadores ou origens e limpeza dos dados podem reutilizar IDs existentes. O backend ainda não gera IDs nem verifica propriedade dos chats.

Após sucesso na criação, o frontend passa a usar `/chat/message`. Em falhas sem confirmação de criação, mantém o ID e tenta `/chat` novamente. Um timeout não comprova que a operação falhou no servidor; repetir o envio pode duplicar mensagens. Não há reenvio automático.

## Comportamento

- A página começa no tema escuro; o botão de tema permite alternar para claro durante o uso.
- Enter envia; Shift + Enter insere uma linha. Sugestões apenas preenchem o campo.
- Durante o envio, o campo, os botões de envio/nova conversa e o seletor ficam bloqueados.
- Histórico, ID, estado de criação e modelo confirmado ficam em `sessionStorage` na chave `routerai.conversation.v1`.
- **Nova conversa** limpa o estado local, sem excluir os chats do backend.
- Erros aparecem na página e devolvem o texto ao campo para uma tentativa manual.
- O timeout de chat é de 180 segundos; o de modelos, 10 segundos.
- O console registra URL e corpo enviado em `[RouterAI] Enviando mensagem`.

## Markdown

`index.html` carrega Marked e DOMPurify antes de `markdown.js`, `app.js` e `models.js`. Preserve essa ordem e a pasta `vendor`.

Respostas do assistente exibem Markdown sanitizado, incluindo código, tabelas e links. HTML literal aparece como texto; imagens aparecem como descrição. Mensagens do usuário são texto simples. A formatação é reaplicada ao histórico restaurado.

## Verificação manual

1. Abrir o menu duas vezes e conferir na aba Network que somente a primeira abertura consulta `/models`.
2. Clicar em **Atualizar lista** e conferir uma nova consulta.
3. Enviar com um modelo selecionado e conferir `modelo` no corpo da requisição.
4. Trocar de modelo durante a conversa e enviar outra mensagem.
5. Selecionar outro modelo sem enviar e recarregar: o menu deve restaurar o último confirmado.
6. Criar nova conversa: seleção e marcações devem estar limpas.
7. Simular falha de conexão e conferir erro visível e possibilidade de tentar novamente.

O aplicativo usa respostas reais da API. Os cenários de modelo padrão e confirmação após erro dependem de o backend implementar o contrato indicado acima.
