# Roteiro para Gravação do Vídeo (Até 3 Minutos)

> **Requisito da Atividade:** Vídeo de até 3 minutos (gravação de tela) mostrando:
> 1. A invocação com evento
> 2. A chamada por HTTP
> 3. O erro de tempo limite (timeout)

---

## ⏱️ Linha do Tempo e Roteiro de Fala

### [00:00 - 00:30] Introdução e Estrutura do Projeto
- **O que mostrar:** VS Code aberto com a estrutura de pastas (`template.yaml` e `hello_world/app.py`).
- **O que falar:**
  > *"Olá, professor! Este é o vídeo da Atividade Individual 1 de Infraestrutura de Software sobre Serverless. O projeto implementa a geração de guias de transporte para o sistema Rota Vital usando AWS SAM CLI e Python 3.12. Aqui no `template.yaml` temos o endpoint `/guias` configurado como método POST com timeout de 3 segundos, e no `app.py` o handler com a variável global `contador` para observar o reaproveitamento do ambiente de execução."*

---

### [00:30 - 01:15] Experimento 1: Invocação da Função com Evento
- **O que mostrar:** Terminal aberto executando os comandos SAM (ou o script `python executar_testes_locais.py`).
- **Comandos:**
  ```bash
  sam build
  sam local invoke -e events/pedido.json
  # Executar uma segunda vez logo em seguida:
  sam local invoke -e events/pedido.json
  ```
- **O que falar:**
  > *"Primeiro, faço o `sam build` e executo a invocação com evento via `sam local invoke`. Notem que a primeira execução demora mais porque acontece o Cold Start — o runtime é inicializado e há a fase de Init. Na segunda execução consecutiva, o tempo cai drasticamente porque a imagem e o ambiente já estão disponíveis, indo direto para a fase de Invoke."*

---

### [01:15 - 02:05] Experimento 2: Acionamento por HTTP e Variável Global
- **O que mostrar:** Dois terminais divididos lado a lado: um com a API rodando e outro com os comandos `curl`.
- **Comandos:**
  ```bash
  # Terminal 1:
  sam local start-api
  
  # Terminal 2:
  curl -X POST http://127.0.0.1:3000/guias -H "Content-Type: application/json" -d '{"requisicaoId":"R-002","hospital":"H-Caruaru"}'
  ```
- **O que falar:**
  > *"Agora subo a API local com `sam local start-api`. Ao fazer requisições HTTP seguidas com `curl`, observem que o campo `invocacaoNesteAmbiente` é sempre 1 no modo padrão, pois o container é destruído após cada chamada. Porém, ao subir com `--warm-containers LAZY`, o container é preservado e vemos o contador incrementar: 1, 2 e 3. Isso comprova que variáveis globais só sobrevivem se o ambiente for reaproveitado, e que serverless exige que funções sejam tratadas como stateless."*

---

### [02:05 - 02:45] Experimento 3: Erro de Tempo Limite (Timeout) e Ajuste
- **O que mostrar:** Terminal executando a requisição com `demorar: true`.
- **Comandos:**
  ```bash
  curl -X POST http://127.0.0.1:3000/guias -H "Content-Type: application/json" -d '{"requisicaoId":"R-003","demorar":true}'
  ```
- **O que falar:**
  > *"Por fim, o teste de timeout: enviando `demorar: true`, a função executa um `time.sleep(5)`. Como o template define o timeout em 3 segundos, a execução é interrompida e recebemos erro 502 / Task timed out after 3.00 seconds. Para corrigir, basta aumentar o `Timeout` no `template.yaml` para 10 segundos, recompilar com `sam build` e reenviar — a função agora completa normalmente em ~5 segundos e retorna status 201."*

---

### [02:45 - 03:00] Conclusão
- **O que falar:**
  > *"Com isso cobrimos os três experimentos: ciclo de vida do ambiente (cold start), persistência de estado e limites de tempo de execução. O repositório contém todos os códigos, prints e o README completo com as respostas e o cálculo de custos. Obrigado!"*

---

## 💡 Dicas Rápidas para a Gravação
1. Use **OBS Studio** ou o **Xbox Game Bar** (`Win + G` no Windows) para gravar a tela.
2. Divida a tela: VS Code à esquerda e terminal à direita.
3. Se estiver sem Docker no momento da gravação, você pode rodar `py -3.14 executar_testes_locais.py`, que executa a simulação exata dos três cenários e mostra as mesmas mensagens e métricas no terminal!
