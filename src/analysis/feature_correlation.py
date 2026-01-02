import pandas as pd
import numpy as np
from scipy.stats import chi2_contingency
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
PROCESSED_PATH = PROJECT_ROOT / "data/processed/diabetic_data_processed.csv"

def cramers_v(x, y):
    """Cramér's V для категориальных переменных"""
    confusion_matrix = pd.crosstab(x, y)
    chi2 = chi2_contingency(confusion_matrix)[0]
    n = confusion_matrix.sum().sum()
    phi2 = chi2 / n
    r, k = confusion_matrix.shape
    return np.sqrt(phi2 / (min(k - 1, r - 1) + 1e-10))

def main():
    df = pd.read_csv(PROCESSED_PATH)
    print(f"Размер датасета: {df.shape}\n")

    # Кодируем target в числовой для корреляций
    target_map = {"NO": 0, "<30": 1, ">30": 2}
    df["readmitted_num"] = df["readmitted"].map(target_map)

    # Числовые признаки
    numerical = df.select_dtypes(exclude="object").columns.tolist()
    numerical = [c for c in numerical if c != "readmitted_num"]

    print("=== Корреляция Пирсона для числовых признаков ===")
    corr_num = {}
    for col in numerical:
        corr = df[col].corr(df["readmitted_num"])
        corr_num[col] = abs(corr)
    corr_num_sorted = dict(sorted(corr_num.items(), key=lambda item: item[1], reverse=True))
    for k, v in corr_num_sorted.items():
        print(f"{k}: {v:.3f}")

    # Категориальные признаки
    categorical = df.select_dtypes(include="object").columns.tolist()
    categorical = [c for c in categorical if c != "readmitted"]

    print("\n=== Cramér's V для категориальных признаков ===")
    corr_cat = {}
    for col in categorical:
        v = cramers_v(df[col], df["readmitted"])
        corr_cat[col] = v
    corr_cat_sorted = dict(sorted(corr_cat.items(), key=lambda item: item[1], reverse=True))
    for k, v in corr_cat_sorted.items():
        print(f"{k}: {v:.3f}")

if __name__ == "__main__":
    main()
