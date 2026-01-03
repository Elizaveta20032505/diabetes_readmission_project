import joblib
import pandas as pd
import numpy as np
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

# Признаки, которые реально использует модель
TOP10_FEATURES = [
    "number_inpatient",
    "number_diagnoses",
    "number_emergency",
    "number_outpatient",
    "time_in_hospital",
    "diag_1",
    "diag_2",
    "diag_3",
    "medical_specialty",
    "diabetesMed"
]

# Загружаем модель один раз при старте
MODEL_PATH = PROJECT_ROOT / "models" / "catboost_top10.pkl"

# Загрузка модели с обработкой ошибок
try:
    model = joblib.load(MODEL_PATH)
except FileNotFoundError:
    model = None
    print(f"⚠️ Внимание: Модель не найдена по пути {MODEL_PATH}")
except Exception as e:
    model = None
    print(f"⚠️ Ошибка при загрузке модели: {e}")


def predict_one(data: dict):
    """
    data: словарь с данными пациента
    возвращает словарь с предсказанием и вероятностью
    """
    if model is None:
        raise ValueError("Модель не загружена. Убедитесь, что файл модели существует.")
    
    # Создаём DataFrame из словаря
    df = pd.DataFrame([data])

    # Оставляем только те признаки, которые ожидает модель
    df = df[TOP10_FEATURES]

    # Категориальные признаки: строковые
    categorical_features = ["diag_1", "diag_2", "diag_3", "medical_specialty", "diabetesMed"]
    for col in categorical_features:
        if col in df.columns:
            df[col] = df[col].astype(str)

    # Остальные признаки числовые (CatBoost принимает int/float)
    numeric_features = [col for col in TOP10_FEATURES if col not in categorical_features]
    for col in numeric_features:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')

    # Предсказание
    pred_array = model.predict(df)
    prob_array = model.predict_proba(df)
    
    # Извлекаем предсказание (model.predict возвращает numpy array)
    if isinstance(pred_array, np.ndarray):
        if pred_array.ndim == 0:  # скаляр
            pred = pred_array.item()
        else:  # массив
            pred = pred_array[0]
    elif isinstance(pred_array, (list, tuple)):
        pred = pred_array[0]
    else:
        pred = pred_array
    
    # Преобразуем в строку (убираем лишние символы если это строка-представление массива)
    pred_str = str(pred).strip()
    # Убираем квадратные скобки и кавычки если они есть
    pred_str = pred_str.replace("'", "").replace('"', '').replace('[', '').replace(']', '').strip()
    
    # Извлекаем максимальную вероятность из массива вероятностей
    if isinstance(prob_array, np.ndarray):
        if prob_array.ndim == 1:
            prob = float(prob_array.max())
        else:  # 2D array (samples x classes)
            prob = float(prob_array[0].max())
    elif isinstance(prob_array, (list, tuple)):
        if len(prob_array) > 0 and isinstance(prob_array[0], (list, tuple, np.ndarray)):
            prob = float(max(prob_array[0]))
        else:
            prob = float(max(prob_array))
    else:
        prob = float(prob_array)
    
    return {"prediction": pred_str, "probability": prob}
