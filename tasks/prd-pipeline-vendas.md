# PRD: Pipeline de vendas — do CSV ao gráfico

## Introdução

Temos dois CSVs de uma rede de lojas: `vendas.csv` (423 vendas, fato) e `lojas.csv` (8 lojas, dimensão). Queremos um pipeline em Python que junte os dois arquivos, calcule a receita por região e por mês e publique uma página estática com um gráfico e uma conclusão. O pipeline é construído pelo laço Ralph; a suíte `pytest` define quando o trabalho está pronto.

Os dados têm duas armadilhas propositais que o pipeline precisa tratar de forma explícita:

1. **Três vendas órfãs** (`V00421`, `V00422`, `V00423`) com `id_loja = 999`, que não existe em `lojas.csv`. Somam R$ 8.120,00.
2. **A loja 108 (Batel/PR)** existe em `lojas.csv` mas não tem nenhuma venda.

Decisão: usar **inner join** por `id_loja`. As 3 vendas órfãs e a loja 108 ficam fora do relatório, e isso é documentado no `README.md`.

## Objetivos

- Gerar `vendas_lojas.csv` (inner join) com exatamente 420 linhas de dados e soma de `receita_brl` = 931274.06.
- Gerar `pivot_receita.csv` com a receita por região × mês (4 regiões × 6 meses).
- Gerar `index.html` com um gráfico de linhas (Chart.js) e um parágrafo de conclusão de pelo menos 300 caracteres.
- Ter pelo menos 4 testes `pytest` passando, sem nenhum falhando.
- Documentar no `README.md` a decisão do join e o que ficou de fora.

## User Stories

### US-001: Inner join de vendas com lojas
**Descrição:** Como analista, quero juntar `vendas.csv` e `lojas.csv` por `id_loja` para ter a região de cada venda.

**Critérios de aceite:**
- [ ] Script `pipeline.py` na raiz lê os dois CSVs com pandas; `receita_brl` é lida como número (float), nunca como texto
- [ ] Faz **inner join** por `id_loja` e grava `vendas_lojas.csv` na **raiz** do repositório
- [ ] `vendas_lojas.csv` tem exatamente 420 linhas de dados e mantém a coluna com o nome exato `receita_brl`
- [ ] A soma de `receita_brl` em `vendas_lojas.csv` é 931274.06 (tolerância 0.50)
- [ ] `tests/test_pipeline.py` tem testes para o número de linhas (420) e para a receita total
- [ ] `python -m pytest -q` passa

### US-002: Pivot de receita por região × mês
**Descrição:** Como gestor, quero ver a receita de cada região em cada mês para comparar o desempenho.

**Critérios de aceite:**
- [ ] `pipeline.py` gera `pivot_receita.csv` na **raiz**, a partir de `vendas_lojas.csv`
- [ ] Cabeçalho exato: `regiao,2026-01,2026-02,2026-03,2026-04,2026-05,2026-06`
- [ ] 4 linhas de dados (Centro-Oeste, Nordeste, Sudeste, Sul), em ordem alfabética, 7 colunas
- [ ] Valores com ponto decimal e 2 casas (ex.: `265077.49`), sem `R$` e sem separador de milhar; arredondar só na escrita
- [ ] A soma de todas as células numéricas é 931274.06 (tolerância 0.50)
- [ ] Teste da forma do pivot (4 × 7, cabeçalho exato) e do total
- [ ] `python -m pytest -q` passa

### US-003: Página com gráfico e conclusão
**Descrição:** Como gestor, quero uma página que mostre a evolução da receita mensal por região e diga o que os números significam.

**Critérios de aceite:**
- [ ] `pipeline.py` gera `index.html` na **raiz**, com os dados do pivot embutidos
- [ ] A página tem um `<canvas>` com gráfico de linhas Chart.js (carregado de `https://cdn.jsdelivr.net/npm/chart.js`), uma linha por região, eixo X = meses
- [ ] A página tem um `<p>` de conclusão com pelo menos 300 caracteres, citando a região líder (Sudeste, R$ 265.077,49) e a receita total, com números calculados dos dados, não inventados
- [ ] Teste que confere que `index.html` existe, contém `<canvas` e um `<p>` com 300+ caracteres
- [ ] `python -m pytest -q` passa

### US-004: README com a decisão do join
**Descrição:** Como leitor do relatório, quero saber quais dados ficaram de fora e por quê.

**Critérios de aceite:**
- [ ] `README.md` na raiz explica como rodar (`python pipeline.py`, `python -m pytest -q`)
- [ ] Explica a escolha do inner join e o que ele deixou de fora: as 3 vendas órfãs (`id_loja = 999`, R$ 8.120,00) e a loja 108 (Batel/PR, sem vendas)
- [ ] Reporta linhas de entrada (423) e de saída (420), receita total bruta (939.394,06) e após o join (931.274,06)
- [ ] `python -m pytest -q` passa

## Requisitos funcionais

- FR-1: `pipeline.py` roda de ponta a ponta com `python pipeline.py`, a partir da raiz do repositório.
- FR-2: Os três entregáveis (`vendas_lojas.csv`, `pivot_receita.csv`, `index.html`) ficam na raiz, com esses nomes exatos.
- FR-3: O mês é extraído da coluna `data` no formato `YYYY-MM`.
- FR-4: Os testes ficam em `tests/test_*.py` e são no mínimo 4.

## Fora do escopo

- Não apagar nem editar linhas de `vendas.csv` ou `lojas.csv`.
- Não inventar dados nem valores.
- Não usar left join nos entregáveis.
- Não criar servidor web; a página é estática.

## Considerações técnicas

- Python 3 com pandas e pytest. Rodar no Windows (Git Bash).
- Commits direto na branch `main`.

## Métricas de sucesso

- `python -m pytest -q` verde, com pelo menos 4 testes.
- Números conferem com a referência: 420 linhas, R$ 931.274,06, Sudeste R$ 265.077,49.

## Perguntas em aberto

- Nenhuma.
