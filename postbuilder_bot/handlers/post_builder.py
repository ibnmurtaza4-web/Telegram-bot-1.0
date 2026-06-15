"""
Post Builder Handler - Post qurma prosesi
"""

import logging
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from states import PostStates
from utils.post_data import PostData
from keyboards import (
    post_builder_keyboard, text_format_keyboard,
    preview_keyboard, options_keyboard, back_keyboard,
)
from locales import t, get_user_lang
from utils.helpers import estimate_message_size, truncate_text
from database import log_action

router = Router()
logger = logging.getLogger(__name__)


def get_lang(user) -> str:
    return get_user_lang(getattr(user, "language_code", "az"))


async def get_post_data(state: FSMContext) -> PostData:
    """State-dən post məlumatlarını al"""
    data = await state.get_data()
    post_dict = data.get("post_data")
    if post_dict:
        return PostData.from_dict(post_dict)
    return PostData()


async def save_post_data(state: FSMContext, post: PostData):
    """Post məlumatlarını state-ə saxla"""
    await state.update_data(post_data=post.to_dict())


@router.callback_query(F.data == "new_post")
async def cb_new_post(callback: CallbackQuery, state: FSMContext):
    """Yeni post yarat"""
    user = callback.from_user
    lang = get_lang(user)

    # Yeni post başlat
    post = PostData()
    await save_post_data(state, post)
    await state.set_state(PostStates.post_menu)

    await callback.message.edit_text(
        t("post_builder_menu", lang),
        reply_markup=post_builder_keyboard(post, lang),
    )
    await callback.answer()


@router.callback_query(F.data == "pb:back")
async def cb_post_back(callback: CallbackQuery, state: FSMContext):
    """Post qurucusuna qayıt"""
    user = callback.from_user
    lang = get_lang(user)

    post = await get_post_data(state)
    await state.set_state(PostStates.post_menu)

    try:
        await callback.message.edit_text(
            t("post_builder_menu", lang),
            reply_markup=post_builder_keyboard(post, lang),
        )
    except Exception:
        await callback.message.answer(
            t("post_builder_menu", lang),
            reply_markup=post_builder_keyboard(post, lang),
        )
    await callback.answer()


@router.callback_query(F.data == "pb:text")
async def cb_add_text(callback: CallbackQuery, state: FSMContext):
    """Mətn əlavə et"""
    user = callback.from_user
    lang = get_lang(user)

    post = await get_post_data(state)

    # Mövcud mətni göstər
    hint = ""
    if post.text:
        preview = truncate_text(post.text, 100)
        hint = f"\n\n<b>Mövcud mətn:</b>\n{preview}"

    await state.set_state(PostStates.waiting_text)

    await callback.message.edit_text(
        t("waiting_text", lang) + hint,
        reply_markup=text_format_keyboard(lang),
    )
    await callback.answer()


@router.message(PostStates.waiting_text)
async def handle_text_input(message: Message, state: FSMContext):
    """Mətn daxiletməsini emal et"""
    user = message.from_user
    lang = get_lang(user)

    text = message.text or message.caption

    if not text:
        await message.answer("❌ Mətn boş ola bilməz.")
        return

    # Ölçü yoxla
    size_info = estimate_message_size(text)
    if not size_info["within_text_limit"]:
        await message.answer(
            t("text_too_long", lang, max=4096) +
            f"\n\nCari: {size_info['characters']} simvol"
        )
        return

    post = await get_post_data(state)
    post.text = text
    await save_post_data(state, post)
    await state.set_state(PostStates.post_menu)

    await log_action(user.id, "add_text", {"length": len(text)})

    await message.answer(
        t("text_added", lang) +
        f"\n\n📊 {size_info['characters']}/4096 simvol",
        reply_markup=post_builder_keyboard(post, lang),
    )


@router.callback_query(F.data.startswith("fmt:"))
async def cb_format_hint(callback: CallbackQuery, state: FSMContext):
    """Format işarəsi göstər"""
    action = callback.data.split(":")[1]

    format_hints = {
        "bold": "Qalın mətn üçün: <code>&lt;b&gt;mətn&lt;/b&gt;</code>",
        "italic": "Kursiv üçün: <code>&lt;i&gt;mətn&lt;/i&gt;</code>",
        "underline": "Altıxətt üçün: <code>&lt;u&gt;mətn&lt;/u&gt;</code>",
        "strike": "Üstüxətt üçün: <code>&lt;s&gt;mətn&lt;/s&gt;</code>",
        "spoiler": "Spoiler üçün: <code>&lt;tg-spoiler&gt;mətn&lt;/tg-spoiler&gt;</code>",
        "code": "Kod üçün: <code>&lt;code&gt;mətn&lt;/code&gt;</code>",
        "pre": "Blok kod üçün: <code>&lt;pre&gt;mətn&lt;/pre&gt;</code>",
        "quote": "Sitat üçün: <code>&lt;blockquote&gt;mətn&lt;/blockquote&gt;</code>",
        "link": 'Keçid üçün: <code>&lt;a href="URL"&gt;mətn&lt;/a&gt;</code>',
        "apply": None,
        "check_size": None,
    }

    if action == "apply":
        await callback.answer("✅ Mətni yazın və göndərin", show_alert=False)
        return

    if action == "check_size":
        data = await state.get_data()
        post_dict = data.get("post_data")
        post = PostData.from_dict(post_dict) if post_dict else PostData()
        if post.text:
            size = estimate_message_size(post.text)
            await callback.answer(
                f"📏 {size['characters']}/4096 simvol\n"
                f"Mətn limiti: {'✅' if size['within_text_limit'] else '❌'}\n"
                f"Caption limiti: {'✅' if size['within_caption_limit'] else '❌'}",
                show_alert=True,
            )
        else:
            await callback.answer("Hələ mətn yoxdur", show_alert=False)
        return

    hint = format_hints.get(action, "")
    if hint:
        await callback.answer(hint, show_alert=True)
    else:
        await callback.answer()


@router.callback_query(F.data == "pb:preview")
async def cb_preview(callback: CallbackQuery, state: FSMContext):
    """Post önizləməsi"""
    user = callback.from_user
    lang = get_lang(user)

    post = await get_post_data(state)

    if not post.has_content():
        await callback.answer(t("no_content", lang), show_alert=True)
        return

    await _send_preview(callback, post, lang)
    await callback.answer()


async def _send_preview(callback: CallbackQuery, post: PostData, lang: str):
    """Önizləmə göndər"""
    from keyboards import build_post_inline_keyboard

    user_keyboard = build_post_inline_keyboard(post)
    preview_kb = preview_keyboard(post, lang)

    header = "👁 <b>POST ÖNİZLƏMƏ</b>\n" + "─" * 30 + "\n\n"

    try:
        if post.media_group:
            # Media albom
            from aiogram.types import InputMediaPhoto, InputMediaVideo
            media_items = []
            for i, m in enumerate(post.media_group):
                caption = post.text if i == 0 else None
                if m.media_type == "photo":
                    media_items.append(InputMediaPhoto(media=m.file_id, caption=caption))
                elif m.media_type == "video":
                    media_items.append(InputMediaVideo(media=m.file_id, caption=caption))

            if media_items:
                await callback.message.answer_media_group(media=media_items[:10])

        elif post.media:
            m = post.media
            caption = post.text
            kwargs = dict(
                caption=caption,
                reply_markup=user_keyboard,
                disable_notification=True,
            )

            if m.media_type == "photo":
                await callback.message.answer_photo(m.file_id, **kwargs)
            elif m.media_type == "video":
                await callback.message.answer_video(m.file_id, **kwargs)
            elif m.media_type == "audio":
                await callback.message.answer_audio(m.file_id, **kwargs)
            elif m.media_type == "voice":
                await callback.message.answer_voice(m.file_id, **kwargs)
            elif m.media_type == "animation":
                await callback.message.answer_animation(m.file_id, **kwargs)
            elif m.media_type == "document":
                await callback.message.answer_document(m.file_id, **kwargs)

        elif post.text:
            await callback.message.answer(
                post.text,
                reply_markup=user_keyboard,
                disable_web_page_preview=post.disable_preview,
                protect_content=post.protect_content,
            )

    except Exception as e:
        logger.error(f"Önizləmə xətası: {e}")
        await callback.message.answer(f"❌ Önizləmə xətası: {e}")

    # Redaktə klaviaturası
    await callback.message.answer(
        "👆 Önizləmə yuxarıdadır\n\nRedaktə etmək üçün:",
        reply_markup=preview_kb,
    )


@router.callback_query(F.data == "pb:options")
async def cb_options(callback: CallbackQuery, state: FSMContext):
    """Post seçimləri"""
    user = callback.from_user
    lang = get_lang(user)

    post = await get_post_data(state)

    await callback.message.edit_text(
        "⚙️ <b>Post Seçimləri</b>",
        reply_markup=options_keyboard(post, lang),
    )
    await callback.answer()


@router.callback_query(F.data.in_({"pb:toggle_preview", "opt:toggle_preview"}))
async def cb_toggle_preview(callback: CallbackQuery, state: FSMContext):
    """Link önizləməsini açıb-bağla"""
    post = await get_post_data(state)
    post.disable_preview = not post.disable_preview
    await save_post_data(state, post)

    status = "söndürüldü" if post.disable_preview else "açıldı"
    await callback.answer(f"🔗 Link önizləməsi {status}", show_alert=False)

    try:
        await callback.message.edit_reply_markup(
            reply_markup=options_keyboard(post)
        )
    except Exception:
        pass


@router.callback_query(F.data.in_({"pb:toggle_protect", "opt:toggle_protect"}))
async def cb_toggle_protect(callback: CallbackQuery, state: FSMContext):
    """Məzmun qorumasını açıb-bağla"""
    post = await get_post_data(state)
    post.protect_content = not post.protect_content
    await save_post_data(state, post)

    status = "aktivləşdi" if post.protect_content else "söndürüldü"
    await callback.answer(f"🔒 Məzmun qoruması {status}", show_alert=False)

    try:
        await callback.message.edit_reply_markup(
            reply_markup=options_keyboard(post)
        )
    except Exception:
        pass


@router.callback_query(F.data == "pb:reset")
async def cb_reset_post(callback: CallbackQuery, state: FSMContext):
    """Postu sıfırla"""
    user = callback.from_user
    lang = get_lang(user)

    from keyboards import confirm_keyboard
    await callback.message.edit_text(
        "⚠️ <b>Diqqət!</b>\n\nBütün post məlumatları silinəcək. Davam etmək istəyirsinizmi?",
        reply_markup=confirm_keyboard("pb:reset_confirm", "pb:back", lang),
    )
    await callback.answer()


@router.callback_query(F.data == "pb:reset_confirm")
async def cb_reset_confirm(callback: CallbackQuery, state: FSMContext):
    """Sıfırlamağı təsdiqlə"""
    user = callback.from_user
    lang = get_lang(user)

    post = PostData()
    await save_post_data(state, post)
    await state.set_state(PostStates.post_menu)

    await callback.message.edit_text(
        "✅ Post sıfırlandı!\n\n" + t("post_builder_menu", lang),
        reply_markup=post_builder_keyboard(post, lang),
    )
    await callback.answer()
