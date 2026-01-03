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
