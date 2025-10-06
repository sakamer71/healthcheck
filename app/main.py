import os
import yaml
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse, FileResponse
from app.api.routes import calorie_count, profile_rda
import openai

# Load configuration
with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)

# Initialize OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY", config["openai"]["api_key"])

# Get the absolute path to the static directory
current_dir = os.path.dirname(os.path.abspath(__file__))
static_dir = os.path.join(os.path.dirname(current_dir), 'static')

app = FastAPI()

app.mount("/static", StaticFiles(directory=static_dir), name='static')

@app.get("/")
async def root():
    return RedirectResponse(url="/static/index.html")

# Include the router with the /api prefix
app.include_router(calorie_count.router, prefix="/api")
app.include_router(profile_rda.router, prefix="/api", tags=["profile"])
