"""Constantes e dados de teste compartilhados pela suíte."""
import os

BASE_URL = os.getenv("BASE_URL", "https://valletapi.onrender.com").rstrip("/")
TIMEOUT = int(os.getenv("TIMEOUT", "90"))

COORD = {"latitude": -23.9618, "longitude": -46.3922}
PLACA = "ABC1D23"


def payload_veiculo(tipo="Carro"):
    return {
        "placa": PLACA,
        "marca": "VW",
        "modelo": "Gol",
        "ano": 2020,
        "cor": "Prata",
        "tipo": tipo,
    }


def payload_estacionamento(admin_uid):
    return {
        "nome": "Estac. Teste QA",
        "cnpj": "00.000.000/0001-00",
        "adminUid": admin_uid,
        **COORD,
        "valorHora": 10,
        "vagasIniciais": [{"numero": "A-1"}, {"numero": "A-2"}],
    }
