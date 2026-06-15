"""
JSON Handler - Inline keyboard JSON idxal/ixrac
"""

import json
import logging
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from states import JsonStates, PostStates
from utils.post_data import PostData
from keyboards import json_mode_keyboard, post_builder_keyboard, back_cancel_keyboard
from locales import get_user_lang, t
from utils.helpers import validate_json_keyboard

router = Router()
logger = logging.getLogger(__name__)


def get_lang(user): return get_user_lang(getattr(user, "language_code", "az"))


async def get_post(state):
    d = await state.get_data(); p = d.get("post_data")
    return PostData.from_dict(p) if p else PostData()


async def save_post(state, post): await state.update_data(post_data=post.to_dict())


@router.callback_query(F.data == "json_mode")
async def cb_json_mode(callback: CallbackQuery, state: FSMContext):
    lang = get_lang(callback.from_user)
    await state.set_state(JsonStates.main)
    await callback.message.edit_text(
        t("json_menu", lang),
        reply_markup=json_mode_keyboard(lang),
    )
    await callback.answer()


async def show_json_menu(callback: CallbackQuery, state: FSMContext):
    """JSON menyusunu göstər (digər handlerlardan çağırıla bilər)"""
    lang = get_lang(callback.from_user)
    await state.set_state(JsonStates.main)
    await callback.message.edit_text(t("json_menu", lang), reply_markup=json_mode_keyboard(lang))
    await callback.answer()


@router.callback_query(F.data == "json:export")
async def cb_json_export(callback: CallbackQuery, state: FSMContext):
    lang = get_lang(callback.from_user)
    post = await get_post(state)

    if not post.buttons:
        await callback.answer("❌ Hələ düymə yoxdur.", show_alert=True)
        return

    json_str = post.to_json()
    await callback.message.answer(
        f"📤 <b>Inline Keyboard JSON:</b>\n\n<pre>{json_str}</pre>",
        reply_markup=json_mode_keyboard(lang),
    )
    await callback.answer()


@router.callback_query(F.data == "json:import")
async def cb_json_import(callback: CallbackQuery, state: FSMContext):
    lang = get_lang(callback.from_user)
    await state.set_state(JsonStates.waiting_import)
    await callback.message.edit_text(
        t("waiting_json_import", lang),
        reply_markup=back_cancel_keyboard("json_mode", lang),
    )
    await callback.answer()


@router.message(JsonStates.waiting_import)
async def handle_json_import(message: Message, state: FSMContext):
    lang = get_lang(message.from_user)
    json_text = message.text

    if not json_text:
        await message.answer("❌ JSON mətni boş ola bilməz.")
        return

    is_valid, error, button_count = validate_json_keyboard(json_text)

    if not is_valid:
        await message.answer(t("json_invalid", lang, error=error))
        return

    try:
        imported_post = PostData.from_json_keyboard(json_text)
        current_post = await get_post(state)
        current_post.buttons = imported_post.buttons
        await save_post(state, current_post)
        await state.set_state(PostStates.post_menu)

        await message.answer(
            t("json_imported", lang, count=button_count),
            reply_markup=post_builder_keyboard(current_post, lang),
        )
    except Exception as e:
        await message.answer(f"❌ İdxal xətası: {e}")


@router.callback_query(F.data == "json:validate")
async def cb_json_validate(callback: CallbackQuery, state: FSMContext):
    lang = get_lang(callback.from_user)
    post = await get_post(state)

    if not post.buttons:
        await callback.answer("❌ Yoxlamaq üçün düymə yoxdur.", show_alert=True)
        return

    json_str = post.to_json()
    is_valid, error, count = validate_json_keyboard(json_str)

    if is_valid:
        await callback.answer(f"✅ JSON etibarlıdır! {count} düymə tapıldı.", show_alert=True)
    else:
        await callback.answer(f"❌ JSON xətası: {error[:100]}", show_alert=True)
