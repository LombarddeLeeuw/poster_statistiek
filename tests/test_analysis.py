from src.analysis import average_income


def test_average_income():
    data = {
        "Bruto maandinkomen in euro": [2000, 3000, 4000]
    }

    import pandas as pd

    df = pd.DataFrame(data)

    result = average_income(df)

    assert result == 3000