import pandas as pd
from pathlib import Path


DATA_PATH = Path(__file__).resolve().parents[2] / "data" / "raw" / "diabetic_data.csv"


def main():
    print("=== Загрузка данных ===")
    df = pd.read_csv(DATA_PATH)

    print("\n=== Размер датасета ===")
    print(df.shape)

    print("\n=== Первые строки ===")
    print(df.head())

    print("\n=== Типы признаков ===")
    print(df.dtypes)

    print("\n=== Описание числовых признаков ===")
    print(df.describe())

    print("\n=== Количество пропусков по столбцам ===")
    print(df.isna().sum())

    print("\n=== Баланс целевого признака (readmitted) ===")
    print(df["readmitted"].value_counts())

    print("\n=== Уникальные значения целевого признака ===")
    print(df["readmitted"].unique())


if __name__ == "__main__":
    main()
