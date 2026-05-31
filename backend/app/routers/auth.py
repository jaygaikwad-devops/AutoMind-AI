from fastapi import APIRouter, Depends, HTTPException, Response, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db import get_db
from app.models import User
from app.schemas import UserCreate, UserOut
from app.core import security
from app.api.deps import get_current_user

router = APIRouter()

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
    response.set_cookie(key="access_token", value=token, httponly=True, samesite="lax", max_age=security.settings.JWT_EXPIRE_MINUTES * 60)
    return new_user

@router.post("/login")
async def login(user_in: UserCreate, response: Response, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).filter(User.email == user_in.email))
    user = result.scalars().first()
    if not user or not security.verify_password(user_in.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Incorrect email or password")
        
    token = security.create_access_token(sub=user.id)
    response.set_cookie(key="access_token", value=token, httponly=True, samesite="lax", max_age=security.settings.JWT_EXPIRE_MINUTES * 60)
    return {"message": "Logged in successfully"}

@router.post("/logout")
async def logout(response: Response):
    response.delete_cookie("access_token")
    return {"message": "Logged out successfully"}

@router.get("/me", response_model=UserOut)
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user
