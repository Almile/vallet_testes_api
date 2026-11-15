"""Fixtures da suíte pytest da Vallet API.

Os recursos compartilhados (estacionamento, reserva, veículo...) são criados uma
única vez por sessão e removidos ao final (limpeza "melhor esforço").
Casos que dependem de algo que não pôde ser preparado são marcados como
SKIPPED, o que na documentação corresponde a "Bloqueado".
"""
import os
import uuid

import pytest
import requests

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:  # python-dotenv é opcional
    pass

from config import BASE_URL, TIMEOUT, PLACA, payload_estacionamento, payload_veiculo


# --------------------------------------------------------------------------- #
# Cliente HTTP
# --------------------------------------------------------------------------- #
class ApiClient:
    def __init__(self, base_url):
        self.base_url = base_url
        self.session = requests.Session()

    def request(self, method, path, token=None, **kwargs):
        headers = kwargs.pop("headers", {})
        if token:
            headers["Authorization"] = f"Bearer {token}"
        return self.session.request(
            method, f"{self.base_url}{path}", headers=headers, timeout=TIMEOUT, **kwargs
        )

    def get(self, path, token=None, **kw):
        return self.request("GET", path, token, **kw)

    def post(self, path, token=None, **kw):
        return self.request("POST", path, token, **kw)

    def delete(self, path, token=None, **kw):
        return self.request("DELETE", path, token, **kw)


def fazer_login(api, email, senha):
    """Login via POST /auth/login (e-mail e senha vão como query params)."""
    r = api.post("/auth/login", params={"email": email, "senha": senha})
    if r.status_code != 200:
        return None
    dados = r.json()
    return {"email": email, "token": dados["idToken"], "uid": dados["localId"]}


def _login_do_ambiente(api, prefixo):
    email, senha = os.getenv(f"{prefixo}_EMAIL"), os.getenv(f"{prefixo}_SENHA")
    if not email or not senha:
        return None
    return fazer_login(api, email, senha)


def _conta_obrigatoria(api, prefixo, perfil):
    if not os.getenv(f"{prefixo}_EMAIL") or not os.getenv(f"{prefixo}_SENHA"):
        pytest.skip(f"Defina {prefixo}_EMAIL e {prefixo}_SENHA no .env (conta {perfil}).")
    conta = _login_do_ambiente(api, prefixo)
    if conta is None:
        pytest.skip(f"Login da conta {perfil} falhou; confira as credenciais no .env.")
    return conta


# --------------------------------------------------------------------------- #
# Infraestrutura
# --------------------------------------------------------------------------- #
@pytest.fixture(scope="session")
def api():
    return ApiClient(BASE_URL)


@pytest.fixture(scope="session", autouse=True)
def _acordar_api(api):
    """Primeira chamada (cold start da hospedagem) com timeout generoso."""
    try:
        api.get("/docs")
    except requests.RequestException as erro:
        pytest.exit(f"API inacessível em {BASE_URL}: {erro}", returncode=2)


# --------------------------------------------------------------------------- #
# Contas
# --------------------------------------------------------------------------- #
@pytest.fixture(scope="session")
def usuarios_criados(api):
    """Contas criadas pelos testes; desativadas ao final se houver superadmin."""
    uids = []
    yield uids
    super_conta = _login_do_ambiente(api, "SUPER")
    if not super_conta:
        return
    for uid in uids:
        try:
            api.post(f"/auth/desativar_conta/{uid}", token=super_conta["token"])
        except requests.RequestException:
            pass


@pytest.fixture(scope="session")
def motorista(api):
    email = os.getenv("MOTORISTA_EMAIL", "teste_motorista@gmail.com")
    senha = os.getenv("MOTORISTA_SENHA", "teste123")
    conta = fazer_login(api, email, senha)
    if conta is None:  # conta ainda não existe: cadastro público de motorista
        r = api.post(
            "/auth/criar_usuario",
            json={"nome": "Motorista Teste", "email": email, "senha": senha},
        )
        if r.status_code == 201:
            conta = fazer_login(api, email, senha)
    if conta is None:
        pytest.skip("Não foi possível obter/criar a conta de motorista de teste.")
    conta["senha"] = senha
    return conta


@pytest.fixture(scope="session")
def admin(api):
    return _conta_obrigatoria(api, "ADMIN", "admin")


@pytest.fixture(scope="session")
def superadmin(api):
    return _conta_obrigatoria(api, "SUPER", "superadmin")


@pytest.fixture(scope="session")
def usuario_novo(api, usuarios_criados):
    """Cadastro público com e-mail único (CT-03 / CT-04)."""
    payload = {
        "nome": "Motorista Teste",
        "email": f"motorista_{uuid.uuid4().hex[:10]}@vallet.com",
        "senha": "senha123",
    }
    r = api.post("/auth/criar_usuario", json=payload)
    if r.status_code == 201:
        usuarios_criados.append(r.json()["uid"])
    return {"payload": payload, "resp": r}


# --------------------------------------------------------------------------- #
# Veículo
# --------------------------------------------------------------------------- #
@pytest.fixture(scope="session")
def veiculo_criado(api, motorista):
    r = api.post("/veiculo/criar_veiculo", token=motorista["token"], json=payload_veiculo())
    yield r
    if r.status_code in (200, 201):
        try:
            api.delete(f"/veiculo/deletar_veiculo/{r.json()['id']}", token=motorista["token"])
        except Exception:
            pass


# --------------------------------------------------------------------------- #
# Estacionamento e vagas
# --------------------------------------------------------------------------- #
@pytest.fixture(scope="session")
def criacao_estacionamento(api, admin, superadmin):
    """Tenta criar o estacionamento (CT-13). Se o admin já tiver um, reaproveita."""
    r = api.post(
        "/estacionamento/criar_estacionamento",
        token=superadmin["token"],
        json=payload_estacionamento(admin["uid"]),
    )
    info = {"resp": r, "criado": r.status_code == 201, "id": None}
    if info["criado"]:
        info["id"] = r.json().get("id")
    else:
        r2 = api.get("/estacionamento/listar_estacionamentos_usuario", token=admin["token"])
        if r2.status_code == 200 and r2.json():
            info["id"] = r2.json()[0]["id"]
    yield info
    if info["criado"] and info["id"]:
        try:
            api.delete(
                f"/estacionamento/excluir_estacionamento/{info['id']}",
                token=superadmin["token"],
            )
        except Exception:
            pass


@pytest.fixture(scope="session")
def estacionamento(criacao_estacionamento):
    if not criacao_estacionamento["id"]:
        r = criacao_estacionamento["resp"]
        pytest.skip(f"Estacionamento de teste indisponível ({r.status_code}): {r.text[:200]}")
    return criacao_estacionamento


@pytest.fixture(scope="session")
def vagas_livres(api, motorista, estacionamento):
    r = api.get(f"/vaga/estacionamento/{estacionamento['id']}", token=motorista["token"])
    if r.status_code != 200:
        pytest.skip(f"Não foi possível listar as vagas ({r.status_code}).")
    livres = [v for v in r.json() if v.get("disponivel")]
    livres.sort(key=lambda v: v.get("numero", ""))
    if len(livres) < 2:
        pytest.skip("São necessárias ao menos 2 vagas livres no estacionamento de teste.")
    return livres


@pytest.fixture(scope="session")
def vaga_reserva(vagas_livres):
    return vagas_livres[0]


@pytest.fixture(scope="session")
def vaga_extra(vagas_livres):
    return vagas_livres[1]


# --------------------------------------------------------------------------- #
# Reserva
# --------------------------------------------------------------------------- #
@pytest.fixture(scope="session")
def reserva_criada(api, motorista, estacionamento, vaga_reserva):
    payload = {
        "vagaId": vaga_reserva["id"],
        "estacionamentoId": estacionamento["id"],
        "duracaoHoras": 1,
        "placa": PLACA,
    }
    r = api.post("/reserva/criar", token=motorista["token"], json=payload)
    yield {"payload": payload, "resp": r}
    if r.status_code == 201:
        try:
            api.post(f"/reserva/{r.json()['id']}/cancelar", token=motorista["token"])
        except Exception:
            pass
