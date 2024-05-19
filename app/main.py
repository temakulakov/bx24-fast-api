import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import calendar
# from app.routers.calendar import router as calendar_router  # Импорт вашего ро

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Разрешить все источники, но вы можете указать конкретные источники
    allow_credentials=True,
    allow_methods=["*"],  # Разрешить все методы (GET, POST и т.д.)
    allow_headers=["*"],  # Разрешить все заголовки
)

app.include_router(calendar.router)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
