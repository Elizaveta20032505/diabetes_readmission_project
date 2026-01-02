import pandas as pd
from pathlib import Path

from .schema import load_schema

PROJECT_ROOT = Path(__file__).resolve().parents[2]
PROCESSED_PATH = PROJECT_ROOT / "data" / "processed" / "diabetic_data_processed.csv"


def load_processed():
    schema = load_schema()

    df = pd.read_csv(PROCESSED_PATH)

    return df


if __name__ == "__main__":
    df = load_processed()
    print(df.head())
