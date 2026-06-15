"""
Media Handler - Şəkil, video, audio, sənəd və albom emalı
"""

import logging
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from states import PostStates
from utils.post_data import PostData, MediaItem
from keyboards import media_type_keyboard, post_builder_keyboard, back_cancel_keyboard
from locales import get_user_lang
from database import log_action

router = Router()
logger = logging.getLogger(__name__)


def get_lang(user): return get_user_lang(getattr(user, "language_code", "az"))


async def get_post(state): 
    d = await state.get_data(); p = d.get("post_data")
    return PostData.from_dict(p) if p else PostData()


async def save_post(state, post): await state.update_data(post_data=post.to_dict())


@router.callback_query(F.data == "pb:media")
async def cb_media_menu(callback: CallbackQuery, state: FSMContext):
    lang = get_lang(callback.from_user)
    await callback.message.edit_text("🖼 <b>Media növünü seçin:</b>", reply_markup=media_type_keyboard(lang))
    await callback.answer()


@router.callback_query(F.data.startswith("media:"))
async def cb_media_type(callback: CallbackQuery, state: FSMContext):
    lang = get_lang(callback.from_user)
    media_type = callback.data.split(":")[1]

    if media_type == "remove":
        post = await get_post(state)
        post.media = None
        post.media_group = []
        await save_post(state, post)
        await callback.answer("✅ Media silindi", show_alert=False)
        await callback.message.edit_text("🖼 <b>Media növünü seçin:</b>", reply_markup=media_type_keyboard(lang))
        return

    prompts = {
        "photo": "🖼 Şəkil göndərin:", "video": "🎥 Video göndərin:",
        "audio": "🎵 Audio göndərin:", "voice": "🎤 Səs mesajı göndərin:",
        "animation": "🎬 GIF/Animasiya göndərin:", "document": "📄 Sənəd göndərin:",
        "group": "📸 Mediyaları göndərin (2-10). Bitirdikdə /done yazın:",
    }

    await state.update_data(pending_media_type=media_type)
    await state.set_state(PostStates.waiting_media)
    await callback.message.edit_text(prompts.get(media_type, "Media göndərin:"),
                                      reply_markup=back_cancel_keyboard("pb:media", lang))
    await callback.answer()


@router.message(PostStates.waiting_media, F.photo)
async def handle_photo(message: Message, state: FSMContext):
    lang = get_lang(message.from_user)
    file_id = message.photo[-1].file_id
    data = await state.get_data()
    media_type = data.get("pending_media_type", "photo")

    if media_type == "group":
        group = data.get("media_group_items", [])
        group.append({"media_type": "photo", "file_id": file_id})
        await state.update_data(media_group_items=group)
        await message.answer(f"✅ {len(group)}. şəkil əlavə edildi. Daha göndərin və ya /done yazın.")
        return

    post = await get_post(state)
    post.media = MediaItem(media_type="photo", file_id=file_id, caption=post.text)
    await save_post(state, post)
    await state.set_state(PostStates.post_menu)
    await message.answer("✅ Şəkil əlavə edildi!", reply_markup=post_builder_keyboard(post, lang))


@router.message(PostStates.waiting_media, F.video)
async def handle_video(message: Message, state: FSMContext):
    lang = get_lang(message.from_user)
    file_id = message.video.file_id
    data = await state.get_data()
    media_type = data.get("pending_media_type", "video")

    if media_type == "group":
        group = data.get("media_group_items", [])
        group.append({"media_type": "video", "file_id": file_id})
        await state.update_data(media_group_items=group)
        await message.answer(f"✅ {len(group)}. video əlavə edildi. Daha göndərin və ya /done yazın.")
        return

    post = await get_post(state)
    post.media = MediaItem(media_type="video", file_id=file_id)
    await save_post(state, post)
    await state.set_state(PostStates.post_menu)
    await message.answer("✅ Video əlavə edildi!", reply_markup=post_builder_keyboard(post, lang))


@router.message(PostStates.waiting_media, F.audio)
async def handle_audio(message: Message, state: FSMContext):
    lang = get_lang(message.from_user)
    post = await get_post(state)
    post.media = MediaItem(media_type="audio", file_id=message.audio.file_id)
    await save_post(state, post)
    await state.set_state(PostStates.post_menu)
    await message.answer("✅ Audio əlavə edildi!", reply_markup=post_builder_keyboard(post, lang))


@router.message(PostStates.waiting_media, F.voice)
async def handle_voice(message: Message, state: FSMContext):
    lang = get_lang(message.from_user)
    post = await get_post(state)
    post.media = MediaItem(media_type="voice", file_id=message.voice.file_id)
    await save_post(state, post)
    await state.set_state(PostStates.post_menu)
    await message.answer("✅ Səs mesajı əlavə edildi!", reply_markup=post_builder_keyboard(post, lang))


@router.message(PostStates.waiting_media, F.animation)
async def handle_animation(message: Message, state: FSMContext):
    lang = get_lang(message.from_user)
    post = await get_post(state)
    post.media = MediaItem(media_type="animation", file_id=message.animation.file_id)
    await save_post(state, post)
    await state.set_state(PostStates.post_menu)
    await message.answer("✅ GIF əlavə edildi!", reply_markup=post_builder_keyboard(post, lang))


@router.message(PostStates.waiting_media, F.document)
async def handle_document(message: Message, state: FSMContext):
    lang = get_lang(message.from_user)
    post = await get_post(state)
    post.media = MediaItem(media_type="document", file_id=message.document.file_id)
    await save_post(state, post)
    await state.set_state(PostStates.post_menu)
    await message.answer("✅ Sənəd əlavə edildi!", reply_markup=post_builder_keyboard(post, lang))


@router.message(PostStates.waiting_media, F.text == "/done")
async def handle_media_group_done(message: Message, state: FSMContext):
    lang = get_lang(message.from_user)
    data = await state.get_data()
    group_items = data.get("media_group_items", [])

    if len(group_items) < 2:
        await message.answer("❌ Albom üçün ən az 2 media lazımdır.")
        return

    post = await get_post(state)
    post.media_group = [MediaItem.from_dict(m) for m in group_items[:10]]
    await save_post(state, post)
    await state.update_data(media_group_items=[])
    await state.set_state(PostStates.post_menu)
    await message.answer(f"✅ {len(post.media_group)} media albom kimi əlavə edildi!",
                          reply_markup=post_builder_keyboard(post, lang))
