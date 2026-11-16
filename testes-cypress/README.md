# Testes de endpoints do ValletWeb

Este projeto Cypress verifica endpoints HTTP do ValletWeb publicado em
`https://valletweb.onrender.com`, sem enviar credenciais nem alterar dados.

## Instalação

No terminal, acesse esta pasta e instale as dependências:

```bash
npm install
```

## Executar

Rode os testes em modo headless:

```bash
npm run cy:run
```

Abra a interface do Cypress:

```bash
npm run cy:open
```

Por padrão, os testes apontam para a URL de produção. Como o Render suspende
instâncias ociosas, a primeira requisição pode demorar (cold start) ou receber
`502/503` enquanto a aplicação acorda. Por isso a suíte usa `responseTimeout`
de 120s e até 2 retries por teste no modo headless. Se a instância estiver
realmente fora do ar, os testes continuarão falhando.

Para testar outra instância, defina `CYPRESS_BASE_URL` antes de executar o
comando. Por exemplo, no PowerShell:

```powershell
$env:CYPRESS_BASE_URL = "http://127.0.0.1:8001"
npm run cy:run
```
