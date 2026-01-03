"""
Модуль: src/data_processing/models.py

Назначение:
    Определяет модель SQLAlchemy для таблицы БД с топ-10 признаками и целевым признаком.

Входные данные:
    - Используется при создании записей в БД через SQLAlchemy ORM

Выходные данные:
    - Класс PatientTop10 для работы с таблицей patients_top10 в БД

Использование:
    - Используется в src/data_processing/database.py для создания таблицы
    - Используется в src/api/routes/upload_data.py для добавления данных
    - Используется в src/data_processing/load_data.py для загрузки данных из БД
    - Таблица содержит 10 признаков + целевой признак readmitted
"""
from sqlalchemy import Column, Integer, Float, String
from .database import Base

# Топ-10 признаков + целевой (readmitted)
# Числовые признаки
NUMERICAL_FEATURES = [
    "number_inpatient",
    "number_diagnoses", 
    "number_emergency",
    "number_outpatient",
    "time_in_hospital"
]

# Категориальные признаки
CATEGORICAL_FEATURES = [
    "diag_1",
    "diag_2",
    "diag_3",
    "medical_specialty",
    "diabetesMed"
]

# Все признаки для БД
ALL_FEATURES = NUMERICAL_FEATURES + CATEGORICAL_FEATURES


class PatientTop10(Base):
    """
    Модель для хранения данных с топ-10 признаками + целевой признак readmitted
    """
    __tablename__ = "patients_top10"

    id = Column(Integer, primary_key=True, index=True)
    
    # Числовые признаки
    number_inpatient = Column(Integer)
    number_diagnoses = Column(Integer)
    number_emergency = Column(Integer)
    number_outpatient = Column(Integer)
    time_in_hospital = Column(Integer)
    
    # Категориальные признаки
    diag_1 = Column(String)
    diag_2 = Column(String)
    diag_3 = Column(String)
    medical_specialty = Column(String)
    diabetesMed = Column(String)
    
    # Целевой признак
    readmitted = Column(String)
