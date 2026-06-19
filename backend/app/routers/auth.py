"""
Auth router — register, login, logout, me.

Cookie strategy:
  - In production (HTTPS via nginx): secure=True, samesite="none", domain from config
  - In development (HTTP localhost): secure=False, samesite="lax"

Since nginx proxies both frontend (/) and backend (/api/) on the same domain
(automindai.info), cookies are first-party. samesite="lax" works fine in this
setup, but we also set secure=True because the connection is HTTPS.
"""
from fastapi import APIRouter, Depends, HTTPException, Response, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db import get_db
from app.models import User
from app.schemas import UserCreate, UserOut
from app.core import security
from app.core.config import settings
from app.api.deps import get_current_user

router = APIRouter()


def _is_production() -> bool:
    """Detect production by checking if automindai.info is in CORS origins."""
    return any("automindai.info" in origin for origin in settings.CORS_ORIGINS)


def _set_auth_cookie(response: Response, token: str) -> None:
    """Set the access_token cookie with correct attributes for the environment."""
    is_prod = _is_production()
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        secure=is_prod,                         # True in prod (HTTPS), False in dev (HTTP)
        samesite="lax",                         # lax works because nginx serves same domain
        max_age=settings.JWT_EXPIRE_MINUTES * 60,
        path="/",                               # Cookie available on all paths
    )


@router.post("/register", response_model=UserOut)
async def register(user_in: UserCreate, response: Response, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).filter(User.email == user_in.email))
    user = result.scalars().first()
    if user:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_password = security.hash_password(user_in.password)
    new_user = User(email=user_in.email, password_hash=hashed_password)
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    # Auto-login after registration
    token = security.create_access_token(sub=new_user.id)
    _set_auth_cookie(response, token)
    return new_user


@router.post("/login")
async def login(user_in: UserCreate, response: Response, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).filter(User.email == user_in.email))
    user = result.scalars().first()
    if not user or not security.verify_password(user_in.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Incorrect email or password")

    token = security.create_access_token(sub=user.id)
    _set_auth_cookie(response, token)
    return {"message": "Logged in successfully", "user_id": user.id, "email": user.email}


@router.post("/logout")
async def logout(response: Response):
    response.delete_cookie(
        key="access_token",
        path="/",
        httponly=True,
        samesite="lax",
    )
    return {"message": "Logged out successfully"}


@router.get("/me", response_model=UserOut)
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user
