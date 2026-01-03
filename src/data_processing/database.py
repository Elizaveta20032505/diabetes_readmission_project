"""
Модуль: src/data_processing/database.py

Назначение:
    Настройка подключения к базе данных SQLite и инициализация БД.

Входные данные:
    - init_db(): автоматически вызывается при первом использовании
    - CSV файл data/processed/diabetic_data_top10.csv для начальной загрузки

Выходные данные:
    - engine: SQLAlchemy engine для подключения к БД
    - SessionLocal: фабрика сессий для работы с БД
    - Base: базовый класс для моделей SQLAlchemy
    - init_db(): создает таблицы и загружает начальные данные если БД пустая

Использование:
    - Используется во всех модулях для работы с БД (models.py, load_data.py, upload_data.py)
    - БД автоматически инициализируется при первом использовании
    - Если БД пустая, загружает данные из CSV файла
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from pathlib import Path
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DB_PATH = PROJECT_ROOT / "data" / "processed" / "diabetes.db"
TOP10_CSV_PATH = PROJECT_ROOT / "data" / "processed" / "diabetic_data_top10.csv"

engine = create_engine(f"sqlite:///{DB_PATH}", echo=False)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def init_db():
    """
    Инициализирует БД: создает таблицы и загружает начальные данные из CSV
    если таблица пустая
    """
    from .models import PatientTop10
    
    # Создаем таблицы
    Base.metadata.create_all(bind=engine)
    
    # Проверяем, есть ли уже данные в БД
    db = SessionLocal()
    try:
        count = db.query(PatientTop10).count()
        if count == 0 and TOP10_CSV_PATH.exists():
            # Загружаем начальные данные из CSV
            print(f"Загрузка начальных данных из {TOP10_CSV_PATH}")
            df = pd.read_csv(TOP10_CSV_PATH)
            
            # Преобразуем DataFrame в список объектов
            records = []
            for _, row in df.iterrows():
                record = PatientTop10(
                    number_inpatient=int(row['number_inpatient']) if pd.notna(row['number_inpatient']) else 0,
                    number_diagnoses=int(row['number_diagnoses']) if pd.notna(row['number_diagnoses']) else 0,
                    number_emergency=int(row['number_emergency']) if pd.notna(row['number_emergency']) else 0,
                    number_outpatient=int(row['number_outpatient']) if pd.notna(row['number_outpatient']) else 0,
                    time_in_hospital=int(row['time_in_hospital']) if pd.notna(row['time_in_hospital']) else 0,
                    diag_1=str(row['diag_1']) if pd.notna(row['diag_1']) else 'Unknown',
                    diag_2=str(row['diag_2']) if pd.notna(row['diag_2']) else 'Unknown',
                    diag_3=str(row['diag_3']) if pd.notna(row['diag_3']) else 'Unknown',
                    medical_specialty=str(row['medical_specialty']) if pd.notna(row['medical_specialty']) else 'Unknown',
                    diabetesMed=str(row['diabetesMed']) if pd.notna(row['diabetesMed']) else 'Unknown',
                    readmitted=str(row['readmitted']) if pd.notna(row['readmitted']) else 'NO'
                )
                records.append(record)
            
            db.bulk_save_objects(records)
            db.commit()
            print(f"Загружено {len(records)} записей в БД")
        else:
            print(f"В БД уже есть {count} записей")
    finally:
        db.close()
