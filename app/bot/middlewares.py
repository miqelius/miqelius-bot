import logging
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, User as TelegramUser
from app.storage.database import AsyncSessionLocal
from app.storage.user_repository import UserRepository

logger = logging.getLogger(__name__)


class UserMiddleware(BaseMiddleware):
    async def __call__(self, handler, event: TelegramObject, data: dict):
        user: TelegramUser = data.get("event_from_user")
        if user:
            async with AsyncSessionLocal() as session:
                await UserRepository.upsert_user(
                    session=session,
                    telegram_id=user.id,
                    username=user.username,
                    first_name=user.first_name
                )
        return await handler(event, data)
