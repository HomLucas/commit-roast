from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.database import get_db
from src.models.user import User
from src.services.auth import AuthService, get_current_user
from src.services.token_blacklist import blacklist_token
from src.services.email import send_password_reset
from src.services.redis_client import cache
from src.schemas.auth import (
    Token,
    UserCreate,
    UserResponse,
    RefreshToken,
)

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("2/minute")
async def register(
    request: Request,
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db),
):
    existing = await db.execute(
        select(User).where(
            (User.email == user_data.email) | (User.username == user_data.username)
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email or username already registered"
        )

    user = User(
        email=user_data.email,
        username=user_data.username,
        full_name=user_data.full_name,
        hashed_password=AuthService.hash_password(user_data.password),
        preferred_currency=user_data.preferred_currency or "USD",
    )

    db.add(user)
    await db.commit()
    await db.refresh(user)

    return UserResponse.from_orm(user)


@router.post("/login", response_model=Token)
@limiter.limit("5/minute")
async def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(User).where(
            (User.email == form_data.username) | (User.username == form_data.username)
        )
    )
    user = result.scalar_one_or_none()

    if not user or not AuthService.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email/username or password"
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is disabled"
        )

    user.last_login = datetime.utcnow()
    await db.commit()

    access_token = AuthService.create_access_token(
        data={"sub": user.id, "email": user.email, "role": user.role.value}
    )
    refresh_token = AuthService.create_refresh_token(
        data={"sub": user.id, "type": "refresh"}
    )

    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        user=UserResponse.from_orm(user)
    )


@router.post("/refresh", response_model=Token)
@limiter.limit("3/minute")
async def refresh_token(
    request: Request,
    refresh: RefreshToken,
    db: AsyncSession = Depends(get_db),
):
    payload = AuthService.decode_token(refresh.refresh_token, "refresh")

    await blacklist_token(refresh.refresh_token)

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive"
        )

    new_access_token = AuthService.create_access_token(
        data={"sub": user.id, "email": user.email, "role": user.role.value}
    )
    new_refresh_token = AuthService.create_refresh_token(
        data={"sub": user.id, "type": "refresh"}
    )

    return Token(
        access_token=new_access_token,
        refresh_token=new_refresh_token,
        token_type="bearer",
        user=UserResponse.from_orm(user)
    )


@router.post("/logout")
async def logout(
    request: Request,
    current_user: User = Depends(get_current_user),
):
    auth_header = request.headers.get("Authorization", "")
    token = auth_header.replace("Bearer ", "")
    if token:
        await blacklist_token(token)
    return {"message": "Successfully logged out"}


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    request: Request,
    current_user: User = Depends(get_current_user),
):
    return UserResponse.from_orm(current_user)


@router.post("/forgot-password")
@limiter.limit("2/minute")
async def forgot_password(
    request: Request,
    email: str,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    if not user:
        return {"message": "If that email exists, a reset link has been sent"}

    import uuid
    reset_token = str(uuid.uuid4())
    c = await cache()
    await c.setex(f"pwdreset:{reset_token}", 3600, str(user.id))

    frontend_url = (settings.cors_origins or ["http://localhost:3000"])[0]
    reset_link = f"{frontend_url}/reset-password?token={reset_token}"

    await send_password_reset(
        user_email=user.email,
        username=user.username,
        reset_link=reset_link,
    )

    return {"message": "If that email exists, a reset link has been sent"}


@router.post("/reset-password")
@limiter.limit("2/minute")
async def reset_password(
    request: Request,
    token: str,
    new_password: str,
    db: AsyncSession = Depends(get_db),
):
    c = await cache()
    user_id_str = await c.get(f"pwdreset:{token}")
    if not user_id_str:
        raise HTTPException(status_code=400, detail="Invalid or expired reset token")

    user_id = int(user_id_str)
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.hashed_password = AuthService.hash_password(new_password)
    await db.commit()
    await c.delete(f"pwdreset:{token}")

    return {"message": "Password reset successfully"}
