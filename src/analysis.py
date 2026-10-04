def average_income(df):
    return df["Bruto maandinkomen in euro"].mean()

def average_working_hours(df):
    return df["Aantal arbeidsuren per week"].mean()

def income_by_gender(df):
    return (
        df.groupby("Geslacht")["Bruto maandinkomen in euro"]
        .mean()
    )

def age_by_education(df):
    return (
        df.groupby("Gaan doen na vmbo")["Leeftijd"]
        .mean()
    )