import json
import os
import shutil
from datetime import datetime
from typing import Optional

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    Request,
    UploadFile,
)
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from ..auth import (
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)
from ..database import get_db
from ..fallback_data import (
    get_home_fallback,
    get_jewelry_fallback,
    get_party_fallback,
)
from ..models import RecommendationHistory, User
from ..recommendation_service import (
    get_home_budget_recommendations,
    get_jewelry_budget_recommendations,
    get_party_budget_recommendations,
)
from ..schemas import (
    HomeBudgetInput,
    JewelryBudgetInput,
    PartyBudgetInput,
    UserCreate,
    UserLogin,
)


router = APIRouter(prefix="/api", tags=["API"])


# ---------------------------------------------------------
# In-memory session storage
# ---------------------------------------------------------

active_sessions = {}


# ---------------------------------------------------------
# Authentication helpers
# ---------------------------------------------------------

def get_token_from_request(request: Request) -> Optional[str]:
    token = request.cookies.get("access_token")

    if token:
        return token

    authorization = request.headers.get("Authorization")

    if authorization and authorization.startswith("Bearer "):
        return authorization.split(" ", 1)[1]

    return None


def get_current_user(
    request: Request,
    db: Session = Depends(get_db),
):
    token = get_token_from_request(request)

    if not token:
        raise HTTPException(
            status_code=401,
            detail="Authentication required."
        )

    payload = decode_access_token(token)

    if not payload:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token."
        )

    username = payload.get("sub")

    if not username:
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication token."
        )

    user = (
        db.query(User)
        .filter(User.username == username)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=401,
            detail="User not found."
        )

    if username not in active_sessions:
        active_sessions[username] = {
            "username": username,
            "login_time": datetime.utcnow(),
            "last_activity": datetime.utcnow(),
            "user_data": {},
            "token": token,
        }

    active_sessions[username]["last_activity"] = datetime.utcnow()

    return user


# ---------------------------------------------------------
# Register
# ---------------------------------------------------------

@router.post("/register")
async def register(
    user_data: UserCreate,
    request: Request,
    db: Session = Depends(get_db),
):
    existing_username = (
        db.query(User)
        .filter(User.username == user_data.username)
        .first()
    )

    if existing_username:
        raise HTTPException(
            status_code=400,
            detail="Username already exists."
        )

    existing_email = (
        db.query(User)
        .filter(User.email == user_data.email)
        .first()
    )

    if existing_email:
        raise HTTPException(
            status_code=400,
            detail="Email already registered."
        )

    new_user = User(
        username=user_data.username,
        email=user_data.email,
        full_name=user_data.full_name,
        password_hash=hash_password(user_data.password),
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {
        "message": "Registration successful.",
        "username": new_user.username,
    }


# ---------------------------------------------------------
# Login
# ---------------------------------------------------------

@router.post("/login")
async def login(
    user_data: UserLogin,
    request: Request,
    db: Session = Depends(get_db),
):
    user = (
        db.query(User)
        .filter(User.username == user_data.username)
        .first()
    )

    if not user or not verify_password(
        user_data.password,
        user.password_hash,
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password."
        )

    token = create_access_token(
        {"sub": user.username}
    )

    active_sessions[user.username] = {
        "username": user.username,
        "login_time": datetime.utcnow(),
        "last_activity": datetime.utcnow(),
        "user_data": {},
        "token": token,
    }

    return {
        "message": "Login successful.",
        "access_token": token,
        "token_type": "bearer",
        "username": user.username,
    }


# ---------------------------------------------------------
# Token endpoint
# ---------------------------------------------------------

@router.post("/token")
async def token_login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    user = (
        db.query(User)
        .filter(User.username == form_data.username)
        .first()
    )

    if not user or not verify_password(
        form_data.password,
        user.password_hash,
    ):
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password.",
        )

    access_token = create_access_token(
        {"sub": user.username}
    )

    active_sessions[user.username] = {
        "username": user.username,
        "login_time": datetime.utcnow(),
        "last_activity": datetime.utcnow(),
        "user_data": {},
        "token": access_token,
    }

    return {
        "access_token": access_token,
        "token_type": "bearer",
    }


# ---------------------------------------------------------
# Logout
# ---------------------------------------------------------

@router.post("/logout")
async def logout(
    request: Request,
    current_user: User = Depends(get_current_user),
):
    username = current_user.username

    if username in active_sessions:
        del active_sessions[username]

    return {
        "message": "Logout successful."
    }


# ---------------------------------------------------------
# Session information
# ---------------------------------------------------------

@router.get("/session-info")
async def session_info(
    current_user: User = Depends(get_current_user),
):
    username = current_user.username

    session = active_sessions.get(username)

    if not session:
        raise HTTPException(
            status_code=404,
            detail="No active session found."
        )

    duration = (
        datetime.utcnow() - session["login_time"]
    ).total_seconds() / 60

    return {
        "username": username,
        "login_time": session["login_time"].isoformat(),
        "last_activity": session["last_activity"].isoformat(),
        "session_duration_minutes": round(duration, 2),
        "logged_in": True,
    }


# ---------------------------------------------------------
# Session data
# ---------------------------------------------------------

@router.post("/session-data")
async def update_session_data(
    data: dict,
    current_user: User = Depends(get_current_user),
):
    username = current_user.username

    if username not in active_sessions:
        raise HTTPException(
            status_code=404,
            detail="No active session found."
        )

    active_sessions[username]["user_data"].update(data)
    active_sessions[username]["last_activity"] = datetime.utcnow()

    return {
        "message": "Session data updated.",
        "data": active_sessions[username]["user_data"],
    }


@router.get("/session-data")
async def get_session_data(
    current_user: User = Depends(get_current_user),
):
    username = current_user.username

    session = active_sessions.get(username)

    if not session:
        raise HTTPException(
            status_code=404,
            detail="No active session found."
        )

    return {
        "username": username,
        "data": session["user_data"],
    }


# ---------------------------------------------------------
# Save recommendation history
# ---------------------------------------------------------

def save_history(
    db: Session,
    user: User,
    recommendation_type: str,
    input_data: dict,
    result: dict,
):
    history = RecommendationHistory(
        username=user.username,
        recommendation_type=recommendation_type,
        input_data=json.dumps(input_data),
        result_summary=json.dumps(result),
        user_id=user.id,
    )

    db.add(history)
    db.commit()


# ---------------------------------------------------------
# Home Planner
# ---------------------------------------------------------

@router.post("/generate-home")
async def generate_home(
    budget_input: HomeBudgetInput,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    username = current_user.username

    try:
        if username in active_sessions:
            active_sessions[username]["user_data"][
                "last_home_budget"
            ] = {
                "timestamp": datetime.utcnow().isoformat(),
                "budget": budget_input.total_budget,
                "requirements": {
                    "lights": budget_input.num_lights,
                    "fans": budget_input.num_fans,
                    "furniture": budget_input.num_furniture,
                    "dining_tables": budget_input.num_dining_tables,
                },
            }

        try:
            result = get_home_budget_recommendations(
                budget_input
            )
        except Exception:
            result = get_home_fallback(
                budget_input.total_budget
            )

        save_history(
            db=db,
            user=current_user,
            recommendation_type="home",
            input_data=budget_input.model_dump(),
            result=result,
        )

        return result

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating home recommendations: {exc}",
        )


# ---------------------------------------------------------
# Party Planner
# ---------------------------------------------------------

@router.post("/generate-party")
async def generate_party(
    budget_input: PartyBudgetInput,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    username = current_user.username

    try:
        if username in active_sessions:
            active_sessions[username]["user_data"][
                "last_party_budget"
            ] = {
                "timestamp": datetime.utcnow().isoformat(),
                "budget": budget_input.total_budget,
                "party_type": budget_input.party_type,
                "guests": budget_input.num_guests,
            }

        try:
            result = get_party_budget_recommendations(
                budget_input
            )
        except Exception:
            result = get_party_fallback(
                budget_input.total_budget
            )

        save_history(
            db=db,
            user=current_user,
            recommendation_type="party",
            input_data=budget_input.model_dump(),
            result=result,
        )

        return result

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating party recommendations: {exc}",
        )


# ---------------------------------------------------------
# Jewelry Planner
# ---------------------------------------------------------

UPLOAD_DIRECTORY = os.path.join(
    os.path.dirname(
        os.path.dirname(
            os.path.dirname(
                os.path.abspath(__file__)
            )
        )
    ),
    "uploads",
)

os.makedirs(UPLOAD_DIRECTORY, exist_ok=True)


@router.post("/generate-jewelry")
async def generate_jewelry(
    total_budget: float = Form(...),
    occasion: str = Form(...),
    preferences: Optional[str] = Form(None),
    image: Optional[UploadFile] = File(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        budget_input = JewelryBudgetInput(
            total_budget=total_budget,
            occasion=occasion,
            preferences=preferences,
        )

        image_path = None

        if image and image.filename:
            safe_filename = os.path.basename(
                image.filename
            )

            image_path = os.path.join(
                UPLOAD_DIRECTORY,
                safe_filename,
            )

            with open(image_path, "wb") as buffer:
                shutil.copyfileobj(
                    image.file,
                    buffer,
                )

        if current_user.username in active_sessions:
            active_sessions[current_user.username]["user_data"][
                "last_jewelry_budget"
            ] = {
                "timestamp": datetime.utcnow().isoformat(),
                "budget": total_budget,
                "occasion": occasion,
                "has_image": image is not None,
            }

        try:
            result = get_jewelry_budget_recommendations(
                budget_input,
                image_path,
            )
        except Exception:
            result = get_jewelry_fallback(
                total_budget
            )

        input_data = budget_input.model_dump()

        if image:
            input_data["image"] = image.filename

        save_history(
            db=db,
            user=current_user,
            recommendation_type="jewelry",
            input_data=input_data,
            result=result,
        )

        return result

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating jewelry recommendations: {exc}",
        )


# ---------------------------------------------------------
# Recommendation history
# ---------------------------------------------------------

@router.get("/history")
async def get_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    records = (
        db.query(RecommendationHistory)
        .filter(
            RecommendationHistory.username
            == current_user.username
        )
        .order_by(
            RecommendationHistory.created_at.desc()
        )
        .all()
    )

    history = []

    for record in records:
        try:
            input_data = json.loads(record.input_data)
        except Exception:
            input_data = {}

        try:
            result = json.loads(record.result_summary)
        except Exception:
            result = {}

        history.append({
            "id": record.id,
            "type": record.recommendation_type,
            "input_data": input_data,
            "result": result,
            "created_at": record.created_at.isoformat(),
        })

    return {
        "history": history
    }


@router.get("/recommendations-details")
async def recommendations_details(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return await get_history(
        current_user=current_user,
        db=db,
    )