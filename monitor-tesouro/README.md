# Monitor Tesouro Direto

Dashboard estático que monitora as taxas de três títulos do Tesouro Direto:

- **Tesouro Prefixado 2032**
- **Tesouro IPCA+ 2050**
- **Tesouro Renda+ 2065** (no dataset oficial, vencimento 15/12/2084 — última parcela)

## Fonte de dados

CSV oficial de dados abertos do **Tesouro Transparente (STN)** — `PrecoTaxaTesouroDireto.csv`, atualizado em dias úteis por volta de 10h50 (BRT) com as taxas de abertura do dia útil anterior. Sem autenticação, sem bloqueio de bot.

> A API JSON do site tesourodireto.com.br foi descontinuada (HTTP 410) e os CSVs do site ficam atrás de proteção Cloudflare, por isso a fonte usada é o dado aberto oficial. Limitação: defasagem de ~1 dia útil (não é intraday).

## Como publicar (uma vez, ~5 min)

1. Crie um repositório no GitHub (público) e suba estes arquivos.
2. Em **Settings → Pages**: Source = *Deploy from a branch*, Branch = `main`, pasta `/docs`.
3. Em **Settings → Actions → General → Workflow permissions**: marque *Read and write permissions*.
4. Pronto. O site fica em `https://SEU_USUARIO.github.io/NOME_DO_REPO/` e o Actions atualiza o `dados.json` automaticamente em dias úteis (11h15 e 14h BRT).

Para forçar uma atualização manual: aba **Actions → Atualizar taxas → Run workflow**, ou localmente:

```bash
python atualizar.py   # gera docs/dados.json
```

## Recursos do dashboard

- Taxa de compra (destaque), taxa de resgate, PU e mín–máx de 52 semanas por título
- Variação em bps vs dia útil anterior e vs ~30 dias
- Gráfico histórico interativo (hover/toque) com janelas 3M / 6M / 1A / Tudo
- Alerta por título ("avisar se taxa compra ≥ X%"), salvo no navegador — a ficha ganha destaque quando a meta é atingida

## Adicionar/trocar títulos

Edite o dicionário `TITULOS` em `atualizar.py` usando o par exato (`Tipo Titulo`, `Data Vencimento`) do CSV oficial.
