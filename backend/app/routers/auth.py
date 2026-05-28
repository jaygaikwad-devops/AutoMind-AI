from fastapi import APIRouter, HTTPException
from app.schemas import UserCreate, Token, UserOut
from app.core.security import hash_password, verify_password, create_access_token

router = APIRouter()

# In-memory placeholder store; replace with SQLAlchemy session.
_USERS: dict[str, dict] = {}


@router.post("/register", response_model=Token)
async def register(body: UserCreate):
    if body.email in _USERS:
        raise HTTPException(400, "Email already registered")
    _USERS[body.email] = {"id": body.email, "email": body.email, "password_hash": hash_password(body.password), "plan": "starter"}
    return Token(access_token=create_access_token(body.email))


@router.post("/login", response_model=Token)
async def login(body: UserCreate):
    u = _USERS.get(body.email)
    if not u or not verify_password(body.password, u["password_hash"]):
        raise HTTPException(401, "Invalid credentials")
    return Token(access_token=create_access_token(body.email))


@router.get("/me", response_model=UserOut)
async def me():
    # TODO: wire JWT dependency
    return UserOut(id="demo", email="demo@automind.ai", plan="growth")
