# Evidências dos Experimentos

Registros das saídas dos comandos executados durante os passos da atividade.

## Arquivos

| Arquivo | Descrição |
|---|---|
| `01-sam-build.txt` | Saída do `sam build` |
| `02-invoke-evento-duas-vezes.txt` | Duas invocações com evento — cold start vs. warm |
| `03-http-com-e-sem-warm-containers.txt` | Chamadas HTTP com e sem `--warm-containers LAZY` |
| `04-timeout-erro-e-ajuste.txt` | Erro de timeout com 3s e correção para 10s |
| `05-validacao-erro-400.txt` | Teste de validação com body vazio |

## Observações

- **Passo 3 (Invoke):** A primeira invocação levou ~8.5s (cold start com download da imagem Docker). A segunda ~3.2s (imagem em cache).
- **Passo 4 (HTTP):** Sem `--warm-containers`, `invocacaoNesteAmbiente` = 1 sempre. Com `--warm-containers LAZY`, incrementou 1→2→3.
- **Passo 5 (Timeout):** Com `Timeout: 3`, a função com `demorar: true` foi abortada (502). Com `Timeout: 10`, completou normalmente (201).
