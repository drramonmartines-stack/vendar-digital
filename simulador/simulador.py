"""Simulador de compradores sintéticos para produtos digitais de ticket baixo.

Para cada nicho, roda milhares de campanhas simuladas de anúncios no Instagram.
Em cada campanha:
  1. Sorteia as incertezas do mercado (CPM, CTR, qualidade do criativo, taxas de
     order bump e upsell, reembolso).
  2. Converte a verba em impressões e cliques.
  3. Gera uma persona sintética para cada visitante da página (dor, confiança em
     infoproduto, impulso de compra e quanto aceitaria pagar) e decide, com um
     modelo probabilístico, se ela compra.
  4. Calcula faturamento, taxas da plataforma, reembolsos, lucro e ROI.

Uso:
  python simulador/simulador.py                 # R$1000, 5000 campanhas por nicho
  python simulador/simulador.py --verba 1000 --runs 10000 --seed 7
  python simulador/simulador.py --precos 37 47 50   # testa outros preços
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import numpy as np

AQUI = Path(__file__).resolve().parent

# Meta repassa PIS/Cofins + ISS desde jan/2026 (~12,15% sobre o valor cobrado),
# então de cada R$1000 pagos cerca de R$891 viram mídia.
IMPOSTO_META = 0.1215
# Taxa Kiwify por venda aprovada (verificar no painel; pode mudar).
TAXA_PCT = 0.0899
TAXA_FIXA = 2.49
# Fração dos cliques que de fato carrega a página (perda por lentidão/voltar).
CARREGAMENTO = (0.70, 0.80, 0.90)

# Coeficientes do modelo de decisão da persona (logístico).
INTERCEPTO = -7.0
PESO_DOR = 2.2
PESO_CONFIANCA = 1.5
PESO_IMPULSO = 1.2
PESO_PRECO = 1.4  # sensibilidade a ln(disposição a pagar / preço)


def tri(rng: np.random.Generator, faixa, n=None):
    lo, moda, hi = faixa
    return rng.triangular(lo, moda, hi, n)


def simular_nicho(nicho: dict, verba: float, runs: int, rng: np.random.Generator,
                  preco: float | None = None) -> dict:
    preco = float(preco or nicho["preco"])
    p = nicho["persona"]
    midia = verba / (1 + IMPOSTO_META)

    lucros = np.empty(runs)
    vendas = np.empty(runs)
    brutos = np.empty(runs)
    cvrs = np.empty(runs)

    for i in range(runs):
        cpm = tri(rng, nicho["cpm"])
        qualidade = rng.lognormal(0.0, 0.35)  # criativo bom ou ruim
        ctr = min(tri(rng, nicho["ctr"]) * qualidade ** 0.5, 0.08)
        impressoes = int(midia / cpm * 1000)
        cliques = rng.binomial(impressoes, ctr)
        visitantes = rng.binomial(cliques, tri(rng, CARREGAMENTO))

        # Personas sintéticas, uma por visitante.
        dor = rng.beta(*p["dor"], visitantes)
        confianca = rng.beta(*p["confianca"], visitantes)
        impulso = rng.beta(*p["impulso"], visitantes)
        wtp = rng.lognormal(math.log(p["wtp_mediana"]), 0.5, visitantes)
        logit = (INTERCEPTO + PESO_DOR * dor + PESO_CONFIANCA * confianca
                 + PESO_IMPULSO * impulso + PESO_PRECO * np.log(wtp / preco)
                 + math.log(qualidade))  # página/oferta boa aumenta a chance
        compra = rng.random(visitantes) < 1 / (1 + np.exp(-logit))
        n = int(compra.sum())

        bump = rng.binomial(n, tri(rng, nicho["order_bump"]["taxa"]))
        up = rng.binomial(n, tri(rng, nicho["upsell"]["taxa"]))
        bruto = n * preco + bump * nicho["order_bump"]["preco"] + up * nicho["upsell"]["preco"]
        reemb = tri(rng, nicho["reembolso"])
        liquido_vendas = bruto * (1 - reemb)
        taxas = liquido_vendas * TAXA_PCT + (n + up) * (1 - reemb) * TAXA_FIXA
        liquido = liquido_vendas - taxas

        lucros[i] = liquido - verba
        vendas[i] = n
        brutos[i] = bruto
        cvrs[i] = n / visitantes if visitantes else 0.0

    roi = lucros / verba
    return {
        "id": nicho["id"],
        "nome": nicho["nome"],
        "preco": preco,
        "vendas_p50": float(np.median(vendas)),
        "vendas_p10": float(np.percentile(vendas, 10)),
        "vendas_p90": float(np.percentile(vendas, 90)),
        "conversao_pagina_p50": float(np.median(cvrs)),
        "faturamento_p50": float(np.median(brutos)),
        "roas_p50": float(np.median(brutos) / verba),
        "cpa_p50": float(verba / max(np.median(vendas), 1)),
        "lucro_p10": float(np.percentile(lucros, 10)),
        "lucro_p50": float(np.median(lucros)),
        "lucro_p90": float(np.percentile(lucros, 90)),
        "roi_p50": float(np.median(roi)),
        "prob_lucro": float((lucros > 0).mean()),
        "prob_empate_50": float((lucros > -0.5 * verba).mean()),
    }


def nota_final(res: dict, qual: dict) -> float:
    """Nota 0-10: 50% simulação (ROI e chance de lucro) + 50% critérios de mercado."""
    nota_roi = max(0.0, min(10.0, 5 + 5 * res["roi_p50"]))
    nota_prob = 10 * res["prob_lucro"]
    sim = 0.6 * nota_roi + 0.4 * nota_prob
    mercado = (qual["demanda"] + qual["concorrencia"] + qual["risco_politica_meta"]
               + qual["escala"] + qual["recompra"]) / 5
    return round(0.5 * sim + 0.5 * mercado, 2)


def brl(v: float) -> str:
    s = f"{v:,.0f}".replace(",", ".")
    return f"R$ {s}" if v >= 0 else f"-R$ {s[1:]}"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--verba", type=float, default=1000)
    ap.add_argument("--runs", type=int, default=5000)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--precos", type=float, nargs="*", default=None)
    ap.add_argument("--saida", default=str(AQUI / "resultados.json"))
    args = ap.parse_args()

    cfg = json.loads((AQUI / "nichos.json").read_text(encoding="utf-8"))
    rng = np.random.default_rng(args.seed)

    resultados = []
    for nicho in cfg["nichos"]:
        r = simular_nicho(nicho, args.verba, args.runs, rng)
        r["nota"] = nota_final(r, nicho["qualitativo"])
        if args.precos:
            r["por_preco"] = {str(int(pz)): simular_nicho(nicho, args.verba, args.runs, rng, pz)
                              for pz in args.precos}
        resultados.append(r)
    resultados.sort(key=lambda r: r["nota"], reverse=True)

    Path(args.saida).write_text(json.dumps(resultados, ensure_ascii=False, indent=2),
                                encoding="utf-8")

    print(f"Verba {brl(args.verba)} | {args.runs} campanhas simuladas por nicho\n")
    print(f"{'Nicho':42} {'Nota':>5} {'Vendas':>12} {'Conv.':>6} {'ROAS':>5} "
          f"{'Lucro p50':>11} {'Chance lucro':>13}")
    for r in resultados:
        print(f"{r['nome'][:42]:42} {r['nota']:>5.2f} "
              f"{r['vendas_p10']:>4.0f}-{r['vendas_p90']:<4.0f}({r['vendas_p50']:.0f}) "
              f"{100 * r['conversao_pagina_p50']:>5.1f}% {r['roas_p50']:>5.2f} "
              f"{brl(r['lucro_p50']):>11} {100 * r['prob_lucro']:>12.0f}%")
        for pz, rp in r.get("por_preco", {}).items():
            print(f"{'   preço R$' + pz:42} {'':>5} {'':>12} "
                  f"{100 * rp['conversao_pagina_p50']:>5.1f}% {rp['roas_p50']:>5.2f} "
                  f"{brl(rp['lucro_p50']):>11} {100 * rp['prob_lucro']:>12.0f}%")


if __name__ == "__main__":
    main()
