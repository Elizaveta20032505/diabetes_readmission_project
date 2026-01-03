from fastapi import APIRouter, HTTPException, Query
from ...data_processing.load_data import load_top10_from_db
from ..utils.visualizations import AVAILABLE_CHARTS

router = APIRouter()


@router.get("/stats")
def stats():
    """
    Возвращает общую статистику по данным
    """
    try:
        df = load_top10_from_db()
        
        if df.empty:
            return {
                "rows": 0,
                "readmission_rate": 0.0,
                "features": 10,
                "message": "База данных пуста"
            }
        
        # Подсчитываем процент повторных госпитализаций
        readmission_count = df['readmitted'].isin(['<30', '>30']).sum()
        readmission_rate = (readmission_count / len(df)) * 100 if len(df) > 0 else 0.0
        
        return {
            "rows": len(df),
            "readmission_rate": round(readmission_rate, 2),
            "features": 10,
            "readmission_count": int(readmission_count),
            "no_readmission_count": int((df['readmitted'] == 'NO').sum())
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при загрузке статистики: {str(e)}")


@router.get("/chart")
def get_chart(chart_type: str = Query(..., description="Тип графика: readmission_by_diagnoses, readmission_by_inpatient_visits, readmission_by_diabetes_med")):
    """
    Возвращает график в формате base64 изображения
    
    Доступные типы графиков:
    - readmission_by_diagnoses: Зависимость повторных госпитализаций от количества диагнозов
    - readmission_by_inpatient_visits: Зависимость от количества стационарных визитов
    - readmission_by_diabetes_med: Зависимость от приема диабетических препаратов
    """
    try:
        # Проверяем, что тип графика существует
        if chart_type not in AVAILABLE_CHARTS:
            available_types = ", ".join(AVAILABLE_CHARTS.keys())
            raise HTTPException(
                status_code=400, 
                detail=f"Неизвестный тип графика: {chart_type}. Доступные типы: {available_types}"
            )
        
        # Загружаем данные
        df = load_top10_from_db()
        
        if df.empty:
            raise HTTPException(status_code=404, detail="База данных пуста. Загрузите данные через /data/upload")
        
        # Создаем график
        chart_func = AVAILABLE_CHARTS[chart_type]
        result = chart_func(df)
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при создании графика: {str(e)}")


@router.get("/charts/list")
def list_charts():
    """
    Возвращает список доступных графиков
    """
    return {
        "available_charts": [
            {
                "type": "readmission_by_diagnoses",
                "name": "Зависимость повторных госпитализаций от количества диагнозов",
                "description": "Показывает, как количество диагнозов влияет на вероятность повторной госпитализации"
            },
            {
                "type": "readmission_by_inpatient_visits",
                "name": "Зависимость от количества стационарных визитов",
                "description": "Анализирует связь между количеством стационарных визитов и повторными госпитализациями"
            },
            {
                "type": "readmission_by_diabetes_med",
                "name": "Зависимость от приема диабетических препаратов",
                "description": "Сравнивает частоту повторных госпитализаций у пациентов с приемом и без приема препаратов"
            }
        ]
    }
