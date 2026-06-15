"""
Throttling Middleware - Sürət məhdudiyyəti
"""

import asyncio
from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message, CallbackQuery
from cachetools import TTLCache


class ThrottlingMiddleware(BaseMiddleware):
    """İstifadəçilərin çox sürətli mesaj göndərməsinin qarşısını al"""

    def __init__(self, rate_limit: float = 0.5):
        self.rate_limit = rate_limit
        self.cache = TTLCache(maxsize=10_000, ttl=rate_limit)

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        user_id = None

        if isinstance(event, (Message, CallbackQuery)):
            user_id = event.from_user.id if event.from_user else None

        if user_id and user_id in self.cache:
            if isinstance(event, CallbackQuery):
                await event.answer("⚠️ Çox sürətli! Zəhmət olmasa bir az gözləyin.", show_alert=False)
            return

        if user_id:
            self.cache[user_id] = True

        return await handler(event, data)
