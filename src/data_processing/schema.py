import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SCHEMA_PATH = PROJECT_ROOT / "data" / "processed" / "schema.json"


def save_schema(df):
    schema = {
        "columns": [
            {"name": col, "dtype": str(df[col].dtype)}
            for col in df.columns
        ]
    }

    SCHEMA_PATH.parent.mkdir(parents=True, exist_ok=True)

    with open(SCHEMA_PATH, "w", encoding="utf-8") as f:
        json.dump(schema, f, indent=4)


def load_schema():
    if not SCHEMA_PATH.exists():
        raise FileNotFoundError(
            f"⚠ schema.json не найден. "
            f"Сначала запусти: preprocess.py"
        )

    with open(SCHEMA_PATH, encoding="utf-8") as f:
        return json.load(f)
