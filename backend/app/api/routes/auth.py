from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.middleware.rate_limiter import check_rate_limit
from app.db.database import get_db
from app.db.models.user import User
from app.schemas.auth import (
    RefreshTokenRequest,
    TokenResponse,
    UserLoginRequest,
    UserRegisterRequest,
    UserResponse,
)
from app.services.auth_service import (
    AuthService,
    InvalidCredentialsError,
    UserAlreadyExistsError,
)
from app.services.storage_service import StorageService

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED, dependencies=[Depends(check_rate_limit)])
async def register_user(
    payload: UserRegisterRequest,
    db: AsyncSession = Depends(get_db),
):
    service = AuthService(db)
    try:
        _, access_token, refresh_token = await service.register_user(
            email=payload.email,
            password=payload.password,
            full_name=payload.full_name or "VizMind User",
        )
        await db.commit()
        return TokenResponse(access_token=access_token, refresh_token=refresh_token)
    except UserAlreadyExistsError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/login", response_model=TokenResponse, dependencies=[Depends(check_rate_limit)])
async def login_user(
    payload: UserLoginRequest,
    db: AsyncSession = Depends(get_db),
):
    service = AuthService(db)
    try:
        _, access_token, refresh_token = await service.authenticate_user(
            email=payload.email,
            password=payload.password,
        )
        return TokenResponse(access_token=access_token, refresh_token=refresh_token)
    except InvalidCredentialsError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))


@router.post("/refresh", response_model=TokenResponse, dependencies=[Depends(check_rate_limit)])
async def refresh_token(
    payload: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db),
):
    service = AuthService(db)
    try:
        access_token, refresh_token = await service.refresh_access_token(payload.refresh_token)
        return TokenResponse(access_token=access_token, refresh_token=refresh_token)
    except InvalidCredentialsError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))


@router.get("/me", response_model=UserResponse)
async def get_me(
    current_user: User = Depends(get_current_user),
):
    return current_user


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
async def delete_me(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = AuthService(db)
    storage_service = StorageService()
    await service.delete_user_account(current_user.id, storage_service=storage_service)
    await db.commit()
    return None
