"""
Drafts Handler - Qaralamalar idarəsi
"""

import logging
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from states import DraftStates, PostStates
from utils.post_data import PostData
from keyboards import drafts_keyboard, post_builder_keyboard, back_cancel_keyboard, confirm_keyboard
from locales import get_user_lang, t
from database import save_draft, get_user_drafts, get_draft, delete_draft
from config import settings

router = Router()
logger = logging.getLogger(__name__)


def get_lang(user): return get_user_lang(getattr(user, "language_code", "az"))


async def get_post(state):
    d = await state.get_data(); p = d.get("post_data")
    return PostData.from_dict(p) if p else PostData()


@router.callback_query(F.data == "my_drafts")
async def cb_my_drafts(callback: CallbackQuery, state: FSMContext):
    lang = get_lang(callback.from_user)
    drafts = await get_user_drafts(callback.from_user.id)

    if not drafts:
        await callback.answer(t("no_drafts", lang), show_alert=True)
        return

    await callback.message.edit_text(
        t("my_drafts", lang, count=len(drafts)),
        reply_markup=drafts_keyboard(drafts),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("draft:page:"))
async def cb_draft_page(callback: CallbackQuery, state: FSMContext):
    page = int(callback.data.split(":")[2])
    drafts = await get_user_drafts(callback.from_user.id)
    await callback.message.edit_reply_markup(reply_markup=drafts_keyboard(drafts, page=page))
    await callback.answer()


@router.callback_query(F.data.startswith("draft:load:"))
async def cb_draft_load(callback: CallbackQuery, state: FSMContext):
    lang = get_lang(callback.from_user)
    draft_id = int(callback.data.split(":")[2])

    draft = await get_draft(draft_id, callback.from_user.id)
    if not draft:
        await callback.answer("❌ Qaralama tapılmadı.", show_alert=True)
        return

    post = PostData(
        text=draft.post_text,
        parse_mode=draft.parse_mode or "HTML",
        disable_preview=draft.disable_preview,
        protect_content=draft.protect_content,
    )

    if draft.media_type and draft.media_file_id:
        from utils.post_data import MediaItem
        post.media = MediaItem(media_type=draft.media_type, file_id=draft.media_file_id)

    if draft.media_group:
        from utils.post_data import MediaItem
        post.media_group = [MediaItem.from_dict(m) for m in draft.media_group]

    if draft.buttons_json:
        from utils.post_data import ButtonData
        post.buttons = [ButtonData.from_dict(b) for b in draft.buttons_json]

    await state.update_data(post_data=post.to_dict())
    await state.set_state(PostStates.post_menu)

    await callback.message.edit_text(
        f"✅ <b>{draft.name}</b> yükləndi!",
        reply_markup=post_builder_keyboard(post, lang),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("draft:delete:"))
async def cb_draft_delete(callback: CallbackQuery, state: FSMContext):
    lang = get_lang(callback.from_user)
    draft_id = int(callback.data.split(":")[2])
    await state.update_data(delete_draft_id=draft_id)

    await callback.message.edit_text(
        "❓ Bu qaralamani silmək istədiyinizə əminsinizmi?",
        reply_markup=confirm_keyboard(f"draft:delete_confirm:{draft_id}", "my_drafts", lang),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("draft:delete_confirm:"))
async def cb_draft_delete_confirm(callback: CallbackQuery, state: FSMContext):
    lang = get_lang(callback.from_user)
    draft_id = int(callback.data.split(":")[2])

    success = await delete_draft(draft_id, callback.from_user.id)
    if success:
        await callback.answer("✅ Qaralama silindi!", show_alert=False)
    else:
        await callback.answer("❌ Silmə xətası", show_alert=True)

    drafts = await get_user_drafts(callback.from_user.id)
    if drafts:
        await callback.message.edit_text(
            t("my_drafts", lang, count=len(drafts)),
            reply_markup=drafts_keyboard(drafts),
        )
    else:
        await callback.message.edit_text(t("no_drafts", lang))


@router.callback_query(F.data == "pb:save_draft")
async def cb_save_draft(callback: CallbackQuery, state: FSMContext):
    lang = get_lang(callback.from_user)
    post = await get_post(state)

    if not post.has_content():
        await callback.answer("❌ Post boşdur, saxlamaq olmaz.", show_alert=True)
        return

    # Mövcud qaralama sayını yoxla
    drafts = await get_user_drafts(callback.from_user.id)
    if len(drafts) >= settings.MAX_DRAFTS_PER_USER:
        await callback.answer(
            t("max_drafts", lang, max=settings.MAX_DRAFTS_PER_USER), show_alert=True
        )
        return

    await state.set_state(DraftStates.waiting_draft_name)
    await callback.message.edit_text(
        t("waiting_draft_name", lang),
        reply_markup=back_cancel_keyboard("pb:back", lang),
    )
    await callback.answer()


@router.message(DraftStates.waiting_draft_name)
async def handle_draft_name(message: Message, state: FSMContext):
    lang = get_lang(message.from_user)
    name = message.text.strip()

    if not name or len(name) > 100:
        await message.answer("❌ Ad 1-100 simvol arası olmalıdır.")
        return

    post = await get_post(state)

    await save_draft(
        user_id=message.from_user.id,
        name=name,
        post_text=post.text,
        parse_mode=post.parse_mode,
        media_type=post.media.media_type if post.media else None,
        media_file_id=post.media.file_id if post.media else None,
        media_group=[m.to_dict() for m in post.media_group] if post.media_group else None,
        buttons_json=[b.to_dict() for b in post.buttons] if post.buttons else None,
        disable_preview=post.disable_preview,
        protect_content=post.protect_content,
    )

    await state.set_state(PostStates.post_menu)
    await message.answer(
        t("draft_saved", lang, name=name),
        reply_markup=post_builder_keyboard(post, lang),
    )
