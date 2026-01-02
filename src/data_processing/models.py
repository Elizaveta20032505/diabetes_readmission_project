from sqlalchemy import Column, Integer, Float
from .database import Base
from .schema import load_schema


schema = load_schema()


class PatientProcessed(Base):
    __tablename__ = "processed_records"

    id = Column(Integer, primary_key=True, index=True)

    for name, dtype in schema.items():
        if name == "readmitted":
            continue

        if dtype.startswith("float"):
            vars()[name] = Column(Float)
        else:
            vars()[name] = Column(Float)

    readmitted = Column(Integer)
