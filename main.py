from pathlib import Path

from src.config import RAW_DATA, FIGURES_DIR
from src.load_data import load_data
from src.clean_data import clean_data
from src.plots import generate_all_plots


def main():
    project_root = Path(__file__).resolve().parent
    processed_dir = project_root / "data" / "processed"
    processed_dir.mkdir(parents=True, exist_ok=True)

    processed_file = processed_dir / "schoolverlaters_clean.csv"

    # 1. Raw data inladen
    df = load_data(RAW_DATA)

    # 2. Data opschonen
    df_clean = clean_data(df)

    # 3. Opslaan in processed map
    df_clean.to_csv(processed_file, sep=";", index=True)

    # 4. Vanuit processed data verder werken
    df_processed = load_data(processed_file)

    # 5. Output map aanmaken
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)

    # 6. Alle mogelijke plots maken
    generate_all_plots(df_processed, FIGURES_DIR)


if __name__ == "__main__":
    main()