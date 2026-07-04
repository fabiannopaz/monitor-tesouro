#!/usr/bin/env python3
"""
Atualiza docs/dados.json com as taxas dos títulos monitorados.

Fonte oficial (dados abertos, sem autenticação):
Tesouro Transparente - "Taxas dos Títulos Ofertados pelo Tesouro Direto"
Arquivo PrecoTaxaTesouroDireto.csv, atualizado em dias úteis (~10h50 BRT)
com as taxas de abertura do dia útil anterior.
"""

import csv
import io
import json
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

CSV_URL = (
    "https://www.tesourotransparente.gov.br/ckan/dataset/"
    "df56aa42-484a-4a59-8184-7676580c81e3/resource/"
    "796d2059-14e9-44e3-80c9-2d9e30b405c1/download/precotaxatesourodireto.csv"
)

# (Tipo Titulo no CSV, Data Vencimento no CSV) -> metadados de exibição
TITULOS = {
    ("Tesouro Prefixado", "01/01/2032"): {
        "id": "prefixado-2032",
        "nome": "Tesouro Prefixado 2032",
        "indexador": "Prefixado",
        "vencimento": "01/01/2032",
    },
    ("Tesouro IPCA+", "15/08/2050"): {
        "id": "ipca-2050",
        "nome": "Tesouro IPCA+ 2050",
        "indexador": "IPCA+",
        "vencimento": "15/08/2050",
    },
    # No dataset, o Renda+ 2065 aparece com vencimento 15/12/2084
    # (última das 240 parcelas mensais; a conversão ocorre em 15/12/2065).
    ("Tesouro Renda+ Aposentadoria Extra", "15/12/2084"): {
        "id": "renda-2065",
        "nome": "Tesouro Renda+ 2065",
        "indexador": "IPCA+",
        "vencimento": "15/12/2065 (conversão)",
    },
}


def num(s: str) -> float:
    return float(s.replace(".", "").replace(",", "."))


def main() -> int:
    req = urllib.request.Request(CSV_URL, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=120) as resp:
        raw = resp.read().decode("latin-1")

    reader = csv.reader(io.StringIO(raw), delimiter=";")
    header = next(reader)
    if header[0] != "Tipo Titulo":
        print(f"Layout inesperado do CSV: {header}", file=sys.stderr)
        return 1

    series = {meta["id"]: {} for meta in TITULOS.values()}
    for row in reader:
        key = (row[0], row[1])
        meta = TITULOS.get(key)
        if not meta:
            continue
        d = datetime.strptime(row[2], "%d/%m/%Y").date().isoformat()
        # Deduplica por data (mantém a última ocorrência do arquivo)
        series[meta["id"]][d] = {
            "d": d,
            "tc": num(row[3]),   # taxa compra (investir), % a.a.
            "tv": num(row[4]),   # taxa venda (resgate), % a.a.
            "puc": num(row[5]),  # PU compra
            "puv": num(row[6]),  # PU venda
        }

    saida = {
        "atualizado_em": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "fonte": "Tesouro Transparente (STN) - PrecoTaxaTesouroDireto.csv",
        "titulos": [],
    }
    for meta in TITULOS.values():
        hist = sorted(series[meta["id"]].values(), key=lambda x: x["d"])
        if not hist:
            print(f"AVISO: nenhum dado para {meta['nome']}", file=sys.stderr)
            continue
        saida["titulos"].append({**meta, "historico": hist})

    destino = Path(__file__).parent / "docs" / "dados.json"
    destino.write_text(
        json.dumps(saida, ensure_ascii=False, separators=(",", ":")),
        encoding="utf-8",
    )
    ult = max(t["historico"][-1]["d"] for t in saida["titulos"])
    print(f"OK: {destino} gerado. Data-base mais recente: {ult}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
