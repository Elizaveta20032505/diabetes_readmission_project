"""
Модуль: src/api/routes/upload_data.py

Назначение:
    Роуты FastAPI для загрузки и валидации данных пациентов в базу данных.

Входные данные (через HTTP POST запрос):
    - CSV файл с данными пациентов
    - Файл должен содержать все обязательные столбцы из REQUIRED_COLUMNS
    - Все значения должны быть заполнены (без пропусков)

Выходные данные (JSON ответ):
    - status: статус загрузки
    - message: сообщение о результате
    - rows_added: количество добавленных записей
    - total_rows_in_db: общее количество записей в БД после загрузки

Использование:
    - Подключается в src/api/app.py через app.include_router()
    - Используется фронтендом (frontend/app.py) в разделе "Загрузка данных"
    - Валидирует данные через validate_data()
    - Добавляет данные в БД через модель PatientTop10 из src/data_processing/models.py
    - Данные добавляются к существующим (не перезаписывают БД)
"""
import pandas as pd
from fastapi import APIRouter, UploadFile, HTTPException
from pathlib import Path
from ...data_processing.database import SessionLocal, init_db
from ...data_processing.models import PatientTop10

# Топ-10 признаков + целевой
REQUIRED_COLUMNS = [
    "number_inpatient",
    "number_diagnoses",
    "number_emergency",
    "number_outpatient",
    "time_in_hospital",
    "diag_1",
    "diag_2",
    "diag_3",
    "medical_specialty",
    "diabetesMed",
    "readmitted"
]

router = APIRouter()


def validate_data(df: pd.DataFrame) -> tuple[bool, str]:
    """
    Валидирует данные: проверяет наличие всех необходимых столбцов
    и отсутствие пропусков в них.
    
    Returns:
        (is_valid, error_message)
    """
    # Проверка наличия всех столбцов
    missing_cols = set(REQUIRED_COLUMNS) - set(df.columns)
    if missing_cols:
        return False, f"Отсутствуют обязательные столбцы: {', '.join(missing_cols)}"
    
    # Проверка на пропуски в обязательных столбцах
    missing_data = df[REQUIRED_COLUMNS].isna().any(axis=1)
    if missing_data.any():
        rows_with_missing = missing_data.sum()
        return False, f"Обнаружены пропуски в данных. Количество строк с пропусками: {rows_with_missing}. Все столбцы должны быть заполнены."
    
    return True, ""


@router.post("/upload")
async def upload(file: UploadFile):
    """
    Загружает данные из CSV файла, валидирует их и добавляет в БД.
    
    Требования:
    - Файл должен содержать все столбцы из топ-10 признаков + readmitted
    - Все значения должны быть заполнены (без пропусков)
    """
    try:
        # Читаем файл
        try:
            df = pd.read_csv(file.file)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Ошибка чтения CSV файла: {str(e)}")
        
        if df.empty:
            raise HTTPException(status_code=400, detail="Файл пустой")
        
        # Валидация данных
        is_valid, error_message = validate_data(df)
        if not is_valid:
            raise HTTPException(status_code=400, detail=error_message)
        
        # Инициализируем БД если нужно
        init_db()
        
        # Добавляем данные в БД
        db = SessionLocal()
        try:
            records = []
            for _, row in df.iterrows():
                record = PatientTop10(
                    number_inpatient=int(row['number_inpatient']),
                    number_diagnoses=int(row['number_diagnoses']),
                    number_emergency=int(row['number_emergency']),
                    number_outpatient=int(row['number_outpatient']),
                    time_in_hospital=int(row['time_in_hospital']),
                    diag_1=str(row['diag_1']),
                    diag_2=str(row['diag_2']),
                    diag_3=str(row['diag_3']),
                    medical_specialty=str(row['medical_specialty']),
                    diabetesMed=str(row['diabetesMed']),
                    readmitted=str(row['readmitted'])
                )
                records.append(record)
            
            db.bulk_save_objects(records)
            db.commit()
            
            return {
                "status": "success",
                "message": "Данные успешно загружены в БД",
                "rows_added": len(records),
                "total_rows_in_db": db.query(PatientTop10).count()
            }
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=500, detail=f"Ошибка при добавлении данных в БД: {str(e)}")
        finally:
            db.close()
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Неожиданная ошибка: {str(e)}")
