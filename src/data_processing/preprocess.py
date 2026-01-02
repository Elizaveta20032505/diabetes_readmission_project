import pandas as pd
from pathlib import Path
import joblib
from diabetes_readmission_project.src.data_processing.clean_data import clean
from diabetes_readmission_project.src.data_processing.schema import save_schema

PROJECT_ROOT = Path(__file__).resolve().parents[2]
RAW_PATH = PROJECT_ROOT / "data/raw/diabetic_data.csv"
PROCESSED_PATH = PROJECT_ROOT / "data/processed/diabetic_data_processed.csv"

def preprocess():
    print("=== Загрузка исходного файла ===")
    df = pd.read_csv(RAW_PATH)
    print(f"Размер исходного датасета: {df.shape}")

    print("\n=== Анализ пропусков ===")
    missing = df.isna().sum()
    missing = missing[missing > 0]
    if missing.empty:
        print("Пропусков нет")
    else:
        print(missing.sort_values(ascending=False))

    print("\n=== Анализ странных значений ===")
    for col in ["race", "gender", "weight", "payer_code", "medical_specialty", "readmitted"]:
        if col in df.columns:
            unique_vals = df[col].unique()
            print(f"{col}: {len(unique_vals)} уникальных значений")
            print(f"Примеры: {unique_vals[:5]}")

    print("\n=== Очистка данных ===")
    df = clean(df)

    # анализ target
    print("\n=== Целевой признак (readmitted) до удаления ===")
    print(df["readmitted"].value_counts(dropna=False))

    # Пропуски только в target оставляем строго
    initial_rows = df.shape[0]
    df = df[~df["readmitted"].isna()]
    removed_rows = initial_rows - df.shape[0]
    print(f"Удалено {removed_rows} строк из-за пропусков в readmitted")

    print("\n=== Целевой признак (readmitted) после удаления ===")
    print(df["readmitted"].value_counts())

    # обработка категориальных пропусков без удаления строк
    categorical_cols = df.select_dtypes(include="object").columns.tolist()
    categorical_cols = [c for c in categorical_cols if c != "readmitted"]
    print(f"\nКатегориальные признаки: {len(categorical_cols)}")

    for c in categorical_cols:
        missing_count = df[c].isna().sum()
        if missing_count > 0:
            print(f"Заполнение пропусков в {c}: {missing_count}")
            df[c] = df[c].fillna("Unknown")

    # числовые пропуски
    numerical_cols = df.select_dtypes(exclude="object").columns.tolist()
    print(f"\nЧисловые признаки: {len(numerical_cols)}")
    for c in numerical_cols:
        missing_count = df[c].isna().sum()
        if missing_count > 0:
            print(f"Заполнение пропусков в {c}: {missing_count}")
            df[c] = df[c].fillna(0)

    print("\n=== Итоговый размер датасета ===")
    print(df.shape)

    PROCESSED_PATH.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(PROCESSED_PATH, index=False)

    save_schema(df)
    print("\n✔ Предобработка завершена")
    print(f"CSV: {PROCESSED_PATH}")
    print("schema.json создан")

if __name__ == "__main__":
    preprocess()
