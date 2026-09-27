import uuid
from typing import AsyncGenerator, Optional
from fastapi import Depends, HTTPException, Header, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security.jwt import JWTHandler
from app.db.database import get_db
from app.db.models.dataset import Dataset
from app.db.models.user import User

SYSTEM_USER_ID = uuid.UUID("00000000-0000-0000-0000-000000000000")


async def get_current_user(
    authorization: Optional[str] = Header(None),
    db: AsyncSession = Depends(get_db),
) -> User:
    """Dependency verifying Bearer token and returning authenticated User."""

    if authorization and authorization.startswith("Bearer "):
        token = authorization[7:].strip()
        payload = JWTHandler.decode_token(token)
        if payload and payload.get("type") == "access":
            user_id_str = payload.get("sub")
            if user_id_str:
                stmt = select(User).where(User.id == uuid.UUID(user_id_str))
                res = await db.execute(stmt)
                user = res.scalar_one_or_none()
                if user and user.is_active:
                    return user

    # Development / Test bypass mode
    if (not settings.AUTH_ENABLED or settings.AUTH_TEST_BYPASS) and settings.APP_ENV != "production":
        stmt = select(User).where(User.id == SYSTEM_USER_ID)
        res = await db.execute(stmt)
        sys_user = res.scalar_one_or_none()
        if sys_user:
            return sys_user
        # Create virtual test user if missing in DB
        test_user = User(
            id=SYSTEM_USER_ID,
            email="system@vizmind.internal",
            password_hash="SYSTEM_LOCKED",
            full_name="System Test User",
            is_active=True,
        )
        return test_user

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )


from app.core.exceptions import DatasetNotFoundException


async def verify_dataset_ownership(
    dataset_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Dataset:
    """Verifies that current_user owns dataset_id. Returns 404 if not found or unowned."""
    stmt = select(Dataset).where(Dataset.id == dataset_id)
    res = await db.execute(stmt)
    dataset = res.scalar_one_or_none()

    if not dataset:
        raise DatasetNotFoundException(f"Dataset with ID {dataset_id} not found.")

    # Ownership check
    if dataset.user_id != current_user.id:
        # Check system migration user exception in non-prod
        if (dataset.user_id == SYSTEM_USER_ID or dataset.user_id is None) and settings.APP_ENV != "production":
            return dataset
        raise DatasetNotFoundException(f"Dataset with ID {dataset_id} not found.")

    return dataset
