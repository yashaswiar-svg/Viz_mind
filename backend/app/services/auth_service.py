import logging
import shutil
import uuid
from typing import Any, Dict, Optional, Tuple
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security.jwt import JWTHandler
from app.core.security.password import PasswordHasher
from app.db.models.dataset import Dataset
from app.db.models.user import User
from app.db.repositories.user_repository import UserRepository
from app.services.storage_service import StorageService

logger = logging.getLogger(__name__)


class UserAlreadyExistsError(Exception):
    pass


class InvalidCredentialsError(Exception):
    pass


class AuthService:
    """Service handling user registration, authentication, token management, and account deletion."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.user_repo = UserRepository(db)

    async def register_user(self, email: str, password: str, full_name: str = "VizMind User") -> Tuple[User, str, str]:
        existing = await self.user_repo.get_by_email(email)
        if existing:
            raise UserAlreadyExistsError(f"User with email '{email}' already exists.")

        pwd_hash = PasswordHasher.hash_password(password)
        user = await self.user_repo.create_user(email=email, password_hash=pwd_hash, full_name=full_name)

        access_token = JWTHandler.create_access_token(str(user.id))
        refresh_token = JWTHandler.create_refresh_token(str(user.id))
        return user, access_token, refresh_token

    async def authenticate_user(self, email: str, password: str) -> Tuple[User, str, str]:
        user = await self.user_repo.get_by_email(email)
        if not user or not user.is_active:
            raise InvalidCredentialsError("Invalid email or password.")

        if not PasswordHasher.verify_password(password, user.password_hash):
            raise InvalidCredentialsError("Invalid email or password.")

        access_token = JWTHandler.create_access_token(str(user.id))
        refresh_token = JWTHandler.create_refresh_token(str(user.id))
        return user, access_token, refresh_token

    async def refresh_access_token(self, refresh_token: str) -> Tuple[str, str]:
        payload = JWTHandler.decode_token(refresh_token)
        if not payload or payload.get("type") != "refresh":
            raise InvalidCredentialsError("Invalid or expired refresh token.")

        user_id_str = payload.get("sub")
        user = await self.user_repo.get_by_id(uuid.UUID(user_id_str))
        if not user or not user.is_active:
            raise InvalidCredentialsError("User account is inactive or missing.")

        new_access_token = JWTHandler.create_access_token(str(user.id))
        new_refresh_token = JWTHandler.create_refresh_token(str(user.id))
        return new_access_token, new_refresh_token

    async def delete_user_account(self, user_id: uuid.UUID, storage_service: Optional[StorageService] = None) -> bool:
        """Coordinated account deletion: DB cascade + physical storage cleanup."""
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            return False

        # Find user dataset IDs for storage cleanup
        stmt = select(Dataset).where(Dataset.user_id == user_id)
        res = await self.db.execute(stmt)
        user_datasets = list(res.scalars().all())

        # 1. Physical storage cleanup
        if storage_service:
            for ds in user_datasets:
                try:
                    dataset_dir = storage_service.get_dataset_dir(ds.id)
                    if dataset_dir.exists():
                        shutil.rmtree(dataset_dir, ignore_errors=True)
                except Exception as exc:
                    logger.error(f"Failed to delete storage directory for dataset {ds.id}: {exc}")

        # 2. Database cascade delete
        await self.user_repo.delete_user(user_id)
        return True
