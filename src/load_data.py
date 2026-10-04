import pandas as pd

def load_data(filepath):
    df = pd.read_csv(
        filepath,
        sep=";",
        encoding="utf-8-sig",
        header=0
    )

    if "Nr" in df.columns:
        df = df.set_index("Nr")

    return df