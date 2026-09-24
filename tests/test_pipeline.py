import subprocess
import sys
from pathlib import Path

import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parent.parent
VENDAS_LOJAS_CSV = ROOT / "vendas_lojas.csv"

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
