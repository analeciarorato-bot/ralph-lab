import re
import subprocess
import sys
from pathlib import Path

import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parent.parent
VENDAS_LOJAS_CSV = ROOT / "vendas_lojas.csv"
PIVOT_RECEITA_CSV = ROOT / "pivot_receita.csv"
INDEX_HTML = ROOT / "index.html"

EXPECTED_LINE_COUNT = 420
EXPECTED_RECEITA_TOTAL = 931274.06
TOLERANCE = 0.50


@pytest.fixture(scope="module", autouse=True)
def run_pipeline():
    subprocess.run([sys.executable, str(ROOT / "pipeline.py")], cwd=ROOT, check=True)
    yield


def test_vendas_lojas_row_count():
    df = pd.read_csv(VENDAS_LOJAS_CSV)
    assert len(df) == EXPECTED_LINE_COUNT


def test_vendas_lojas_receita_total():
    df = pd.read_csv(VENDAS_LOJAS_CSV)
    assert "receita_brl" in df.columns
    total = df["receita_brl"].sum()
    assert total == pytest.approx(EXPECTED_RECEITA_TOTAL, abs=TOLERANCE)


def test_pivot_shape_and_header():
    header = PIVOT_RECEITA_CSV.read_text(encoding="utf-8").splitlines()[0]
    assert header == "regiao,2026-01,2026-02,2026-03,2026-04,2026-05,2026-06"
    df = pd.read_csv(PIVOT_RECEITA_CSV)
    assert df.shape == (4, 7)
    assert list(df["regiao"]) == ["Centro-Oeste", "Nordeste", "Sudeste", "Sul"]


def test_pivot_total_and_format():
    df = pd.read_csv(PIVOT_RECEITA_CSV)
    assert df.drop(columns="regiao").to_numpy().sum() == pytest.approx(EXPECTED_RECEITA_TOTAL, abs=TOLERANCE)
    for line in PIVOT_RECEITA_CSV.read_text(encoding="utf-8").splitlines()[1:]:
        for cell in line.split(",")[1:]:
            assert len(cell.split(".")[1]) == 2


def test_index_html_canvas_chartjs_and_conclusion():
    assert INDEX_HTML.exists()
    html = INDEX_HTML.read_text(encoding="utf-8")
    assert "<canvas" in html
    assert "https://cdn.jsdelivr.net/npm/chart.js" in html
    paragraphs = re.findall(r"<p[^>]*>(.*?)</p>", html, flags=re.S)
    conclusao = max(paragraphs, key=len)
    assert len(conclusao) >= 300
    assert "Sudeste" in conclusao
    assert "R$ 265.077,49" in conclusao
    assert "R$ 931.274,06" in conclusao


def test_readme_documents_join_decision():
    readme = (INDEX_HTML.parent / "README.md").read_text(encoding="utf-8")
    for expected in ("python pipeline.py", "python -m pytest -q", "inner join", "999",
                     "R$ 8.120,00", "108", "Batel", "423", "420", "939394.06", "931274.06"):
        assert expected in readme
