from fastapi import APIRouter

from ...data_processing.load_data import load_processed

router = APIRouter()


@router.get("/stats")
def stats():
    df = load_processed()

    return {
        "rows": len(df),
        "readmission_rate": float(df["readmitted"].mean()),
        "features": len(df.columns) - 1,
    }
