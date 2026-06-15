"""
Logging Middleware - Bütün mesajları logla
"""

import logging
from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message, CallbackQuery

logger = logging.getLogger(__name__)


class LoggingMiddleware(BaseMiddleware):
    """Əməliyyatları logla"""

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        user = None

        if isinstance(event, Message):
            user = event.from_user
            if event.text:
                logger.info(
                    f"MSG user_id={user.id} username={user.username} "
                    f"text={event.text[:50] if event.text else 'N/A'}"
                )
            elif event.photo:
                logger.info(f"MSG user_id={user.id} type=photo")
            elif event.video:
                logger.info(f"MSG user_id={user.id} type=video")
            elif event.document:
                logger.info(f"MSG user_id={user.id} type=document")

        elif isinstance(event, CallbackQuery):
            user = event.from_user
            logger.info(
                f"CBQ user_id={user.id} username={user.username} "
                f"data={event.data}"
            )

        result = await handler(event, data)

        return result
