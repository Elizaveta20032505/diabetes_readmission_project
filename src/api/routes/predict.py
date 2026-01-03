from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Dict, Any
from ...modeling.predict import predict_one, TOP10_FEATURES

router = APIRouter()


class Patient(BaseModel):
    data: Dict[str, Any] = Field(..., description="Данные пациента с топ-10 признаками")


@router.post("/predict")
def predict_route(patient: Patient):
    """
    Принимает JSON вида:
    {
        "data": {
            "number_inpatient": 1,
            "number_diagnoses": 5,
            "number_emergency": 0,
            "number_outpatient": 2,
            "time_in_hospital": 5,
            "diag_1": "250.83",
            "diag_2": "250.01",
            "diag_3": "Unknown",
            "medical_specialty": "Cardiology",
            "diabetesMed": "Yes"
        }
    }
    Возвращает:
    {
        "prediction": "NO" | "<30" | ">30",
        "prediction_category": "Нет повторной госпитализации" | "Повторная госпитализация в течение 30 дней" | "Повторная госпитализация более чем через 30 дней",
        "risk_level": "Низкий риск" | "Высокий риск" | "Средний риск",
        "probability": 0.68
    }
    """
    try:
        # Проверяем наличие всех необходимых признаков
        missing_features = set(TOP10_FEATURES) - set(patient.data.keys())
        if missing_features:
            raise HTTPException(
                status_code=400,
                detail=f"Отсутствуют обязательные признаки: {', '.join(missing_features)}"
            )
        
        # Выполняем предсказание
        result = predict_one(patient.data)
        
        # Нормализуем предсказание для читаемости
        prediction = result["prediction"]
        
        # Убираем лишние символы если это строка-представление массива
        prediction_str = str(prediction).strip()
        prediction_str = prediction_str.replace("'", "").replace('"', '').replace('[', '').replace(']', '').strip()
        
        # Определяем категорию и описание на основе значений целевого признака
        # Целевой признак readmitted имеет значения: "NO", "<30", ">30"
        pred_upper = prediction_str.upper()
        
        if pred_upper in ["NO", "N", "0", "FALSE"]:
            category = "Нет повторной госпитализации"
            risk_level = "Низкий риск"
        elif pred_upper in ["<30", "LESS30", "LESS_THAN_30"]:
            category = "Повторная госпитализация в течение 30 дней"
            risk_level = "Высокий риск"
        elif pred_upper in [">30", "MORE30", "GREATER30", "MORE_THAN_30"]:
            category = "Повторная госпитализация более чем через 30 дней"
            risk_level = "Средний риск"
        else:
            # Если формат неизвестен, показываем как есть
            category = f"Неизвестный формат: {prediction_str}"
            risk_level = "Неопределено"
        
        return {
            "status": "success",
            "prediction": prediction_str,
            "prediction_category": category,
            "risk_level": risk_level,
            "probability": round(result["probability"], 4),
            "message": f"{category}. Вероятность: {result['probability']:.2%}"
        }
        
    except HTTPException:
        raise
    except KeyError as e:
        raise HTTPException(status_code=400, detail=f"Ошибка в данных: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при выполнении предсказания: {str(e)}")
