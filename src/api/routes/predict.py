from fastapi import APIRouter
from pydantic import BaseModel
from ...modeling.predict import predict_one

router = APIRouter()


class Patient(BaseModel):
    data: dict


@router.post("/predict")
def predict_route(patient: Patient):
    """
    Принимает JSON вида:
    {
        "data": {
            "number_inpatient": 1,
            "number_diagnoses": 5,
            ...
        }
    }
    Возвращает:
    {
        "prediction": "YES",
        "probability": 0.68
    }
    """
    return predict_one(patient.data)
