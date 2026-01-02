from fastapi import FastAPI

from .routes import dashboard, predict, upload_data

app = FastAPI(title="Diabetes Readmission API")

app.include_router(upload_data.router, prefix="/data")
app.include_router(predict.router, prefix="/model")
app.include_router(dashboard.router, prefix="/dashboard")


@app.get("/")
def root():
    return {"msg": "API работает"}
