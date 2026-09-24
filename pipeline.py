"""Pipeline de vendas: junta vendas.csv e lojas.csv, agrega por regiao x mes e gera index.html."""
import json

import pandas as pd

VENDAS_CSV = "vendas.csv"
LOJAS_CSV = "lojas.csv"
VENDAS_LOJAS_CSV = "vendas_lojas.csv"
PIVOT_RECEITA_CSV = "pivot_receita.csv"
INDEX_HTML = "index.html"
CHARTJS_URL = "https://cdn.jsdelivr.net/npm/chart.js"


def load_vendas() -> pd.DataFrame:
    return pd.read_csv(VENDAS_CSV, dtype={"id_loja": "int64"}).astype({"receita_brl": "float64"})


def load_lojas() -> pd.DataFrame:
    return pd.read_csv(LOJAS_CSV, dtype={"id_loja": "int64"})


def build_vendas_lojas() -> pd.DataFrame:
    vendas = load_vendas()
    lojas = load_lojas()
    return vendas.merge(lojas, on="id_loja", how="inner")


def build_pivot_receita(vendas_lojas: pd.DataFrame) -> pd.DataFrame:
    mes = vendas_lojas["data"].str[:7].rename("mes")
    pivot = vendas_lojas.pivot_table(
        index="regiao", columns=mes, values="receita_brl", aggfunc="sum", fill_value=0.0
    )
    return pivot.sort_index().reset_index().rename_axis(columns=None)


def format_brl(value: float) -> str:
    return "R$ " + f"{value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def build_conclusao(pivot: pd.DataFrame) -> str:
    meses = [c for c in pivot.columns if c != "regiao"]
    totais = pivot.set_index("regiao")[meses].sum(axis=1).sort_values(ascending=False)
    total = totais.sum()
    lider, ultima = totais.index[0], totais.index[-1]
    por_mes = pivot[meses].sum()
    melhor_mes, pior_mes = por_mes.idxmax(), por_mes.idxmin()
    return (
        f"A receita total das vendas com loja identificada, de {meses[0]} a {meses[-1]}, foi de {format_brl(total)}. "
        f"A regiao lider e {lider}, com {format_brl(totais[lider])} ({totais[lider] / total:.1%} do total), "
        f"seguida por {totais.index[1]} ({format_brl(totais.iloc[1])}) e {totais.index[2]} ({format_brl(totais.iloc[2])}). "
        f"A regiao com menor receita e {ultima}, com {format_brl(totais[ultima])} ({totais[ultima] / total:.1%} do total). "
        f"O melhor mes foi {melhor_mes} ({format_brl(por_mes[melhor_mes])}) e o pior foi {pior_mes} "
        f"({format_brl(por_mes[pior_mes])}). Os valores consideram apenas o inner join: as vendas orfas "
        f"(id_loja 999) e a loja sem vendas ficam fora deste relatorio."
    )


HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<title>Receita por regiao e mes</title>
<script src="{chartjs_url}"></script>
</head>
<body>
<h1>Receita mensal por regiao</h1>
<canvas id="grafico" width="900" height="450"></canvas>
<p id="conclusao">{conclusao}</p>
<script>
const meses = {meses};
const series = {series};
new Chart(document.getElementById("grafico"), {{
  type: "line",
  data: {{
    labels: meses,
    datasets: series.map(s => ({{ label: s.regiao, data: s.valores, tension: 0.2 }}))
  }},
  options: {{ scales: {{ y: {{ title: {{ display: true, text: "Receita (R$)" }} }} }} }}
}});
</script>
</body>
</html>
"""


def build_index_html(pivot: pd.DataFrame) -> str:
    meses = [c for c in pivot.columns if c != "regiao"]
    series = [
        {"regiao": row["regiao"], "valores": [round(float(row[m]), 2) for m in meses]}
        for _, row in pivot.iterrows()
    ]
    return HTML_TEMPLATE.format(
        chartjs_url=CHARTJS_URL,
        conclusao=build_conclusao(pivot),
        meses=json.dumps(meses),
        series=json.dumps(series),
    )


def main() -> None:
    vendas_lojas = build_vendas_lojas()
    vendas_lojas.to_csv(VENDAS_LOJAS_CSV, index=False)
    pivot = build_pivot_receita(vendas_lojas)
    pivot.to_csv(PIVOT_RECEITA_CSV, index=False, float_format="%.2f")
    with open(INDEX_HTML, "w", encoding="utf-8") as f:
        f.write(build_index_html(pivot))


if __name__ == "__main__":
    main()
