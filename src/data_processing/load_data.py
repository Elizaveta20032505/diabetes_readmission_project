"""
Модуль: src/data_processing/load_data.py

Назначение:
    Функции для загрузки данных из базы данных или CSV файлов.

Входные данные:
    - load_top10_from_db(): без параметров, загружает из БД
    - load_processed(): без параметров, загружает из CSV (для обратной совместимости)

Выходные данные:
    - DataFrame с данными пациентов (топ-10 признаков + readmitted)
    - Если БД пустая, возвращает данные из CSV файла

Использование:
    - Используется в src/api/routes/dashboard.py для получения данных для графиков
    - Используется в src/api/routes/upload_data.py для проверки данных
    - Автоматически инициализирует БД через init_db() если нужно
    - Преобразует записи из БД в DataFrame для удобной работы
"""
import pandas as pd
from pathlib import Path
from .database import SessionLocal, init_db
from .models import PatientTop10

PROJECT_ROOT = Path(__file__).resolve().parents[2]
PROCESSED_PATH = PROJECT_ROOT / "data" / "processed" / "diabetic_data_processed.csv"
TOP10_CSV_PATH = PROJECT_ROOT / "data" / "processed" / "diabetic_data_top10.csv"


def load_processed():
    """Загружает обработанные данные из CSV (для обратной совместимости)"""
    from .schema import load_schema
    schema = load_schema()
    df = pd.read_csv(PROCESSED_PATH)
    return df


def load_top10_from_db():
    """
    Загружает данные с топ-10 признаками из БД.
    Инициализирует БД если нужно.
    """
    init_db()
    db = SessionLocal()
    try:
        records = db.query(PatientTop10).all()
        if not records:
            # Если БД пустая, загружаем из CSV
            if TOP10_CSV_PATH.exists():
                df = pd.read_csv(TOP10_CSV_PATH)
                return df
            else:
                return pd.DataFrame()
        
        # Преобразуем записи в DataFrame
        data = []
        for record in records:
            data.append({
                'number_inpatient': record.number_inpatient,
                'number_diagnoses': record.number_diagnoses,
                'number_emergency': record.number_emergency,
                'number_outpatient': record.number_outpatient,
                'time_in_hospital': record.time_in_hospital,
                'diag_1': record.diag_1,
                'diag_2': record.diag_2,
                'diag_3': record.diag_3,
                'medical_specialty': record.medical_specialty,
                'diabetesMed': record.diabetesMed,
                'readmitted': record.readmitted
            })
        
        return pd.DataFrame(data)
    finally:
        db.close()


if __name__ == "__main__":
    df = load_top10_from_db()
    print(df.head())
