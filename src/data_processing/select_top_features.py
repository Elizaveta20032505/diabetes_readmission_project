import pandas as pd
from pathlib import Path
from sklearn.preprocessing import OneHotEncoder

PROJECT_ROOT = Path(__file__).resolve().parents[2]
PROCESSED_PATH = PROJECT_ROOT / "data/processed/diabetic_data_processed.csv"
TOP10_PATH = PROJECT_ROOT / "data/processed/diabetic_data_top10.csv"
TOP10_ENCODED_PATH = PROJECT_ROOT / "data/processed/diabetic_data_top10_encoded.csv"

# Топ 10 признаков на основании корреляций, которые мы уже посчитали
NUMERICAL_TOP = ["number_inpatient", "number_diagnoses", "number_emergency",
                 "number_outpatient", "time_in_hospital"]
CATEGORICAL_TOP = ["diag_1", "diag_3", "diag_2", "medical_specialty", "diabetesMed"]

TOP_FEATURES = NUMERICAL_TOP + CATEGORICAL_TOP + ["readmitted"]  # оставляем target


def main():
    df = pd.read_csv(PROCESSED_PATH)
    df_top10 = df[TOP_FEATURES].copy()

    # ДОПОЛНИТЕЛЬНАЯ ОБРАБОТКА ПРОПУСКОВ В ТОП-10 ФАЙЛЕ
    print("Дополнительная обработка пропусков в топ-10 признаках...")

    # Числовые признаки - медианой (если остались пропуски)
    for col in NUMERICAL_TOP:
        if col in df_top10.columns:
            missing_count = df_top10[col].isna().sum()
            if missing_count > 0:
                median_val = df_top10[col].median()
                df_top10[col] = df_top10[col].fillna(median_val)
                print(f"✅ {col}: дополнительно заполнено {missing_count} пропусков медианой {median_val}")

    # Категориальные признаки - самым частым значением (если остались пропуски)
    for col in CATEGORICAL_TOP:
        if col in df_top10.columns:
            missing_count = df_top10[col].isna().sum()
            if missing_count > 0:
                mode_val = df_top10[col].mode().iloc[0] if not df_top10[col].mode().empty else "Unknown"
                df_top10[col] = df_top10[col].fillna(mode_val)
                print(f"✅ {col}: дополнительно заполнено {missing_count} пропусков значением '{mode_val}'")

    # Сохраняем таблицу с топ-10 признаками без кодирования
    TOP10_PATH.parent.mkdir(parents=True, exist_ok=True)
    df_top10.to_csv(TOP10_PATH, index=False)
    print(f"✔ Таблица с топ-10 признаками сохранена: {TOP10_PATH}")

    # Кодируем категориальные признаки для классических моделей
    cat_cols = CATEGORICAL_TOP
    df_encoded = pd.get_dummies(df_top10, columns=cat_cols, dummy_na=True)

    df_encoded.to_csv(TOP10_ENCODED_PATH, index=False)
    print(f"✔ Таблица с закодированными категориальными признаками сохранена: {TOP10_ENCODED_PATH}")


if __name__ == "__main__":
    main()
