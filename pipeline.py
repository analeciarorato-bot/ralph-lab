"""Pipeline de vendas: junta vendas.csv e lojas.csv, agrega por regiao x mes e gera index.html."""
import pandas as pd

VENDAS_CSV = "vendas.csv"
LOJAS_CSV = "lojas.csv"
VENDAS_LOJAS_CSV = "vendas_lojas.csv"


def load_vendas() -> pd.DataFrame:
    return pd.read_csv(VENDAS_CSV, dtype={"id_loja": "int64"}).astype({"receita_brl": "float64"})


def load_lojas() -> pd.DataFrame:
    return pd.read_csv(LOJAS_CSV, dtype={"id_loja": "int64"})


def build_vendas_lojas() -> pd.DataFrame:
    vendas = load_vendas()
    lojas = load_lojas()
    return vendas.merge(lojas, on="id_loja", how="inner")


def main() -> None:
    vendas_lojas = build_vendas_lojas()
    vendas_lojas.to_csv(VENDAS_LOJAS_CSV, index=False)


if __name__ == "__main__":
    main()
