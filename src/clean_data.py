import pandas as pd


def clean_data(df):
    df = df.copy()

    # Kolomnamen opschonen
    df.columns = df.columns.str.strip()

    # Vervang '*' door NaN
    df.replace("*", pd.NA, inplace=True)

    # Hernoem kolommen voor duidelijkheid
    df.rename(columns={
        "Vragenlijstnummer": "Opleidingsniveau",  # Hernoem naar iets logischer
        "Leeftijd": "Leeftijd",
        "Aantal arbeidsuren per week": "Arbeidsuren_per_week",
        "Bruto maandinkomen in euro": "Bruto_maandinkomen"
    }, inplace=True)

    # Getallen daadwerkelijk als getallen opslaan
    df["Leeftijd"] = pd.to_numeric(
        df["Leeftijd"],
        errors="coerce"
    )

    df["Arbeidsuren_per_week"] = pd.to_numeric(
        df["Arbeidsuren_per_week"],
        errors="coerce"
    )

    df["Bruto_maandinkomen"] = pd.to_numeric(
        df["Bruto_maandinkomen"],
        errors="coerce"
    )

    return df