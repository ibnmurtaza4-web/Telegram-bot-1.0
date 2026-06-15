"""
Maintenance Middleware - Texniki xidmət rejimi
"""

from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message, CallbackQuery

from config import settings


class MaintenanceMiddleware(BaseMiddleware):
    """Texniki xidmət rejimini idarə et"""

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        if settings.MAINTENANCE_MODE:
            user_id = None
            if isinstance(event, (Message, CallbackQuery)):
                user_id = event.from_user.id if event.from_user else None

            # Adminlər işləyə bilər
            if user_id and user_id in settings.ADMIN_IDS:
                return await handler(event, data)

            # Digər istifadəçilərə məlumat ver
            if isinstance(event, Message):
                await event.answer(
                    "🔧 Bot texniki xidmətdədir. Zəhmət olmasa gözləyin."
                )
            elif isinstance(event, CallbackQuery):
                await event.answer(
                    "🔧 Bot texniki xidmətdədir. Zəhmət olmasa gözləyin.",
                    show_alert=True,
                )
            return

        return await handler(event, data)
