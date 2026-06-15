"""
Button Builder Handler - Düymə qurma
"""

import logging
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from states import ButtonStates, PostStates
from utils.post_data import PostData, ButtonData
from keyboards import (
    button_type_keyboard, button_menu_keyboard,
    buttons_list_keyboard, back_keyboard, back_cancel_keyboard,
)
from locales import t, get_user_lang
from utils.helpers import (
    is_valid_url, is_valid_https_url, get_button_type_emoji,
    truncate_text,
)
from database import log_action
from config import settings

router = Router()
logger = logging.getLogger(__name__)


def get_lang(user) -> str:
    return get_user_lang(getattr(user, "language_code", "az"))


async def get_post(state: FSMContext) -> PostData:
    data = await state.get_data()
    post_dict = data.get("post_data")
    if post_dict:
        return PostData.from_dict(post_dict)
    return PostData()


async def save_post(state: FSMContext, post: PostData):
    await state.update_data(post_data=post.to_dict())


@router.callback_query(F.data == "pb:buttons")
async def cb_buttons_menu(callback: CallbackQuery, state: FSMContext):
    """Düymə menyusu"""
    user = callback.from_user
    lang = get_lang(user)

    post = await get_post(state)

    text = t("button_menu", lang, button_count=post.get_button_count())

    await callback.message.edit_text(
        text,
        reply_markup=button_menu_keyboard(post, lang),
    )
    await callback.answer()


@router.callback_query(F.data == "btn:menu")
async def cb_btn_back_menu(callback: CallbackQuery, state: FSMContext):
    """Düymə menyusuna qayıt"""
    user = callback.from_user
    lang = get_lang(user)
    post = await get_post(state)

    await callback.message.edit_text(
        t("button_menu", lang, button_count=post.get_button_count()),
        reply_markup=button_menu_keyboard(post, lang),
    )
    await callback.answer()


@router.callback_query(F.data == "btn:add")
async def cb_add_button(callback: CallbackQuery, state: FSMContext):
    """Yeni düymə əlavə et"""
    user = callback.from_user
    lang = get_lang(user)

    post = await get_post(state)

    # Limit yoxla
    if post.get_button_count() >= settings.MAX_BUTTON_ROWS * settings.MAX_BUTTONS_PER_ROW:
        await callback.answer("❌ Maksimum düymə limitinə çatdınız!", show_alert=True)
        return

    await state.set_state(ButtonStates.choosing_type)

    await callback.message.edit_text(
        t("choose_button_type", lang),
        reply_markup=button_type_keyboard(lang),
    )
    await callback.answer()


@router.callback_query(F.data == "btn:new_row")
async def cb_new_row(callback: CallbackQuery, state: FSMContext):
    """Yeni sətir başlat"""
    post = await get_post(state)

    if not post.buttons:
        await callback.answer("❌ Əvvəlcə düymə əlavə edin!", show_alert=False)
        return

    # Cari sətri artır
    post.current_row = max((b.row for b in post.buttons), default=-1) + 1
    await save_post(state, post)

    await callback.answer(f"✅ Yeni sətir ({post.current_row + 1}) başladıldı!", show_alert=False)


@router.callback_query(F.data == "btn:view")
async def cb_view_buttons(callback: CallbackQuery, state: FSMContext):
    """Düymələri göstər"""
    post = await get_post(state)

    if not post.buttons:
        await callback.answer(t("no_buttons"), show_alert=True)
        return

    await callback.message.edit_text(
        f"📋 <b>Düymələr siyahısı</b>\n\nCəmi: {post.get_button_count()} düymə",
        reply_markup=buttons_list_keyboard(post, "view"),
    )
    await callback.answer()


@router.callback_query(F.data == "btn:edit")
async def cb_edit_button_list(callback: CallbackQuery, state: FSMContext):
    """Redaktə üçün düymə seç"""
    post = await get_post(state)

    if not post.buttons:
        await callback.answer(t("no_buttons"), show_alert=True)
        return

    await callback.message.edit_text(
        "✏️ <b>Redaktə etmək üçün düymə seçin:</b>",
        reply_markup=buttons_list_keyboard(post, "edit"),
    )
    await callback.answer()


@router.callback_query(F.data == "btn:delete")
async def cb_delete_button_list(callback: CallbackQuery, state: FSMContext):
    """Silmək üçün düymə seç"""
    post = await get_post(state)

    if not post.buttons:
        await callback.answer(t("no_buttons"), show_alert=True)
        return

    await callback.message.edit_text(
        "🗑 <b>Silmək üçün düymə seçin:</b>",
        reply_markup=buttons_list_keyboard(post, "del"),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("btn_del:"))
async def cb_delete_button(callback: CallbackQuery, state: FSMContext):
    """Düymə sil"""
    user = callback.from_user
    lang = get_lang(user)

    index = int(callback.data.split(":")[1])
    post = await get_post(state)

    if post.remove_button(index):
        await save_post(state, post)
        await callback.answer(t("button_deleted", lang), show_alert=False)

        if post.buttons:
            await callback.message.edit_text(
                "🗑 <b>Silmək üçün düymə seçin:</b>",
                reply_markup=buttons_list_keyboard(post, "del"),
            )
        else:
            await callback.message.edit_text(
                t("button_menu", lang, button_count=0),
                reply_markup=button_menu_keyboard(post, lang),
            )
    else:
        await callback.answer("❌ Düymə tapılmadı", show_alert=True)


@router.callback_query(F.data == "btn:clear_all")
async def cb_clear_buttons(callback: CallbackQuery, state: FSMContext):
    """Bütün düymələri sil"""
    user = callback.from_user
    lang = get_lang(user)

    from keyboards import confirm_keyboard
    await callback.message.edit_text(
        "⚠️ Bütün düymələr silinəcək. Davam etmək istəyirsinizmi?",
        reply_markup=confirm_keyboard("btn:clear_confirm", "btn:menu", lang),
    )
    await callback.answer()


@router.callback_query(F.data == "btn:clear_confirm")
async def cb_clear_confirm(callback: CallbackQuery, state: FSMContext):
    """Silməni təsdiqlə"""
    user = callback.from_user
    lang = get_lang(user)

    post = await get_post(state)
    post.buttons.clear()
    post.current_row = 0
    await save_post(state, post)

    await callback.answer(t("buttons_cleared", lang), show_alert=False)
    await callback.message.edit_text(
        t("button_menu", lang, button_count=0),
        reply_markup=button_menu_keyboard(post, lang),
    )


@router.callback_query(F.data == "btn:json")
async def cb_btn_json(callback: CallbackQuery, state: FSMContext):
    """Düymə JSON ixrac/idxal"""
    from handlers.json_handler import show_json_menu
    await show_json_menu(callback, state)


# ─── Düymə növü seçimi ──────────────────────────────────────────────────────

@router.callback_query(ButtonStates.choosing_type, F.data.startswith("btn_type:"))
async def cb_button_type_chosen(callback: CallbackQuery, state: FSMContext):
    """Düymə növü seçildi"""
    user = callback.from_user
    lang = get_lang(user)

    btn_type = callback.data.split(":")[1]
    await state.update_data(current_btn_type=btn_type, current_btn_row=None)

    # Növə görə giriş soruşmaq
    type_prompts = {
        "url": ("waiting_url_button_text", ButtonStates.waiting_url_text),
        "callback": ("waiting_callback_text", ButtonStates.waiting_callback_text),
        "webapp": ("waiting_webapp_text", ButtonStates.waiting_webapp_text),
        "share": ("waiting_url_button_text", ButtonStates.waiting_url_text),
        "switch_inline": ("waiting_switch_text", ButtonStates.waiting_switch_text),
        "switch_current": ("waiting_switch_text", ButtonStates.waiting_switch_text),
        "copy": ("waiting_copy_text", ButtonStates.waiting_copy_text),
        "login": ("waiting_login_text", ButtonStates.waiting_login_text),
        "game": None,
        "pay": None,
    }

    if btn_type in ("game", "pay"):
        # Mətn tələb edir amma value yox
        await state.update_data(current_btn_type=btn_type)
        await state.set_state(ButtonStates.waiting_url_text)
        await callback.message.edit_text(
            "✏️ Düymə mətni daxil edin:",
            reply_markup=back_cancel_keyboard("btn:add", lang),
        )
    elif btn_type in type_prompts:
        prompt_key, next_state = type_prompts[btn_type]
        await state.set_state(next_state)
        await callback.message.edit_text(
            t(prompt_key, lang),
            reply_markup=back_cancel_keyboard("btn:add", lang),
        )

    await callback.answer()


# ─── URL düymə ──────────────────────────────────────────────────────────────

@router.message(ButtonStates.waiting_url_text)
async def handle_url_btn_text(message: Message, state: FSMContext):
    """URL düymə mətni"""
    user = message.from_user
    lang = get_lang(user)

    text = message.text
    if not text or len(text) > 200:
        await message.answer("❌ Düymə mətni 1-200 simvol arası olmalıdır.")
        return

    data = await state.get_data()
    btn_type = data.get("current_btn_type", "url")
    await state.update_data(current_btn_text=text)

    if btn_type in ("game", "pay"):
        # Bu növlər üçün əlavə dəyər tələb olunmur
        await _add_button_final(message, state, text, "", btn_type, lang)
        return

    # URL soruş
    type_prompts = {
        "url": "waiting_url_button_url",
        "share": "waiting_url_button_url",
        "webapp": "waiting_webapp_url",
        "login": "waiting_login_url",
    }

    prompt_key = type_prompts.get(btn_type, "waiting_url_button_url")
    await state.set_state(ButtonStates.waiting_url)

    await message.answer(
        t(prompt_key, lang),
        reply_markup=back_cancel_keyboard("btn:add", lang),
    )


@router.message(ButtonStates.waiting_url)
async def handle_url_input(message: Message, state: FSMContext):
    """URL daxiletməsi"""
    user = message.from_user
    lang = get_lang(user)

    url = message.text
    if not url:
        return

    data = await state.get_data()
    btn_type = data.get("current_btn_type", "url")

    # URL yoxla
    if btn_type == "webapp" and not is_valid_https_url(url):
        await message.answer(t("invalid_url", lang) + "\nWeb App üçün HTTPS tələb olunur.")
        return
    elif btn_type != "webapp" and not is_valid_url(url):
        await message.answer(t("invalid_url", lang))
        return

    btn_text = data.get("current_btn_text", "Düymə")
    await _add_button_final(message, state, btn_text, url, btn_type, lang)


# ─── Callback düymə ─────────────────────────────────────────────────────────

@router.message(ButtonStates.waiting_callback_text)
async def handle_callback_btn_text(message: Message, state: FSMContext):
    """Callback düymə mətni"""
    user = message.from_user
    lang = get_lang(user)

    text = message.text
    if not text or len(text) > 200:
        await message.answer("❌ Düymə mətni 1-200 simvol arası olmalıdır.")
        return

    await state.update_data(current_btn_text=text)
    await state.set_state(ButtonStates.waiting_callback_data)

    await message.answer(
        t("waiting_callback_data", lang),
        reply_markup=back_cancel_keyboard("btn:add", lang),
    )


@router.message(ButtonStates.waiting_callback_data)
async def handle_callback_data(message: Message, state: FSMContext):
    """Callback data daxiletməsi"""
    user = message.from_user
    lang = get_lang(user)

    data_text = message.text
    if not data_text:
        return

    if len(data_text) > 64:
        await message.answer(t("callback_too_long", lang))
        return

    data = await state.get_data()
    btn_text = data.get("current_btn_text", "Düymə")
    await _add_button_final(message, state, btn_text, data_text, "callback", lang)


# ─── Switch Inline ───────────────────────────────────────────────────────────

@router.message(ButtonStates.waiting_switch_text)
async def handle_switch_text(message: Message, state: FSMContext):
    """Switch düymə mətni"""
    user = message.from_user
    lang = get_lang(user)

    text = message.text
    if not text:
        return

    await state.update_data(current_btn_text=text)
    await state.set_state(ButtonStates.waiting_switch_query)

    await message.answer(
        t("waiting_switch_query", lang),
        reply_markup=back_cancel_keyboard("btn:add", lang),
    )


@router.message(ButtonStates.waiting_switch_query)
async def handle_switch_query(message: Message, state: FSMContext):
    """Switch query daxiletməsi"""
    user = message.from_user
    lang = get_lang(user)

    query = message.text or ""
    data = await state.get_data()
    btn_text = data.get("current_btn_text", "Düymə")
    btn_type = data.get("current_btn_type", "switch_inline")
    await _add_button_final(message, state, btn_text, query, btn_type, lang)


# ─── Copy Text ───────────────────────────────────────────────────────────────

@router.message(ButtonStates.waiting_copy_text)
async def handle_copy_btn_text(message: Message, state: FSMContext):
    """Copy düymə mətni"""
    user = message.from_user
    lang = get_lang(user)

    text = message.text
    if not text:
        return

    await state.update_data(current_btn_text=text)
    await state.set_state(ButtonStates.waiting_copy_value)

    await message.answer(
        t("waiting_copy_value", lang),
        reply_markup=back_cancel_keyboard("btn:add", lang),
    )


@router.message(ButtonStates.waiting_copy_value)
async def handle_copy_value(message: Message, state: FSMContext):
    """Kopyalanacaq mətn"""
    user = message.from_user
    lang = get_lang(user)

    value = message.text
    if not value:
        return

    data = await state.get_data()
    btn_text = data.get("current_btn_text", "Düymə")
    await _add_button_final(message, state, btn_text, value, "copy", lang)


# ─── Login URL ───────────────────────────────────────────────────────────────

@router.message(ButtonStates.waiting_login_text)
async def handle_login_btn_text(message: Message, state: FSMContext):
    """Login düymə mətni"""
    user = message.from_user
    lang = get_lang(user)

    text = message.text
    if not text:
        return

    await state.update_data(current_btn_text=text)
    await state.set_state(ButtonStates.waiting_login_url)

    await message.answer(
        t("waiting_login_url", lang),
        reply_markup=back_cancel_keyboard("btn:add", lang),
    )


@router.message(ButtonStates.waiting_login_url)
async def handle_login_url(message: Message, state: FSMContext):
    """Login URL daxiletməsi"""
    user = message.from_user
    lang = get_lang(user)

    url = message.text
    if not url or not is_valid_https_url(url):
        await message.answer(t("invalid_url", lang))
        return

    data = await state.get_data()
    btn_text = data.get("current_btn_text", "Düymə")
    await _add_button_final(message, state, btn_text, url, "login", lang)


# ─── Web App ─────────────────────────────────────────────────────────────────

@router.message(ButtonStates.waiting_webapp_text)
async def handle_webapp_text(message: Message, state: FSMContext):
    """Web App düymə mətni"""
    user = message.from_user
    lang = get_lang(user)

    text = message.text
    if not text:
        return

    await state.update_data(current_btn_text=text)
    await state.set_state(ButtonStates.waiting_webapp_url)

    await message.answer(
        t("waiting_webapp_url", lang),
        reply_markup=back_cancel_keyboard("btn:add", lang),
    )


# ─── Ümumi düymə əlavə etmə ─────────────────────────────────────────────────

async def _add_button_final(
    message: Message,
    state: FSMContext,
    text: str,
    value: str,
    btn_type: str,
    lang: str,
):
    """Düymə əlavə etmə prosesini tamamla"""
    data = await state.get_data()
    post_dict = data.get("post_data")
    post = PostData.from_dict(post_dict) if post_dict else PostData()

    new_row = data.get("force_new_row", False)

    button = ButtonData(
        text=text,
        button_type=btn_type,
        value=value,
    )
    post.add_button(button, new_row=new_row)

    await state.update_data(post_data=post.to_dict(), force_new_row=False)
    await state.set_state(PostStates.post_menu)

    emoji = get_button_type_emoji(btn_type)
    await message.answer(
        f"✅ Düymə əlavə edildi!\n\n"
        f"{emoji} <b>{text}</b>\n"
        f"Növ: {btn_type}\n"
        f"Cəmi düymə: {post.get_button_count()}",
        reply_markup=button_menu_keyboard(post, lang),
    )

    await log_action(message.from_user.id, "add_button", {
        "type": btn_type,
        "text": text[:50],
    })


@router.callback_query(F.data.startswith("btn_view:"))
async def cb_view_button_detail(callback: CallbackQuery, state: FSMContext):
    """Düymə detallarını göstər"""
    index = int(callback.data.split(":")[1])
    post = await get_post(state)

    if 0 <= index < len(post.buttons):
        btn = post.buttons[index]
        emoji = get_button_type_emoji(btn.button_type)
        detail = (
            f"{emoji} <b>Düymə #{index + 1}</b>\n\n"
            f"📝 Mətn: <code>{btn.text}</code>\n"
            f"🔧 Növ: <code>{btn.button_type}</code>\n"
        )
        if btn.value:
            val_preview = truncate_text(btn.value, 100)
            detail += f"🔗 Dəyər: <code>{val_preview}</code>\n"
        detail += f"📍 Mövqe: sətir {btn.row + 1}, sütun {btn.col + 1}"

        await callback.answer(detail[:200], show_alert=True)
    else:
        await callback.answer("Düymə tapılmadı", show_alert=True)
