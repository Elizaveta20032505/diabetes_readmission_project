"""
Модуль: src/api/app.py

Назначение:
    Главный файл FastAPI приложения. Инициализирует приложение, настраивает CORS,
    подключает роуты и обрабатывает ошибки.

Входные данные:
    - HTTP запросы к различным эндпоинтам API

Выходные данные:
    - JSON ответы от роутов
    - Документация API доступна по /docs (Swagger)

Использование:
    - Запускается через: uvicorn src.api.app:app --reload
    - Подключает роуты из src/api/routes/ (dashboard, predict, upload_data)
    - Настраивает CORS для работы с фронтендом
    - Обрабатывает глобальные ошибки
    - Используется фронтендом (frontend/app.py) для всех API запросов
"""
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import traceback
import sys

# Импортируем роуты
try:
    from .routes import dashboard, predict, upload_data
except Exception as e:
    print(f"Ошибка при импорте роутов: {e}")
    traceback.print_exc()
    sys.exit(1)

app = FastAPI(
    title="Diabetes Readmission API",
    description="API для анализа и прогнозирования повторных госпитализаций пациентов с диабетом",
    version="1.0.0"
)

# Настройка CORS для работы с фронтендом
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # В продакшене указать конкретные домены
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(upload_data.router, prefix="/data")
app.include_router(predict.router, prefix="/model")
app.include_router(dashboard.router, prefix="/dashboard")


@app.get("/")
def root():
    return {
        "msg": "API работает",
        "version": "1.0.0",
        "endpoints": {
            "data": "/data/upload - загрузка данных",
            "model": "/model/predict - предсказание",
            "dashboard": "/dashboard/stats - статистика, /dashboard/chart - графики"
        }
    }


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Глобальный обработчик ошибок"""
    error_traceback = traceback.format_exc()
    print(f"Ошибка: {exc}")
    print(error_traceback)
    
    return JSONResponse(
        status_code=500,
        content={
            "detail": f"Внутренняя ошибка сервера: {str(exc)}",
            "path": str(request.url),
            "type": type(exc).__name__
        }
    )
