import unittest
import json
import time
import sys
import os

# Adiciona o diretório da função ao path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "hello_world")))
import app

class TestGuiaFunction(unittest.TestCase):

    def setUp(self):
        # Reinicia o contador global para cada teste individual
        app.contador = 0

    def test_geracao_guia_sucesso(self):
        """Testa geração correta de guia com payload válido."""
        evento = {
            "body": json.dumps({
                "requisicaoId": "R-001",
                "hospital": "H-Recife",
                "bolsas": ["O-NEG-0142"]
            })
        }
        resposta = app.lambda_handler(evento, None)
        self.assertEqual(resposta["statusCode"], 201)

        corpo = json.loads(resposta["body"])
        self.assertEqual(corpo["guia"], "G-R-001")
        self.assertEqual(corpo["hospital"], "H-Recife")
        self.assertEqual(corpo["bolsas"], ["O-NEG-0142"])
        self.assertEqual(corpo["invocacaoNesteAmbiente"], 1)

    def test_requisicao_sem_id_retorna_400(self):
        """Testa se a ausência de requisicaoId resulta em erro 400."""
        evento = {"body": json.dumps({"hospital": "H-Recife"})}
        resposta = app.lambda_handler(evento, None)
        self.assertEqual(resposta["statusCode"], 400)

        corpo = json.loads(resposta["body"])
        self.assertIn("erro", corpo)
        self.assertEqual(corpo["erro"], "requisicaoId obrigatório")

    def test_incremento_contador_ambiente(self):
        """Testa se o contador global incrementa quando o ambiente é reaproveitado."""
        evento = {"body": json.dumps({"requisicaoId": "R-002"})}
        
        resp1 = app.lambda_handler(evento, None)
        corpo1 = json.loads(resp1["body"])
        self.assertEqual(corpo1["invocacaoNesteAmbiente"], 1)

        resp2 = app.lambda_handler(evento, None)
        corpo2 = json.loads(resp2["body"])
        self.assertEqual(corpo2["invocacaoNesteAmbiente"], 2)

        resp3 = app.lambda_handler(evento, None)
        corpo3 = json.loads(resp3["body"])
        self.assertEqual(corpo3["invocacaoNesteAmbiente"], 3)

    def test_parametro_demorar(self):
        """Verifica se o parâmetro demorar aciona a pausa de execução."""
        evento = {"body": json.dumps({"requisicaoId": "R-003", "demorar": True})}
        
        inicio = time.time()
        resp = app.lambda_handler(evento, None)
        duracao = time.time() - inicio

        self.assertEqual(resp["statusCode"], 201)
        self.assertGreaterEqual(duracao, 4.9, "A execução deveria demorar pelo menos 5 segundos com demorar=True")

if __name__ == "__main__":
    unittest.main()
