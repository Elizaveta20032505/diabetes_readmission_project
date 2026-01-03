"""
Модуль: src/api/routes/dashboard.py

Назначение:
    Роуты FastAPI для работы с дашбордом: получение статистики и построение графиков.

Входные данные (через HTTP запросы):
    - GET /dashboard/stats: без параметров
    - GET /dashboard/chart?chart_type={type}: тип графика (обязательный)
    - GET /dashboard/chart?chart_type=custom&feature={name}&chart_style={style}: произвольный график
    - GET /dashboard/charts/list: без параметров

Выходные данные (JSON ответы):
    - stats(): словарь со статистикой (rows, readmission_rate, features, etc.)
    - get_chart(): словарь с графиком (chart_type, title, image_base64, data)
    - list_charts(): список доступных графиков

Использование:
    - Подключается в src/api/app.py через app.include_router()
    - Используется фронтендом (frontend/app.py) для получения статистики и графиков
    - Данные загружаются из БД через src/data_processing/load_data.py
    - Графики строятся через src/api/utils/visualizations.py
"""
from fastapi import APIRouter, HTTPException, Query
from ...data_processing.load_data import load_top10_from_db
from ..utils.visualizations import AVAILABLE_CHARTS, create_custom_chart

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
        
        # Разбивка по категориям
        no_readmission = int((df['readmitted'] == 'NO').sum())
        readmission_less_30 = int((df['readmitted'] == '<30').sum())
        readmission_more_30 = int((df['readmitted'] == '>30').sum())
        
        return {
            "rows": len(df),
            "readmission_rate": round(readmission_rate, 2),
            "features": 10,
            "no_readmission": no_readmission,
            "readmission_less_30": readmission_less_30,
            "readmission_more_30": readmission_more_30
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при загрузке статистики: {str(e)}")


@router.get("/chart")
def get_chart(
    chart_type: str = Query(..., description="Тип графика: readmission_by_diagnoses, readmission_by_inpatient_visits, readmission_by_diabetes_med, custom"),
    feature: str = Query(None, description="Признак для произвольного графика (только для chart_type=custom)"),
    chart_style: str = Query("bar", description="Стиль графика для произвольного: bar, line, pie (только для chart_type=custom)")
):
    """
    Возвращает график в формате base64 изображения
    
    Доступные типы графиков:
    - readmission_by_diagnoses: Зависимость повторных госпитализаций от количества диагнозов
    - readmission_by_inpatient_visits: Зависимость от количества стационарных визитов
    - readmission_by_diabetes_med: Зависимость от приема диабетических препаратов
    - custom: Произвольный график (требует параметр feature)
    """
    try:
        # Загружаем данные
        df = load_top10_from_db()
        
        if df.empty:
            raise HTTPException(status_code=404, detail="База данных пуста. Загрузите данные через /data/upload")
        
        # Обработка произвольного графика
        if chart_type == "custom":
            if not feature:
                raise HTTPException(
                    status_code=400,
                    detail="Для произвольного графика необходимо указать параметр 'feature'"
                )
            if feature not in df.columns:
                available_features = ", ".join([col for col in df.columns if col != 'readmitted'])
                raise HTTPException(
                    status_code=400,
                    detail=f"Признак '{feature}' не найден. Доступные признаки: {available_features}"
                )
            result = create_custom_chart(df, feature, chart_style)
        else:
            # Проверяем, что тип графика существует
            if chart_type not in AVAILABLE_CHARTS:
                available_types = ", ".join([k for k in AVAILABLE_CHARTS.keys() if k != "custom"])
                raise HTTPException(
                    status_code=400, 
                    detail=f"Неизвестный тип графика: {chart_type}. Доступные типы: {available_types}, custom"
                )
            
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
            },
            {
                "type": "custom",
                "name": "Произвольный график",
                "description": "Построение графика зависимости от любого признака из данных"
            }
        ]
    }
