import streamlit as st
import pandas as pd
import joblib
from pathlib import Path

# Корень проекта (на 1 уровень выше frontend)
PROJECT_ROOT = Path(__file__).resolve().parents[1]

# Путь к модели
MODEL_PATH = PROJECT_ROOT / "models" / "catboost_top10.pkl"
model = joblib.load(MODEL_PATH)

# Топ-10 признаков (теперь с patient_nbr и diabetesMed, чтобы совпадало с моделью)
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

def predict_one(data: dict):
    df = pd.DataFrame([data])
    df = df[TOP10_FEATURES]

    # CatBoost требует строки для категориальных признаков
    for col in df.select_dtypes(include="object").columns:
        df[col] = df[col].astype(str)

    pred = model.predict(df)[0]
    prob = model.predict_proba(df).max()

    return {"prediction": pred, "probability": float(prob)}

# Streamlit UI
st.title("Прогноз повторной госпитализации диабетиков")

st.header("Введите данные пациента")

inputs = {}
for feature in TOP10_FEATURES:
    inputs[feature] = st.text_input(feature, "")

if st.button("Сделать предсказание"):
    if all(inputs.values()):
        result = predict_one(inputs)
        st.success(f"Предсказание: {result['prediction']}, вероятность: {result['probability']:.2f}")
    else:
        st.error("Пожалуйста, заполните все поля")
