"""
PostBuilder Bot - Ana başlanğıc nöqtəsi
Peşəkar Telegram Post və Button Builder Botu
"""

import asyncio
import logging
import sys
from pathlib import Path

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from config import settings
from database.db import init_db
from handlers import (
    start,
    post_builder,
    button_builder,
    media_handler,
    templates_handler,
    send_handler,
    admin_handler,
    json_handler,
    premium_handler,
    drafts_handler,
)
from middlewares.logging_middleware import LoggingMiddleware
from middlewares.throttling import ThrottlingMiddleware
from middlewares.maintenance import MaintenanceMiddleware

# Logging konfiqurasiyası
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("bot.log", encoding="utf-8"),
    ],
)
logger = logging.getLogger(__name__)


async def main():
    """Botu başlat"""
    logger.info("PostBuilder Bot başladılır...")

    # Verilənlər bazasını inisializasiya et
    await init_db()
    logger.info("Verilənlər bazası hazır")

    # Bot obyekti
    bot = Bot(
        token=settings.BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )

    # Dispatcher
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)

    # Middleware-lər
    dp.message.middleware(LoggingMiddleware())
    dp.message.middleware(ThrottlingMiddleware(rate_limit=0.5))
    dp.message.middleware(MaintenanceMiddleware())
    dp.callback_query.middleware(LoggingMiddleware())
    dp.callback_query.middleware(ThrottlingMiddleware(rate_limit=0.3))
    dp.callback_query.middleware(MaintenanceMiddleware())

    # Routerları qeydiyyatdan keçir
    dp.include_router(start.router)
    dp.include_router(post_builder.router)
    dp.include_router(button_builder.router)
    dp.include_router(media_handler.router)
    dp.include_router(templates_handler.router)
    dp.include_router(send_handler.router)
    dp.include_router(json_handler.router)
    dp.include_router(premium_handler.router)
    dp.include_router(drafts_handler.router)
    dp.include_router(admin_handler.router)

    # Bot məlumatlarını yoxla
    bot_info = await bot.get_me()
    logger.info(f"Bot başladıldı: @{bot_info.username} ({bot_info.id})")

    # Polling başlat
    try:
        await dp.start_polling(
            bot,
            allowed_updates=dp.resolve_used_update_types(),
            drop_pending_updates=True,
        )
    finally:
        await bot.session.close()
        logger.info("Bot dayandırıldı")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot istifadəçi tərəfindən dayandırıldı")
    except Exception as e:
        logger.critical(f"Kritik xəta: {e}", exc_info=True)
        sys.exit(1)
