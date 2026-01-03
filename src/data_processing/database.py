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
            # Финальная проверка пропусков перед загрузкой в БД
            missing_total = df.isna().sum().sum()
            if missing_total > 0:
                print(f"⚠️ Обнаружено {missing_total} пропусков в данных перед загрузкой в БД!")
                print("Заполняем пропуски...")

                # Числовые признаки - медианой
                numerical_cols = ['number_inpatient', 'number_diagnoses', 'number_emergency', 'number_outpatient', 'time_in_hospital']
                for col in numerical_cols:
                    if col in df.columns:
                        missing_count = df[col].isna().sum()
                        if missing_count > 0:
                            median_val = df[col].median()
                            df[col] = df[col].fillna(median_val)
                            print(f"  ✅ {col}: заполнено {missing_count} пропусков медианой {median_val}")

                # Категориальные признаки - самым частым значением
                categorical_cols = ['diag_1', 'diag_2', 'diag_3', 'medical_specialty', 'diabetesMed']
                for col in categorical_cols:
                    if col in df.columns:
                        missing_count = df[col].isna().sum()
                        if missing_count > 0:
                            mode_val = df[col].mode().iloc[0] if not df[col].mode().empty else "Unknown"
                            df[col] = df[col].fillna(mode_val)
                            print(f"  ✅ {col}: заполнено {missing_count} пропусков значением '{mode_val}'")

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
            print(f"Загружено {len(records)} записей в БД")
        else:
            print(f"В БД уже есть {count} записей")
    finally:
        db.close()
