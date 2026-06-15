"""
Start Handler - Başlanğıc, ana menyu və qeydiyyat
"""

import logging
from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from database import get_or_create_user, log_action
from keyboards import main_menu_keyboard, admin_keyboard
from locales import t, get_user_lang
from config import settings
from states import PostStates

router = Router()
logger = logging.getLogger(__name__)


async def _get_lang(user_id: int, language_code: str = None) -> str:
    """İstifadəçi dilini al"""
    return get_user_lang(language_code or "az")


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    """Bot başladıldıqda"""
    user = message.from_user
    lang = get_user_lang(user.language_code)

    # İstifadəçini qeydiyyatdan keçir
    db_user = await get_or_create_user(
        user_id=user.id,
        username=user.username,
        first_name=user.first_name,
        last_name=user.last_name,
        language_code=lang,
    )

    # Bloklanıb mı?
    if db_user.is_blocked:
        await message.answer(t("blocked", lang))
        return

    await log_action(user.id, "start")

    # State-i sıfırla
    await state.clear()

    # Xoş gəldiniz mesajı
    await message.answer(
        t("welcome", lang, version=settings.VERSION),
        reply_markup=main_menu_keyboard(lang),
    )


@router.message(Command("menu"))
async def cmd_menu(message: Message, state: FSMContext):
    """Ana menyuya qayıt"""
    user = message.from_user
    lang = get_user_lang(user.language_code)

    db_user = await get_or_create_user(
        user_id=user.id,
        username=user.username,
        first_name=user.first_name,
    )

    if db_user.is_blocked:
        await message.answer(t("blocked", lang))
        return

    await state.clear()

    await message.answer(
        t("main_menu", lang),
        reply_markup=main_menu_keyboard(lang),
    )


@router.message(Command("admin"))
async def cmd_admin(message: Message, state: FSMContext):
    """Admin paneli aç"""
    user = message.from_user

    if user.id not in settings.ADMIN_IDS:
        lang = get_user_lang(user.language_code)
        await message.answer(t("not_admin", lang))
        return

    await state.clear()

    await message.answer(
        "⚙️ <b>Admin Paneli</b>",
        reply_markup=admin_keyboard(),
    )


@router.message(Command("help"))
async def cmd_help(message: Message):
    """Kömək menyusu"""
    user = message.from_user
    lang = get_user_lang(user.language_code)

    await message.answer(
        t("help_text", lang),
        reply_markup=main_menu_keyboard(lang),
    )


@router.callback_query(F.data == "main_menu")
async def cb_main_menu(callback: CallbackQuery, state: FSMContext):
    """Ana menyuya qayıt callback"""
    user = callback.from_user
    lang = get_user_lang(user.language_code)

    await state.clear()

    try:
        await callback.message.edit_text(
            t("main_menu", lang),
            reply_markup=main_menu_keyboard(lang),
        )
    except Exception:
        await callback.message.answer(
            t("main_menu", lang),
            reply_markup=main_menu_keyboard(lang),
        )

    await callback.answer()


@router.callback_query(F.data == "help")
async def cb_help(callback: CallbackQuery):
    """Kömək callback"""
    user = callback.from_user
    lang = get_user_lang(user.language_code)

    await callback.message.edit_text(
        t("help_text", lang),
        reply_markup=main_menu_keyboard(lang),
    )
    await callback.answer()


@router.callback_query(F.data == "settings")
async def cb_settings(callback: CallbackQuery):
    """Parametrlər callback"""
    user = callback.from_user
    lang = get_user_lang(user.language_code)

    from aiogram.utils.keyboard import InlineKeyboardBuilder
    from aiogram.types import InlineKeyboardButton

    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="🇦🇿 Azərbaycan", callback_data="lang:az"),
        InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang:ru"),
        InlineKeyboardButton(text="🇬🇧 English", callback_data="lang:en"),
    )
    builder.row(
        InlineKeyboardButton(text="⬅️ Geri", callback_data="main_menu"),
    )

    await callback.message.edit_text(
        "⚙️ <b>Parametrlər</b>\n\nDili seçin:",
        reply_markup=builder.as_markup(),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("lang:"))
async def cb_language(callback: CallbackQuery):
    """Dil seçimi"""
    lang = callback.data.split(":")[1]
    if lang not in ("az", "ru", "en"):
        lang = "az"

    await callback.answer(f"✅ Dil dəyişdirildi!", show_alert=False)
    await callback.message.edit_text(
        t("main_menu", lang),
        reply_markup=main_menu_keyboard(lang),
    )
