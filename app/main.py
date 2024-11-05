from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.api.routes import calorie_count



app = FastAPI()

app.mount("/static", StaticFiles(directory='static'), name='static')

app.include_router(calorie_count.router)
