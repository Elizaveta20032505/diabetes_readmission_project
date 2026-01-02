import pandas as pd
from fastapi import APIRouter, UploadFile
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
UPLOAD_PATH = PROJECT_ROOT / "data" / "external" / "uploaded.csv"

router = APIRouter()


@router.post("/upload")
async def upload(file: UploadFile):
    df = pd.read_csv(file.file)

    UPLOAD_PATH.parent.mkdir(exist_ok=True)
    df.to_csv(UPLOAD_PATH, index=False)

    return {"rows": len(df), "stored_at": str(UPLOAD_PATH)}
