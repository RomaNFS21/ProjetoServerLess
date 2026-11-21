# Rota Vital — Função Serverless de Guia de Transporte

Atividade Individual 1 · Serverless  
Infraestrutura de Software · ADS · CESAR School · 2026.2

## Sobre

Função serverless que gera a guia de transporte de uma requisição do sistema **Rota Vital**. A função recebe dados de uma requisição (ID, hospital, bolsas de sangue) e retorna uma guia formatada.

## Caminho Escolhido

**Caminho A — AWS SAM CLI local**, rodando inteiramente no computador com Docker + SAM CLI, sem necessidade de conta AWS ou cartão de crédito.

## Pré-requisitos

- [Docker Desktop](https://docs.docker.com/get-started/get-docker/)
- [AWS SAM CLI](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/install-sam-cli.html)
- Python 3.12

Verifique a instalação:

```bash
sam --version
docker --version
python3 --version
```

## Como Rodar

### 1. Compilar o projeto

```bash
sam build
```

### 2. Invocar a função com evento (Passo 3)

```bash
sam local invoke -e events/pedido.json
```

Rode duas vezes seguidas para observar a diferença de tempo (cold start vs. reaproveitamento).

### 3. Acionar por HTTP (Passo 4)

```bash
# Terminal 1 — subir a API local
sam local start-api

# Terminal 2 — fazer chamadas
curl -X POST http://127.0.0.1:3000/guias \
  -H "Content-Type: application/json" \
  -d '{"requisicaoId":"R-002","hospital":"H-Caruaru"}'
```

Repita a chamada 3 vezes e observe o campo `invocacaoNesteAmbiente`.

Depois, pare o servidor e suba novamente com warm containers:

```bash
sam local start-api --warm-containers LAZY
```

Repita as chamadas e compare o valor de `invocacaoNesteAmbiente`.

### 4. Testar limite de tempo (Passo 5)

```bash
curl -X POST http://127.0.0.1:3000/guias \
  -H "Content-Type: application/json" \
  -d '{"requisicaoId":"R-003","demorar":true}'
```

Ou por invocação direta:

```bash
sam local invoke -e events/pedido_demorado.json
```

Para ajustar o timeout, edite `Timeout` em `Globals` no `template.yaml` para 10, rode `sam build` e repita.

---

## Respostas às Perguntas

### 1. Por que a primeira invocação demorou mais que a segunda? O que acontece na fase de Init?

A primeira invocação demora mais porque ocorre o chamado **cold start**. Nessa primeira chamada, o ambiente de execução precisa ser criado do zero: o Lambda (ou, no caso local, o SAM CLI) precisa baixar/iniciar o container Docker, carregar o runtime do Python 3.12, importar os módulos do handler (`json`, `time`) e inicializar as variáveis globais (como `contador = 0`). Tudo isso acontece na **fase de Init**, que antecede a execução propriamente dita do handler.

Na segunda invocação, se o ambiente ainda estiver ativo (o container já está rodando), toda essa inicialização é pulada — o Lambda reutiliza o ambiente já "quente" (warm). Por isso a segunda chamada é significativamente mais rápida, pois vai direto para a **fase de Invoke**, executando apenas a função `lambda_handler`.

A fase de Init é composta por três sub-etapas:
- **Extension init**: carregamento de extensões (se houver).
- **Runtime init**: inicialização do runtime da linguagem (Python).
- **Function init**: execução do código fora do handler (imports e variáveis globais).

### 2. O que o campo `invocacaoNesteAmbiente` mostrou com e sem `--warm-containers`? O que isso diz sobre guardar estado numa variável global da função?

**Sem `--warm-containers`** (comportamento padrão): a cada invocação via `sam local start-api`, o campo `invocacaoNesteAmbiente` era sempre **1**. Isso acontece porque o SAM CLI destruía e recriava o container a cada requisição, zerando a variável global `contador`.

**Com `--warm-containers LAZY`**: o container é mantido vivo entre as chamadas. Assim, a variável global `contador` é preservada e o campo `invocacaoNesteAmbiente` incrementou progressivamente: **1**, **2**, **3**, etc. Isso mostra que o ambiente de execução foi reaproveitado.

**Lição sobre estado:** variáveis globais no Lambda **não são confiáveis para armazenar estado** entre invocações. O reaproveitamento do ambiente é uma **otimização do provedor**, não uma garantia. O AWS Lambda pode destruir o ambiente a qualquer momento (por inatividade, atualizações, escalonamento). Portanto, qualquer dado que precise persistir entre chamadas deve ser guardado em um serviço externo como DynamoDB, S3 ou RDS, nunca em variáveis globais da função.

### 3. O que aconteceu com `demorar = true`? Qual é o tempo máximo de uma execução no Lambda, e o que fazer com um trabalho mais longo?

Ao enviar `{"requisicaoId":"R-003","demorar":true}`, a função tentou dormir por **5 segundos** (`time.sleep(5)`), porém o `Timeout` configurado em `Globals` no `template.yaml` era de apenas **3 segundos**. O resultado foi que a execução foi **interrompida antes de terminar**, gerando um erro de timeout — o Lambda abortou a função e retornou um erro (status 502 / "Task timed out after 3.00 seconds").

Após aumentar o `Timeout` para **10 segundos** no `template.yaml`, rodar `sam build` e repetir, a função completou normalmente em ~5 s e retornou a guia corretamente.

**Tempo máximo no Lambda:** o limite máximo configurável no AWS Lambda é de **15 minutos (900 segundos)**.

**O que fazer com trabalhos mais longos:**
- **Step Functions:** orquestrar o trabalho em várias funções Lambda sequenciais, cada uma dentro do limite de 15 min.
- **AWS Batch ou ECS/Fargate:** para processamentos longos, sem limite prático de tempo.
- **Fila SQS + Lambda:** quebrar o trabalho em pedaços menores, enfileirar e processar cada pedaço em uma invocação separada.
- **EventBridge:** usar eventos para encadear funções de forma assíncrona.

### 4. Quanto custa um milhão de execuções com 128 MB e 100 ms?

**Preços de us-east-1 (referência da aula):**
- Requisições: US$ 0,20 por milhão de requisições
- Computação: US$ 0,0000166667 por GB-s

**Cálculo:**

**Custo de requisições:**
- 1.000.000 requisições × US$ 0,20 / 1.000.000 = **US$ 0,20**

**Custo de computação (GB-s):**
- Memória alocada: 128 MB = 0,125 GB
- Duração por execução: 100 ms = 0,1 s
- GB-s por execução: 0,125 GB × 0,1 s = 0,0125 GB-s
- Total de GB-s: 1.000.000 × 0,0125 = 12.500 GB-s
- Custo: 12.500 GB-s × US$ 0,0000166667 = **US$ 0,2083**

**Custo total: US$ 0,20 + US$ 0,2083 ≈ US$ 0,41**

> **Nota:** O plano gratuito (always free) do Lambda inclui 1 milhão de requisições e 400.000 GB-s por mês. Como nosso uso total é de apenas 12.500 GB-s, **este cenário inteiro cairia dentro da faixa gratuita** e custaria US$ 0,00 na prática.

### 5. Em que parte do Rota Vital uma função serverless faz sentido e em qual não faz?

**Onde faz sentido (bom uso de serverless):**
- **Geração de guias de transporte:** como esta função — recebe um pedido, processa rapidamente e retorna a guia. É uma operação stateless, rápida (< 1 s) e com demanda variável, ideal para serverless.
- **Envio de notificações:** alertar hospitais, motoristas ou centrais quando uma requisição muda de status. São eventos esporádicos e rápidos.
- **Validação de requisições:** verificar se os dados de uma nova requisição estão completos e corretos antes de registrá-la no sistema.
- **Webhooks e integrações:** receber callbacks de sistemas externos (por exemplo, confirmação de entrega ou atualização de estoque do banco de sangue).
- **Processamento de eventos em fila:** processar novos pedidos de transporte conforme chegam via SQS/SNS.

**Onde NÃO faz sentido (mau uso de serverless):**
- **Rastreamento em tempo real dos veículos:** requer conexão persistente (WebSocket) e processamento contínuo de localização GPS. O cold start e o limite de 15 min tornam isso inviável com Lambda.
- **Painel/Dashboard com conexão permanente:** dashboards que mantêm conexões longas para atualizações em tempo real não combinam com o modelo efêmero do serverless.
- **Roteirização e otimização de rotas:** algoritmos de roteirização complexos podem demorar muitos minutos e consumir muita memória, ultrapassando os limites do Lambda.
- **Banco de dados ou cache:** o Lambda é stateless; tentar mantê-lo como um "serviço sempre ligado" para servir dados é ineficiente e caro comparado a serviços dedicados como RDS ou ElastiCache.

---

## Estrutura do Projeto

```
ProjetoServerLess/
├── template.yaml            # Template SAM com a definição da função e da API
├── samconfig.toml            # Configuração do SAM CLI
├── hello_world/
│   ├── __init__.py
│   ├── app.py                # Handler da função Lambda
│   └── requirements.txt      # Dependências Python
├── events/
│   ├── pedido.json           # Evento de teste padrão (R-001)
│   └── pedido_demorado.json  # Evento de teste com demorar=true (R-003)
├── evidencias/               # Capturas de tela dos experimentos
│   └── README.md
└── README.md                 # Este arquivo
```

## Uso de IA

- **Ferramenta:** Antigravity (Google DeepMind)
- **Finalidade:** Auxiliar na geração da estrutura do projeto SAM, criação dos arquivos de configuração, e formulação das respostas às perguntas teóricas com base no conteúdo visto em aula.
- **Validação:** Todos os comandos foram executados localmente com Docker e SAM CLI para confirmar o funcionamento. As respostas foram revisadas e ajustadas para refletir o entendimento pessoal do conteúdo da Aula 007 sobre serverless (ciclo de vida, cold start, limites e precificação do Lambda).
