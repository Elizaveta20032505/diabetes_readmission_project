import pandas as pd
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

# Список проверяемых файлов относительно PROJECT_ROOT
FILES = [
    "data/processed/diabetic_data_processed.csv",
    "data/processed/diabetic_data_top10.csv",
    "data/processed/diabetic_data_top10_encoded.csv"
]


def analyze_file(file_path: Path):
    if not file_path.exists():
        print(f"❌ Файл не найден: {file_path}")
        return

    df = pd.read_csv(file_path)
    print(f"\n=== Анализ файла: {file_path.name} ===")
    print(f"Размер: {df.shape}")

    print("\nТипы данных:")
    print(df.dtypes)

    print("\nКоличество пропусков по столбцам:")
    print(df.isna().sum())

    print("\nУникальные значения категориальных признаков (первые 5):")
    cat_cols = df.select_dtypes(include="object").columns
    for col in cat_cols:
        print(f"{col}: {df[col].dropna().unique()[:5]}")

    print("\nПервые 5 строк таблицы:")
    print(df.head(5))


def main():
    for f in FILES:
        file_path = PROJECT_ROOT / f
        analyze_file(file_path)

    print("\n✔ Проверка завершена для всех файлов.")


if __name__ == "__main__":
    main()
