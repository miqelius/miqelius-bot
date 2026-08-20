import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from app.core.config import settings
from app.core.logging import setup_logging
from app.storage.database import engine, Base
from app.bot.handlers import router
from app.bot.middlewares import UserMiddleware

logger = logging.getLogger(__name__)


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database initialized")


async def main():
    setup_logging()
    await init_db()

    bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())
    
    # Register middlewares
    dp.message.middleware(UserMiddleware())
    dp.callback_query.middleware(UserMiddleware())

    # Include router
    dp.include_router(router)

    try:
        print("🚀 Bot started successfully!")
        logger.info("Bot polling started")
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
