from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

import os


router = APIRouter()

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )
)

templates = Jinja2Templates(
    directory=os.path.join(BASE_DIR, "templates")
)


@router.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {"request": request}
    )


@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse(
        "login.html",
        {"request": request}
    )


@router.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse(
        "register.html",
        {"request": request}
    )


@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard_page(request: Request):
    return templates.TemplateResponse(
        "dashboard.html",
        {"request": request}
    )


@router.get("/history", response_class=HTMLResponse)
async def history_page(request: Request):
    return templates.TemplateResponse(
        "history.html",
        {"request": request}
    )


@router.get("/home-planner", response_class=HTMLResponse)
async def home_planner_page(request: Request):
    return templates.TemplateResponse(
        "home_planner.html",
        {"request": request}
    )


@router.get("/party-planner", response_class=HTMLResponse)
async def party_planner_page(request: Request):
    return templates.TemplateResponse(
        "party_planner.html",
        {"request": request}
    )


@router.get("/jewelry-planner", response_class=HTMLResponse)
async def jewelry_planner_page(request: Request):
    return templates.TemplateResponse(
        "jewelry_planner.html",
        {"request": request}
    )


@router.get("/recommendations", response_class=HTMLResponse)
async def recommendations_page(request: Request):
    return templates.TemplateResponse(
        "recommendations.html",
        {"request": request}
    )