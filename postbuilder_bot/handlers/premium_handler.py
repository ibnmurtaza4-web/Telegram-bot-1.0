"""
Premium Handler - Deep Link, UTM, QR Kod, Markdown↔HTML çevirmə
"""

import logging
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, BufferedInputFile
from aiogram.fsm.context import FSMContext

from states import PremiumStates
from keyboards import premium_menu_keyboard, back_cancel_keyboard
from locales import get_user_lang, t
from utils.helpers import (
    generate_deep_link, generate_utm_url,
    markdown_to_html, html_to_markdown,
    estimate_message_size, is_valid_url,
)

router = Router()
logger = logging.getLogger(__name__)


def get_lang(user): return get_user_lang(getattr(user, "language_code", "az"))


@router.callback_query(F.data == "premium")
async def cb_premium(callback: CallbackQuery, state: FSMContext):
    lang = get_lang(callback.from_user)
    await state.set_state(PremiumStates.main)
    await callback.message.edit_text(t("premium_menu", lang), reply_markup=premium_menu_keyboard(lang))
    await callback.answer()


# ─── Deep Link ───────────────────────────────────────────────────────────────

@router.callback_query(F.data == "premium:deeplink")
async def cb_deep_link(callback: CallbackQuery, state: FSMContext):
    lang = get_lang(callback.from_user)
    await state.set_state(PremiumStates.waiting_deep_link_bot)
    await callback.message.edit_text(
        t("waiting_deep_link_bot", lang),
        reply_markup=back_cancel_keyboard("premium", lang),
    )
    await callback.answer()


@router.message(PremiumStates.waiting_deep_link_bot)
async def handle_deep_link_bot(message: Message, state: FSMContext):
    lang = get_lang(message.from_user)
    username = message.text.strip()
    await state.update_data(dl_bot=username)
    await state.set_state(PremiumStates.waiting_deep_link_param)
    await message.answer(
        t("waiting_deep_link_param", lang),
        reply_markup=back_cancel_keyboard("premium", lang),
    )


@router.message(PremiumStates.waiting_deep_link_param)
async def handle_deep_link_param(message: Message, state: FSMContext):
    lang = get_lang(message.from_user)
    param = message.text.strip() if message.text.strip() != "-" else ""
    data = await state.get_data()
    bot_username = data.get("dl_bot", "bot")

    start_link, startgroup_link = generate_deep_link(bot_username, param)

    await state.set_state(PremiumStates.main)
    await message.answer(
        f"🔗 <b>Deep Link Nəticəsi:</b>\n\n"
        f"▶️ <b>Start:</b>\n<code>{start_link}</code>\n\n"
        f"👥 <b>Start Group:</b>\n<code>{startgroup_link}</code>",
        reply_markup=premium_menu_keyboard(lang),
    )


# ─── UTM Generator ───────────────────────────────────────────────────────────

@router.callback_query(F.data == "premium:utm")
async def cb_utm(callback: CallbackQuery, state: FSMContext):
    lang = get_lang(callback.from_user)
    await state.set_state(PremiumStates.waiting_utm_url)
    await callback.message.edit_text(
        t("waiting_utm_url", lang),
        reply_markup=back_cancel_keyboard("premium", lang),
    )
    await callback.answer()


@router.message(PremiumStates.waiting_utm_url)
async def handle_utm_url(message: Message, state: FSMContext):
    lang = get_lang(message.from_user)
    url = message.text.strip()
    if not is_valid_url(url):
        await message.answer("❌ Düzgün URL deyil.")
        return
    await state.update_data(utm_url=url)
    await state.set_state(PremiumStates.waiting_utm_source)
    await message.answer(t("waiting_utm_source", lang))


@router.message(PremiumStates.waiting_utm_source)
async def handle_utm_source(message: Message, state: FSMContext):
    await state.update_data(utm_source=message.text.strip())
    await state.set_state(PremiumStates.waiting_utm_medium)
    await message.answer(t("waiting_utm_medium", "az"))


@router.message(PremiumStates.waiting_utm_medium)
async def handle_utm_medium(message: Message, state: FSMContext):
    await state.update_data(utm_medium=message.text.strip())
    await state.set_state(PremiumStates.waiting_utm_campaign)
    await message.answer(t("waiting_utm_campaign", "az"))


@router.message(PremiumStates.waiting_utm_campaign)
async def handle_utm_campaign(message: Message, state: FSMContext):
    lang = get_lang(message.from_user)
    data = await state.get_data()

    final_url = generate_utm_url(
        url=data["utm_url"],
        source=data["utm_source"],
        medium=data["utm_medium"],
        campaign=message.text.strip(),
    )

    await state.set_state(PremiumStates.main)
    await message.answer(
        f"📊 <b>UTM Link hazırdır:</b>\n\n<code>{final_url}</code>",
        reply_markup=premium_menu_keyboard(lang),
    )


# ─── QR Kod ──────────────────────────────────────────────────────────────────

@router.callback_query(F.data == "premium:qr")
async def cb_qr(callback: CallbackQuery, state: FSMContext):
    lang = get_lang(callback.from_user)
    await state.set_state(PremiumStates.waiting_qr_text)
    await callback.message.edit_text(
        t("waiting_qr_text", lang),
        reply_markup=back_cancel_keyboard("premium", lang),
    )
    await callback.answer()


@router.message(PremiumStates.waiting_qr_text)
async def handle_qr_text(message: Message, state: FSMContext):
    lang = get_lang(message.from_user)
    text = message.text.strip()

    processing = await message.answer("⏳ QR kod yaradılır...")

    try:
        import qrcode
        import io

        qr = qrcode.QRCode(version=1, box_size=10, border=4)
        qr.add_data(text)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")

        buf = io.BytesIO()
        img.save(buf, format="PNG")
        buf.seek(0)

        await processing.delete()
        await message.answer_photo(
            photo=BufferedInputFile(buf.read(), filename="qrcode.png"),
            caption=f"📱 <b>QR Kod</b>\n\n<code>{text[:100]}</code>",
            reply_markup=premium_menu_keyboard(lang),
        )
    except ImportError:
        await processing.edit_text(
            "❌ QR kod kitabxanası quraşdırılmayıb.\n"
            "Quraşdırın: <code>pip install qrcode[pil]</code>",
            reply_markup=premium_menu_keyboard(lang),
        )
    except Exception as e:
        await processing.edit_text(f"❌ QR kod yaratma xətası: {e}")

    await state.set_state(PremiumStates.main)


# ─── Markdown ↔ HTML ─────────────────────────────────────────────────────────

@router.callback_query(F.data == "premium:convert")
async def cb_convert(callback: CallbackQuery, state: FSMContext):
    lang = get_lang(callback.from_user)
    await state.set_state(PremiumStates.markdown_html)

    from aiogram.utils.keyboard import InlineKeyboardBuilder
    from aiogram.types import InlineKeyboardButton
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="📄 Markdown → HTML", callback_data="conv:md2html"),
        InlineKeyboardButton(text="📄 HTML → Markdown", callback_data="conv:html2md"),
    )
    builder.row(InlineKeyboardButton(text="⬅️ Geri", callback_data="premium"))

    await callback.message.edit_text("🔄 <b>Format Çevirmə</b>\n\nNə çevirmək istəyirsiniz?", reply_markup=builder.as_markup())
    await callback.answer()


@router.callback_query(F.data.startswith("conv:"))
async def cb_conv_type(callback: CallbackQuery, state: FSMContext):
    conv_type = callback.data.split(":")[1]
    await state.update_data(conv_type=conv_type)
    await state.set_state(PremiumStates.waiting_convert_text)
    await callback.message.edit_text("✏️ Çevirmək istədiyiniz mətni göndərin:")
    await callback.answer()


@router.message(PremiumStates.waiting_convert_text)
async def handle_convert(message: Message, state: FSMContext):
    lang = get_lang(message.from_user)
    data = await state.get_data()
    conv_type = data.get("conv_type", "md2html")
    text = message.text or ""

    if conv_type == "md2html":
        result = markdown_to_html(text)
        label = "Markdown → HTML"
    else:
        result = html_to_markdown(text)
        label = "HTML → Markdown"

    await state.set_state(PremiumStates.main)
    await message.answer(
        f"✅ <b>{label} nəticəsi:</b>\n\n<pre>{result[:3000]}</pre>",
        reply_markup=premium_menu_keyboard(lang),
    )


# ─── Limit Yoxlayıcı ─────────────────────────────────────────────────────────

@router.callback_query(F.data == "premium:limits")
async def cb_limits(callback: CallbackQuery, state: FSMContext):
    lang = get_lang(callback.from_user)
    from handlers.post_builder import get_post_data
    post_dict = (await state.get_data()).get("post_data")
    from utils.post_data import PostData
    post = PostData.from_dict(post_dict) if post_dict else PostData()

    text_len = len(post.text) if post.text else 0
    size = estimate_message_size(post.text or "")

    info = (
        "📏 <b>Bot API Limitləri</b>\n\n"
        f"📝 Mətn uzunluğu: <b>{text_len}</b> simvol\n"
        f"  • Mesaj limiti (4096): {'✅' if text_len <= 4096 else '❌'}\n"
        f"  • Caption limiti (1024): {'✅' if text_len <= 1024 else '❌'}\n\n"
        f"🔘 Düymə sayı: <b>{post.get_button_count()}</b>\n"
        f"  • Sətir limiti (100): ✅\n"
        f"  • Sütun limiti (8): ✅\n\n"
        f"🖼 Media: {'✅ Əlavə edilib' if post.media else '⭕ Yoxdur'}\n"
        f"📸 Albom: {'✅ ' + str(len(post.media_group)) + ' media' if post.media_group else '⭕ Yoxdur'}\n"
    )

    await callback.message.edit_text(info, reply_markup=premium_menu_keyboard(lang))
    await callback.answer()


@router.callback_query(F.data == "premium:history")
async def cb_history(callback: CallbackQuery, state: FSMContext):
    lang = get_lang(callback.from_user)
    from database import get_user_drafts
    drafts = await get_user_drafts(callback.from_user.id)

    if not drafts:
        await callback.answer("📜 Hələ heç bir qaralama yoxdur.", show_alert=True)
        return

    history_text = "📜 <b>Son Qaralamalar</b>\n\n"
    for d in drafts[:10]:
        history_text += f"• <b>{d.name}</b> — {d.updated_at.strftime('%d.%m.%Y %H:%M')}\n"

    await callback.message.edit_text(history_text, reply_markup=premium_menu_keyboard(lang))
    await callback.answer()
