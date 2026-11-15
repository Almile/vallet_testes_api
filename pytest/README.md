# Testes automatizados — Vallet API (pytest)


## 1. Preparar o ambiente

```bash
python -m venv venv
# Windows (cmd):   venv\Scripts\activate
# Linux / macOS:   source venv/bin/activate
pip install -r requirements.txt
```

## 2. Configurar contas

Copie `.env.example` para `.env` e preencha:

| Variável | Uso |
|---|---|
| `BASE_URL` | API sob teste (Render ou `http://127.0.0.1:8000` se rodar local) |
| `MOTORISTA_EMAIL` / `MOTORISTA_SENHA` | Motorista de teste (criado automaticamente se não existir) |
| `ADMIN_EMAIL` / `ADMIN_SENHA` | Admin **sem estacionamento vinculado** |
| `SUPER_EMAIL` / `SUPER_SENHA` | Superadmin |


## 3. Rodar

```bash
pytest --html=relatorio.html --self-contained-html
```

Para um caso específico: `pytest -k ct18`.

Abra `relatorio.html` e tire os prints (seção 4 da documentação).

## 4. Como ler o resultado

| pytest | Na documentação |
|---|---|
| PASSED | Passou |
| FAILED | Falhou (registrar em 4.2 — Relatório de Defeitos) |
| SKIPPED | Bloqueado (a mensagem mostra o motivo) |

Percentual de sucesso = `passed ÷ (passed + failed) × 100`.

## 5. Observações importantes

- **Dados criados:** a suíte cria um estacionamento, veículo, reserva e usuário, e tenta removê-los ao final (excluir estacionamento, deletar veículo, cancelar reserva, desativar usuário). Prefira um banco/projeto Firebase **de teste**.
- **Admin já vinculado:** se o admin já tiver estacionamento, o CT-13 fica SKIPPED e os demais reaproveitam o existente.
- **Cold start:** na hospedagem gratuita a 1ª chamada pode demorar; o `TIMEOUT` padrão é 90 s.
- **Falhas esperadas (hipóteses da seção 2.3):** o CT-24 deve **falhar** se a câmera marcar `ocupada` mas não `disponivel` na vaga. Se falhar, é um bug real a documentar.
- **Barra final:** `/reserva/` e `/notificacoes/` usam barra final porque o router define a rota como `/` (evita redirect 307).
- Os códigos `401/403` para "sem token" são aceitos nos dois valores; o real aparece na mensagem de falha.
