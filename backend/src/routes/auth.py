"""Authentication endpoints for JWT access tokens."""
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from backend.src.config import settings
from backend.src.database import SessionLocal
from backend.src.dependencies.auth import Principal, get_current_principal
from backend.src.models.tables import User
from backend.src.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])
auth_service = AuthService()


EMAIL_PATTERN = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"


class TokenRequest(BaseModel):
    email: str = Field(..., min_length=5, max_length=255, pattern=EMAIL_PATTERN)
    password: str = Field(..., min_length=8, max_length=128)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str


class RegisterRequest(BaseModel):
    email: str = Field(..., min_length=5, max_length=255, pattern=EMAIL_PATTERN)
    password: str = Field(..., min_length=8, max_length=128)
    role: str = Field(default="user", pattern="^(user|analyst|admin)$")


async def get_db() -> AsyncSession:
    async with SessionLocal() as session:
        yield session


@router.post("/token", response_model=TokenResponse)
async def issue_token(body: TokenRequest, session: AsyncSession = Depends(get_db)) -> TokenResponse:
    user = await auth_service.authenticate(session, body.email, body.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    token = auth_service.create_access_token(str(user.id), user.email, user.role)
    return TokenResponse(access_token=token, role=user.role)


@router.get("/me")
async def current_user(principal: Principal = Depends(get_current_principal)) -> dict[str, str | None]:
    return {"user_id": principal.user_id, "email": principal.email, "role": principal.role}


@router.post("/register", response_model=TokenResponse)
async def register_user(body: RegisterRequest, session: AsyncSession = Depends(get_db)) -> TokenResponse:
    if settings.app_env != "development":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Registration disabled")
    email = body.email.lower().strip()
    user = User(
        email=email,
        hashed_password=auth_service.hash_password(body.password),
        role=body.role,
    )
    session.add(user)
    await session.flush()
    token = auth_service.create_access_token(str(user.id), user.email, user.role)
    await session.commit()
    return TokenResponse(access_token=token, role=body.role)
