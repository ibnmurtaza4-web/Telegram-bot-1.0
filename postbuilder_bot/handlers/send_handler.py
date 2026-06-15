"""
Send Handler - Postları göndərmə
"""

import asyncio
import logging
from datetime import datetime
from typing import List, Union

from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery, InputMediaPhoto, InputMediaVideo
from aiogram.fsm.context import FSMContext
from aiogram.exceptions import TelegramForbiddenError, TelegramBadRequest

from states import SendStates, PostStates
from utils.post_data import PostData
from keyboards import (
    send_target_keyboard, confirm_keyboard, post_builder_keyboard,
    back_cancel_keyboard, build_post_inline_keyboard,
)
from locales import get_user_lang, t
from database import log_action
from utils.helpers import parse_date_time

router = Router()
logger = logging.getLogger(__name__)


def get_lang(user): return get_user_lang(getattr(user, "language_code", "az"))


async def get_post(state):
    d = await state.get_data(); p = d.get("post_data")
    return PostData.from_dict(p) if p else PostData()


@router.callback_query(F.data == "pb:send")
async def cb_send_menu(callback: CallbackQuery, state: FSMContext):
    lang = get_lang(callback.from_user)
    post = await get_post(state)

    if not post.has_content():
        await callback.answer("❌ Post boşdur! Mətn və ya media əlavə edin.", show_alert=True)
        return

    await state.set_state(SendStates.choosing_target_type)
    await callback.message.edit_text(
        "📤 <b>Göndərmə Menyusu</b>\n\nPostunuzu hara göndərmək istərsiniz?",
        reply_markup=send_target_keyboard(lang),
    )
    await callback.answer()


@router.callback_query(SendStates.choosing_target_type, F.data == "send:me")
async def cb_send_me(callback: CallbackQuery, state: FSMContext):
    lang = get_lang(callback.from_user)
    post = await get_post(state)
    bot: Bot = callback.bot

    await callback.answer("📤 Göndərilir...", show_alert=False)
    success = await _send_post(bot, callback.from_user.id, post)

    if success:
        await callback.message.edit_text(
            "✅ Post özünüzə göndərildi!\n\nNə etmək istərsiniz?",
            reply_markup=post_builder_keyboard(post, lang),
        )
        await log_action(callback.from_user.id, "send_post", {"target": "self"})
    else:
        await callback.message.edit_text("❌ Göndərmə xətası baş verdi.")


@router.callback_query(SendStates.choosing_target_type, F.data == "send:custom")
async def cb_send_custom(callback: CallbackQuery, state: FSMContext):
    lang = get_lang(callback.from_user)
    await state.set_state(SendStates.waiting_chat_id)
    await callback.message.edit_text(
        t("waiting_chat_id", lang),
        reply_markup=back_cancel_keyboard("pb:send", lang),
    )
    await callback.answer()


@router.message(SendStates.waiting_chat_id)
async def handle_chat_id(message: Message, state: FSMContext):
    lang = get_lang(message.from_user)
    post = await get_post(state)
    bot: Bot = message.bot

    target = message.text.strip()
    await message.answer("📤 Göndərilir...")

    success = await _send_post(bot, target, post)

    if success:
        await message.answer(
            f"✅ Post uğurla göndərildi!\nHədəf: <code>{target}</code>",
            reply_markup=post_builder_keyboard(post, lang),
        )
        await log_action(message.from_user.id, "send_post", {"target": target})
    else:
        await message.answer(
            f"❌ Göndərmə uğursuz oldu!\n\nYoxlayın:\n"
            "• Bot o çata əlavə edilib?\n"
            "• Bot admin hüquqları var?\n"
            "• Chat ID doğrudur?",
            reply_markup=back_cancel_keyboard("pb:send", lang),
        )
    await state.set_state(PostStates.post_menu)


@router.callback_query(SendStates.choosing_target_type, F.data == "send:multiple")
async def cb_send_multiple(callback: CallbackQuery, state: FSMContext):
    lang = get_lang(callback.from_user)
    await state.set_state(SendStates.waiting_multiple_targets)
    await callback.message.edit_text(
        t("waiting_multiple_targets", lang),
        reply_markup=back_cancel_keyboard("pb:send", lang),
    )
    await callback.answer()


@router.message(SendStates.waiting_multiple_targets)
async def handle_multiple_targets(message: Message, state: FSMContext):
    lang = get_lang(message.from_user)
    post = await get_post(state)
    bot: Bot = message.bot

    targets = [line.strip() for line in message.text.strip().splitlines() if line.strip()]

    if not targets:
        await message.answer("❌ Heç bir hədəf daxil edilmədi.")
        return

    from config import settings
    if len(targets) > settings.MAX_TARGETS_AT_ONCE:
        await message.answer(f"❌ Maksimum {settings.MAX_TARGETS_AT_ONCE} hədəfə göndərə bilərsiniz.")
        return

    status_msg = await message.answer(f"📤 {len(targets)} hədəfə göndərilir...")

    success_count = 0
    failed = []

    for target in targets:
        ok = await _send_post(bot, target, post)
        if ok:
            success_count += 1
        else:
            failed.append(target)
        await asyncio.sleep(0.3)

    result = f"✅ <b>Göndərmə tamamlandı!</b>\n\n"
    result += f"✅ Uğurlu: {success_count}/{len(targets)}\n"
    if failed:
        result += f"❌ Uğursuz: {', '.join(failed[:5])}"

    await status_msg.edit_text(result, reply_markup=post_builder_keyboard(post, lang))
    await log_action(message.from_user.id, "send_multiple", {"targets": len(targets), "success": success_count})
    await state.set_state(PostStates.post_menu)


@router.callback_query(SendStates.choosing_target_type, F.data == "send:schedule")
async def cb_schedule(callback: CallbackQuery, state: FSMContext):
    lang = get_lang(callback.from_user)
    await state.set_state(SendStates.waiting_chat_id)
    await state.update_data(schedule_mode=True)
    await callback.message.edit_text(
        "📅 Əvvəlcə hədəf chat ID-ni daxil edin:\n(Sonra tarixi soruşacağıq)",
        reply_markup=back_cancel_keyboard("pb:send", lang),
    )
    await callback.answer()


async def _send_post(bot: Bot, chat_id: Union[str, int], post: PostData) -> bool:
    """Postu göndər - True/False qaytar"""
    try:
        keyboard = build_post_inline_keyboard(post)

        if post.media_group and len(post.media_group) >= 2:
            media_list = []
            for i, m in enumerate(post.media_group[:10]):
                caption = post.text if i == 0 else None
                parse_mode = post.parse_mode if i == 0 else None
                if m.media_type == "photo":
                    media_list.append(InputMediaPhoto(media=m.file_id, caption=caption, parse_mode=parse_mode))
                elif m.media_type == "video":
                    media_list.append(InputMediaVideo(media=m.file_id, caption=caption, parse_mode=parse_mode))
            if media_list:
                await bot.send_media_group(chat_id=chat_id, media=media_list)
            return True

        if post.media:
            m = post.media
            kw = dict(
                chat_id=chat_id,
                caption=post.text,
                parse_mode=post.parse_mode,
                reply_markup=keyboard,
                protect_content=post.protect_content,
            )
            if m.media_type == "photo":
                await bot.send_photo(photo=m.file_id, **kw)
            elif m.media_type == "video":
                await bot.send_video(video=m.file_id, **kw)
            elif m.media_type == "audio":
                await bot.send_audio(audio=m.file_id, **kw)
            elif m.media_type == "voice":
                await bot.send_voice(voice=m.file_id, **kw)
            elif m.media_type == "animation":
                await bot.send_animation(animation=m.file_id, **kw)
            elif m.media_type == "document":
                await bot.send_document(document=m.file_id, **kw)
            return True

        if post.text:
            await bot.send_message(
                chat_id=chat_id,
                text=post.text,
                parse_mode=post.parse_mode,
                reply_markup=keyboard,
                disable_web_page_preview=post.disable_preview,
                protect_content=post.protect_content,
            )
            return True

        return False

    except (TelegramForbiddenError, TelegramBadRequest) as e:
        logger.warning(f"Göndərmə xətası [{chat_id}]: {e}")
        return False
    except Exception as e:
        logger.error(f"Gözlənilməz göndərmə xətası [{chat_id}]: {e}")
        return False
