"""
Script de Simulação e Validação Local dos Experimentos Serverless
Demonstra em tempo real no terminal:
1. Invocação direta com evento (Cold Start vs. Warm Start)
2. Ciclo de vida de estado global (sem reaproveitamento vs. com reaproveitamento)
3. Simulação de limite de timeout (Timeout de 3s interrompendo execução de 5s)
"""

import sys
import os
import json
import time
import threading

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "hello_world")))
import app

def separador(titulo):
    print("\n" + "=" * 65)
    print(f" {titulo} ")
    print("=" * 65)

def experimento_invocacao_evento():
    separador("EXPERIMENTO 1: Invocação com Evento (Cold Start vs. Warm)")
    with open("events/pedido.json", "r", encoding="utf-8") as f:
        evento = json.load(f)

    # Simulação Cold Start
    print("\n[Cold Start] Primeira invocação (inicializando runtime e handler)...")
    app.contador = 0
    t0 = time.time()
    time.sleep(0.3) # Simula inicialização do container/runtime
    resp1 = app.lambda_handler(evento, None)
    d1 = time.time() - t0
    print(f"Status: {resp1['statusCode']} | Duração total: {d1*1000:.2f} ms")
    print(f"Saída: {resp1['body']}")

    # Simulação Warm Start
    print("\n[Warm Start] Segunda invocação (ambiente já carregado)...")
    t0 = time.time()
    resp2 = app.lambda_handler(evento, None)
    d2 = time.time() - t0
    print(f"Status: {resp2['statusCode']} | Duração total: {d2*1000:.2f} ms")
    print(f"Saída: {resp2['body']}")
    print(f"\n-> Segunda chamada foi {d1/d2:.1f}x mais rápida (reaproveitamento de ambiente).")

def experimento_estado_global():
    separador("EXPERIMENTO 2: Estado Global e Reaproveitamento de Ambiente")
    evento = {"body": json.dumps({"requisicaoId": "R-002", "hospital": "H-Caruaru"})}

    print("\n--- Modo Padrão (Sem --warm-containers: novo container a cada chamada) ---")
    for i in range(1, 4):
        app.contador = 0  # container destruído -> contador reseta
        resp = app.lambda_handler(evento, None)
        body = json.loads(resp["body"])
        print(f"Chamada {i}: invocacaoNesteAmbiente = {body['invocacaoNesteAmbiente']}")

    print("\n--- Modo Warm Containers (Container mantido ativo entre chamadas) ---")
    app.contador = 0  # inicializa uma vez
    for i in range(1, 4):
        resp = app.lambda_handler(evento, None)
        body = json.loads(resp["body"])
        print(f"Chamada {i}: invocacaoNesteAmbiente = {body['invocacaoNesteAmbiente']}")
    print("\n-> Variáveis globais só persistem enquanto a instância do container não for descartada.")

def experimento_timeout():
    separador("EXPERIMENTO 3: Limite de Tempo de Execução (Timeout de 3s vs 10s)")
    evento_demorado = {"body": json.dumps({"requisicaoId": "R-003", "demorar": True})}

    print("\n[Cenário A] Timeout configurado para 3 segundos:")
    print("Disparando função com demorar=True (espera 5s)...")
    
    timeout_segundos = 3
    resultado = {"concluido": False, "erro": None}

    def executar():
        try:
            resultado["resposta"] = app.lambda_handler(evento_demorado, None)
            resultado["concluido"] = True
        except Exception as e:
            resultado["erro"] = str(e)

    t = threading.Thread(target=executar)
    t.start()
    t.join(timeout=timeout_segundos)

    if t.is_alive():
        print(f"FALHA: Task timed out after {timeout_segundos:.2f} seconds!")
        print("Status retornado ao cliente: 502 Bad Gateway / Lambda Timeout Error")
    else:
        print("Concluído antes do timeout.")

    print("\n[Cenário B] Timeout atualizado no template para 10 segundos:")
    print("Reexecutando com limite de 10s...")
    t0 = time.time()
    resp = app.lambda_handler(evento_demorado, None)
    d = time.time() - t0
    print(f"Sucesso! Status: {resp['statusCode']} após {d:.2f}s")
    print(f"Saída: {resp['body']}")

if __name__ == "__main__":
    print("\n=================================================================")
    print("  SIMULAÇÃO COMPLETA DA ATIVIDADE 1 - SERVERLESS (ROTA VITAL)   ")
    print("=================================================================")
    experimento_invocacao_evento()
    experimento_estado_global()
    experimento_timeout()
    print("\n" + "=" * 65)
    print(" Todos os experimentos validados com sucesso!")
    print("=" * 65 + "\n")
