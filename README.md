# Pipeline de vendas

Junta `vendas.csv` com `lojas.csv`, calcula a receita por região e mês e gera uma página com gráfico e conclusão.

## Como rodar

```
python pipeline.py
python -m pytest -q
```

`python pipeline.py` lê `vendas.csv` e `lojas.csv` (sem alterá-los) e grava na raiz do repositório:

- `vendas_lojas.csv`: resultado do join (uma linha por venda, com a região da loja);
- `pivot_receita.csv`: receita por região (linhas) x mês (colunas);
- `index.html`: gráfico de linhas Chart.js (uma linha por região) e parágrafo de conclusão.

Requer Python com `pandas` e `pytest`.

## Decisão do join: inner join por `id_loja`

Usamos **inner join**: só entram na análise as vendas cuja loja existe em `lojas.csv`, porque a região vem da tabela de lojas. Uma venda sem loja não tem região e não pode entrar no pivot região x mês sem inventar dados. Por isso o inner join deixa dois grupos de fora:

1. **3 vendas órfãs**, com `id_loja = 999`, que não existe em `lojas.csv`. Somam **R$ 8.120,00**.
2. **A loja 108 (Batel/PR, região Sul)**, que existe em `lojas.csv` mas não tem nenhuma venda. Ela não gera linha no resultado.

Nenhuma linha foi apagada ou editada nos CSVs de origem; as vendas órfãs continuam em `vendas.csv`. `receita_brl` é lida como número (float).

## Números

| | Linhas | Receita total (R$) |
|---|---|---|
| Entrada (`vendas.csv`) | 423 | 939394.06 |
| Saída (`vendas_lojas.csv`, após o join) | 420 | 931274.06 |
| Diferença (vendas órfãs) | 3 | 8120.00 |

A receita do pivot e do gráfico (R$ 931.274,06) não inclui as vendas órfãs, então fica R$ 8.120,00 abaixo da receita bruta.
