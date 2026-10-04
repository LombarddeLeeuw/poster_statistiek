from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

RAW_DATA = BASE_DIR / "data" / "raw" / "Schoolverlaters dataset.csv"
PROCESSED_DATA = BASE_DIR / "data" / "processed" / "schoolverlaters_clean.csv"

FIGURES_DIR = BASE_DIR / "output" / "figures"