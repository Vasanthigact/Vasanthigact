import os

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from .database import Base, engine
from .routers import api, pages

load_dotenv()

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="PocketSmart AI",
    description="AI-Powered Budget Planning for Everyday Needs",
    version="1.0.0",
)

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

TEMPLATES_DIR = os.path.join(
    BASE_DIR,
    "templates"
)

STATIC_DIR = os.path.join(
    BASE_DIR,
    "static"
)

templates = Jinja2Templates(
    directory=TEMPLATES_DIR
)

app.mount(
    "/static",
    StaticFiles(directory=STATIC_DIR),
    name="static",
)

# Page routes
app.include_router(pages.router)

# API routes
app.include_router(api.router)


@app.get("/health")
async def health_check():
    return {
        "status": "ok",
        "message": "PocketSmart AI is running"
    }