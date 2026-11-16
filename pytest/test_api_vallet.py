"""Testes automatizados da Vallet API — mapeados 1:1 com CT-01 a CT-25 da documentação.

Execução:  pytest --html=relatorio.html --self-contained-html
Status na documentação:  PASSED = Passou · FAILED = Falhou · SKIPPED = Bloqueado
"""
import pytest

from config import COORD, PLACA, payload_estacionamento, payload_veiculo

SEM_TOKEN = (401, 403)


def _exigir_reserva(reserva_criada):
    if reserva_criada["resp"].status_code != 201:
        pytest.skip(
            f"Reserva de base não foi criada (CT-18): "
            f"{reserva_criada['resp'].status_code} {reserva_criada['resp'].text[:200]}"
        )
    return reserva_criada["resp"].json()


def _vaga_por_id(api, token, estacionamento_id, vaga_id):
    r = api.get(f"/vaga/estacionamento/{estacionamento_id}", token=token)
    assert r.status_code == 200, r.text
    return next((v for v in r.json() if v["id"] == vaga_id), None)


# ============================ AUTENTICAÇÃO ================================== #
def test_ct01_login_valido(api, motorista):
    r = api.post(
        "/auth/login",
        params={"email": motorista["email"], "senha": motorista["senha"]},
    )
    assert r.status_code == 200, r.text
    corpo = r.json()
    for campo in ("mensagem", "idToken", "refreshToken", "expiresIn", "localId"):
        assert campo in corpo, f"campo ausente: {campo}"


def test_ct02_login_senha_incorreta(api, motorista):
    r = api.post(
        "/auth/login",
        params={"email": motorista["email"], "senha": "errada123"},
    )
    assert r.status_code == 401, r.text
    assert "incorretos" in r.json()["detail"]
    assert "idToken" not in r.json()


def test_ct03_criar_usuario_motorista(usuario_novo):
    r = usuario_novo["resp"]
    assert r.status_code == 201, r.text
    corpo = r.json()
    assert corpo["uid"]
    assert corpo["email"] == usuario_novo["payload"]["email"]
    assert corpo["nome"] == usuario_novo["payload"]["nome"]
    assert corpo["tipo_user"] == "motorista"


def test_ct04_criar_usuario_email_duplicado(api, usuario_novo):
    if usuario_novo["resp"].status_code != 201:
        pytest.skip("Usuário do CT-03 não foi criado.")
    r = api.post("/auth/criar_usuario", json=usuario_novo["payload"])
    assert r.status_code == 400, r.text
    assert "já está em uso" in r.json()["detail"]


def test_ct05_criar_admin_sem_autenticacao(api):
    email = "falso_admin_qa@vallet.com"
    r = api.post(
        "/auth/criar_usuario",
        json={"nome": "Falso Admin", "email": email, "senha": "senha123", "tipo_user": "admin"},
    )
    assert r.status_code == 403, r.text
    login = api.post("/auth/login", params={"email": email, "senha": "senha123"})
    assert login.status_code != 200, "conta admin foi criada sem autenticação!"


# ============================ ADMINISTRAÇÃO ================================= #
def test_ct06_dashboard_admin(api, admin, estacionamento):
    r = api.get("/admin/dashboard", token=admin["token"])
    assert r.status_code == 200, r.text
    corpo = r.json()
    for campo in (
        "id_estacionamento", "vagas_total", "vagas_ocupadas", "reservas_hoje",
        "reservas_pendentes", "reservas_canceladas", "receita_mensal", "ultimas_reservas",
    ):
        assert campo in corpo, f"campo ausente: {campo}"
    assert corpo["id_estacionamento"] == estacionamento["id"]


def test_ct07_dashboard_sem_token(api):
    r = api.get("/admin/dashboard")
    assert r.status_code in SEM_TOKEN, f"{r.status_code} {r.text}"
    assert "vagas_total" not in r.text


# ============================== VEÍCULO ===================================== #
def test_ct08_criar_veiculo(motorista, veiculo_criado):
    r = veiculo_criado
    assert r.status_code in (200, 201), r.text
    corpo = r.json()
    assert corpo["id"]
    assert corpo["usuarioId"] == motorista["uid"]
    assert corpo["placa"] == PLACA
    assert corpo["dataCadastro"]


def test_ct09_criar_veiculo_tipo_invalido(api, motorista):
    r = api.post(
        "/veiculo/criar_veiculo",
        token=motorista["token"],
        json=payload_veiculo(tipo="Caminhão"),
    )
    assert r.status_code == 422, r.text


def test_ct10_listar_veiculos_usuario(api, motorista, veiculo_criado):
    if veiculo_criado.status_code not in (200, 201):
        pytest.skip("Veículo do CT-08 não foi criado.")
    r = api.get("/veiculo/veiculos_usuario", token=motorista["token"])
    assert r.status_code == 200, r.text
    veiculos = r.json()
    assert any(v["placa"] == PLACA for v in veiculos)
    assert all(v["usuarioId"] == motorista["uid"] for v in veiculos)

# ============================ ESTACIONAMENTO ================================ #
def test_ct11_estacionamentos_proximos(api, motorista, criacao_estacionamento):
    r = api.get(
        "/estacionamento/proximos",
        token=motorista["token"],
        params={**COORD, "raio_km": 10},
    )
    assert r.status_code == 200, r.text
    lista = r.json()
    assert isinstance(lista, list)
    distancias = [e["distanciaKm"] for e in lista]
    assert all(d <= 10 for d in distancias), "item fora do raio"
    assert distancias == sorted(distancias), "lista não está ordenada por distância"
    if criacao_estacionamento["criado"]:
        assert any(e["id"] == criacao_estacionamento["id"] for e in lista)


def test_ct12_proximos_latitude_invalida(api, motorista):
    r = api.get(
        "/estacionamento/proximos",
        token=motorista["token"],
        params={"latitude": 91, "longitude": -46.39},
    )
    assert r.status_code == 422, r.text


def test_ct13_criar_estacionamento_superadmin(admin, criacao_estacionamento):
    r = criacao_estacionamento["resp"]
    if r.status_code == 400 and "vinculado" in r.text:
        pytest.skip("O admin de teste já possuía estacionamento; use um admin sem vínculo.")
    assert r.status_code == 201, r.text
    corpo = r.json()
    assert corpo["id"]
    assert corpo["adminUid"] == admin["uid"]
    assert corpo["quantidadeVagasTotal"] == 2


def test_ct14_criar_estacionamento_como_motorista(api, motorista, admin):
    r = api.post(
        "/estacionamento/criar_estacionamento",
        token=motorista["token"],
        json=payload_estacionamento(admin["uid"]),
    )
    assert r.status_code == 403, r.text


def test_ct15_buscar_estacionamento_existente(api, superadmin, estacionamento):
    r = api.get(
        f"/estacionamento/buscar_estacionamento/{estacionamento['id']}",
        token=superadmin["token"],
    )
    assert r.status_code == 200, r.text
    corpo = r.json()
    assert corpo["id"] == estacionamento["id"]
    assert "etiquetaFuncionamento" in corpo


def test_ct16_buscar_estacionamento_inexistente(api, superadmin):
    r = api.get(
        "/estacionamento/buscar_estacionamento/id_inexistente_999",
        token=superadmin["token"],
    )
    assert r.status_code == 404, r.text
    assert "não encontrado" in r.json()["detail"]
