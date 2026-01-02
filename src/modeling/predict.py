import joblib
import pandas as pd
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

# Фичи, которые реально использует модель
TOP10_FEATURES = [
    "number_inpatient",
    "number_diagnoses",
    "number_emergency",
    "number_outpatient",
    "patient_nbr",
    "diag_1",
    "diag_2",
    "diag_3",
    "medical_specialty",
    "diabetesMed"
]

# Загружаем модель один раз при старте
MODEL_PATH = PROJECT_ROOT / "models" / "catboost_top10.pkl"
model = joblib.load(MODEL_PATH)


def predict_one(data: dict):
    """
    data: словарь с данными пациента
    возвращает словарь с предсказанием и вероятностью
    """
    df = pd.DataFrame([data])
    # Оставляем только те признаки, которые ожидает модель
    df = df[TOP10_FEATURES]

    # CatBoost требует строки для категориальных признаков
    for col in df.select_dtypes(include="object").columns:
        df[col] = df[col].astype(str)

    pred = model.predict(df)[0]
    prob = model.predict_proba(df).max()

    return {"prediction": pred, "probability": float(prob)}
