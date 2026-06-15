"""
Templates Handler - Hazır şablonlar
"""

import logging
from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext

from states import TemplateStates, PostStates
from utils.post_data import PostData, ButtonData
from keyboards import templates_keyboard, post_builder_keyboard, back_cancel_keyboard, drafts_keyboard
from locales import get_user_lang
from database import get_user_drafts, save_draft

router = Router()
logger = logging.getLogger(__name__)


def get_lang(user): return get_user_lang(getattr(user, "language_code", "az"))


async def get_post(state):
    d = await state.get_data(); p = d.get("post_data")
    return PostData.from_dict(p) if p else PostData()


async def save_post(state, post): await state.update_data(post_data=post.to_dict())


BUILTIN_TEMPLATES = {
    "channel": {
        "name": "Kanal Postu",
        "text": (
            "📢 <b>KANAL ADI</b>\n\n"
            "📝 <i>Burada postun əsas mətni yerləşir. Vacib məlumatları qısa və aydın şəkildə yazın.</i>\n\n"
            "✅ Xüsusiyyət 1\n"
            "✅ Xüsusiyyət 2\n"
            "✅ Xüsusiyyət 3\n\n"
            "📌 <b>Əlaqə:</b> @username"
        ),
        "buttons": [
            {"text": "🌐 Vebsayt", "button_type": "url", "value": "https://example.com", "row": 0, "col": 0, "style": "default"},
            {"text": "📢 Kanal", "button_type": "url", "value": "https://t.me/channel", "row": 0, "col": 1, "style": "default"},
        ]
    },
    "news": {
        "name": "Xəbər Postu",
        "text": (
            "🗞 <b>XƏBƏRİN BAŞLIĞI</b>\n\n"
            "📅 <i>Tarix: DD.MM.YYYY</i>\n\n"
            "Xəbərin ətraflı məzmunu burada yerləşir. Vacib faktları, rəqəmləri və əsas məlumatları qeyd edin.\n\n"
            "🔗 <b>Mənbə:</b> <a href='https://example.com'>Tam oxu</a>"
        ),
        "buttons": [
            {"text": "📖 Tam oxu", "button_type": "url", "value": "https://example.com", "row": 0, "col": 0, "style": "default"},
            {"text": "📤 Paylaş", "button_type": "switch_inline", "value": "", "row": 0, "col": 1, "style": "default"},
        ]
    },
    "announcement": {
        "name": "Elan",
        "text": (
            "📣 <b>ELAN</b>\n\n"
            "Hörmətli istifadəçilər,\n\n"
            "<i>Elanın məzmunu burada yazılır. Vacib məlumatları aydın şəkildə çatdırın.</i>\n\n"
            "⏰ <b>Tarix:</b> DD.MM.YYYY\n"
            "📍 <b>Yer:</b> Yer adı\n\n"
            "❓ Suallarınız üçün əlaqə saxlayın."
        ),
        "buttons": [
            {"text": "✅ Qeydiyyat", "button_type": "url", "value": "https://example.com", "row": 0, "col": 0, "style": "default"},
            {"text": "📞 Əlaqə", "button_type": "url", "value": "https://t.me/username", "row": 1, "col": 0, "style": "default"},
        ]
    },
    "giveaway": {
        "name": "Giveaway",
        "text": (
            "🎁 <b>GIVEAWAY!</b>\n\n"
            "🏆 <b>Mükafat:</b> [Mükafatı yazın]\n\n"
            "📋 <b>İştirak şərtləri:</b>\n"
            "1️⃣ Kanala abunə ol\n"
            "2️⃣ Bu postu 3 dostuna göndər\n"
            "3️⃣ Aşağıdakı düyməyə klik et\n\n"
            "⏰ <b>Bitmə tarixi:</b> DD.MM.YYYY saat HH:MM\n\n"
            "🎰 Qalib təsadüfi seçiləcək!"
        ),
        "buttons": [
            {"text": "🎁 İştirak et!", "button_type": "url", "value": "https://example.com", "row": 0, "col": 0, "style": "default"},
            {"text": "📢 Kanal", "button_type": "url", "value": "https://t.me/channel", "row": 1, "col": 0, "style": "default"},
        ]
    },
    "file": {
        "name": "Fayl Paylaşımı",
        "text": (
            "📁 <b>FAYL ADI</b>\n\n"
            "📝 <b>Təsvir:</b>\n"
            "Faylın qısa təsviri burada yazılır.\n\n"
            "📊 <b>Ölçü:</b> XX MB\n"
            "🔖 <b>Format:</b> PDF/ZIP/vb.\n"
            "📅 <b>Tarix:</b> DD.MM.YYYY\n\n"
            "⬇️ Yükləmək üçün düyməyə klik edin:"
        ),
        "buttons": [
            {"text": "⬇️ Yüklə", "button_type": "url", "value": "https://example.com/file", "row": 0, "col": 0, "style": "default"},
        ]
    },
    "discount": {
        "name": "Endirim Kampaniyası",
        "text": (
            "🔥 <b>ENDİRİM!</b>\n\n"
            "💰 <b>Məhsul:</b> Məhsul adı\n"
            "❌ ~~Köhnə qiymət: XX AZN~~\n"
            "✅ <b>Yeni qiymət: XX AZN</b>\n"
            "🏷 <b>Endirim: XX%</b>\n\n"
            "⏰ Təklif <b>DD.MM.YYYY</b> tarixinə qədər keçərlidir!\n\n"
            "🛒 İndi sifariş et:"
        ),
        "buttons": [
            {"text": "🛒 Sifariş et", "button_type": "url", "value": "https://example.com", "row": 0, "col": 0, "style": "default"},
            {"text": "📞 Əlaqə", "button_type": "url", "value": "https://t.me/username", "row": 0, "col": 1, "style": "default"},
        ]
    },
    "lesson": {
        "name": "Dərs Paylaşımı",
        "text": (
            "📚 <b>DƏRS ADI</b>\n\n"
            "👨‍🏫 <b>Müəllim:</b> Ad Soyad\n"
            "📖 <b>Mövzu:</b> Mövzu adı\n"
            "⏱ <b>Müddət:</b> XX dəqiqə\n"
            "🎯 <b>Səviyyə:</b> Başlanğıc/Orta/İrəliləmiş\n\n"
            "📝 <b>Dərsdə öyrənəcəksiniz:</b>\n"
            "• Mövzu 1\n"
            "• Mövzu 2\n"
            "• Mövzu 3"
        ),
        "buttons": [
            {"text": "▶️ İzlə", "button_type": "url", "value": "https://example.com", "row": 0, "col": 0, "style": "default"},
            {"text": "📥 Materiallar", "button_type": "url", "value": "https://example.com/materials", "row": 0, "col": 1, "style": "default"},
        ]
    },
    "nav_menu": {
        "name": "Yönləndirici Menyu",
        "text": (
            "🗂 <b>ANA MENYU</b>\n\n"
            "Aşağıdakı bölmələrdən birini seçin:"
        ),
        "buttons": [
            {"text": "📢 Haqqımızda", "button_type": "url", "value": "https://t.me/channel", "row": 0, "col": 0, "style": "default"},
            {"text": "🛒 Məhsullar", "button_type": "url", "value": "https://example.com/products", "row": 0, "col": 1, "style": "default"},
            {"text": "📞 Əlaqə", "button_type": "url", "value": "https://t.me/username", "row": 1, "col": 0, "style": "default"},
            {"text": "❓ FAQ", "button_type": "url", "value": "https://example.com/faq", "row": 1, "col": 1, "style": "default"},
        ]
    },
    "faq": {
        "name": "FAQ Menyusu",
        "text": (
            "❓ <b>Tez-tez verilən suallar</b>\n\n"
            "Aşağıdakı suallar üzrə cavablar üçün düyməyə klikləyin:"
        ),
        "buttons": [
            {"text": "❓ Sual 1", "button_type": "callback", "value": "faq_1", "row": 0, "col": 0, "style": "default"},
            {"text": "❓ Sual 2", "button_type": "callback", "value": "faq_2", "row": 1, "col": 0, "style": "default"},
            {"text": "❓ Sual 3", "button_type": "callback", "value": "faq_3", "row": 2, "col": 0, "style": "default"},
            {"text": "📞 Dəstək", "button_type": "url", "value": "https://t.me/support", "row": 3, "col": 0, "style": "default"},
        ]
    },
    "support": {
        "name": "Dəstək Menyusu",
        "text": (
            "🆘 <b>DƏSTƏк MƏRKƏZİ</b>\n\n"
            "Sizə necə kömək edə bilərik?\n\n"
            "⏰ İş saatları: 09:00 - 18:00 (İş günləri)"
        ),
        "buttons": [
            {"text": "💬 Canlı Dəstək", "button_type": "url", "value": "https://t.me/support_agent", "row": 0, "col": 0, "style": "default"},
            {"text": "📧 E-poçt", "button_type": "url", "value": "https://example.com/contact", "row": 0, "col": 1, "style": "default"},
            {"text": "📋 Bilet aç", "button_type": "url", "value": "https://example.com/ticket", "row": 1, "col": 0, "style": "default"},
            {"text": "❓ FAQ", "button_type": "url", "value": "https://example.com/faq", "row": 1, "col": 1, "style": "default"},
        ]
    },
    "social": {
        "name": "Sosial Şəbəkə Keçidləri",
        "text": (
            "🌐 <b>BİZİ İZLƏYİN</b>\n\n"
            "Bütün platformalarda bizimlə əlaqədə qalın:"
        ),
        "buttons": [
            {"text": "📱 Telegram", "button_type": "url", "value": "https://t.me/channel", "row": 0, "col": 0, "style": "default"},
            {"text": "📸 Instagram", "button_type": "url", "value": "https://instagram.com/username", "row": 0, "col": 1, "style": "default"},
            {"text": "🐦 Twitter/X", "button_type": "url", "value": "https://twitter.com/username", "row": 1, "col": 0, "style": "default"},
            {"text": "▶️ YouTube", "button_type": "url", "value": "https://youtube.com/@channel", "row": 1, "col": 1, "style": "default"},
            {"text": "💼 LinkedIn", "button_type": "url", "value": "https://linkedin.com/company/name", "row": 2, "col": 0, "style": "default"},
        ]
    },
    "premium": {
        "name": "Premium Abunə Postu",
        "text": (
            "⭐ <b>PREMIUM ÜZVLÜK</b>\n\n"
            "🔥 <b>Premium ilə əldə edin:</b>\n"
            "✅ Xüsusiyyət 1\n"
            "✅ Xüsusiyyət 2\n"
            "✅ Xüsusiyyət 3\n"
            "✅ Xüsusiyyət 4\n\n"
            "💰 <b>Qiymət:</b>\n"
            "• Aylıq: XX AZN\n"
            "• İllik: XX AZN (XX% endirim)\n\n"
            "🚀 İndi başla!"
        ),
        "buttons": [
            {"text": "⭐ Premium al", "button_type": "url", "value": "https://example.com/premium", "row": 0, "col": 0, "style": "default"},
            {"text": "ℹ️ Ətraflı", "button_type": "url", "value": "https://example.com/premium/info", "row": 1, "col": 0, "style": "default"},
        ]
    },
}


@router.callback_query(F.data == "templates")
async def cb_templates(callback: CallbackQuery, state: FSMContext):
    lang = get_lang(callback.from_user)
    await callback.message.edit_text("📋 <b>Şablonlar</b>\n\nHazır şablonlardan seçin:", reply_markup=templates_keyboard(lang))
    await callback.answer()


@router.callback_query(F.data.startswith("tpl:"))
async def cb_template_chosen(callback: CallbackQuery, state: FSMContext):
    lang = get_lang(callback.from_user)
    tpl_key = callback.data.split(":")[1]

    if tpl_key == "my":
        user_id = callback.from_user.id
        drafts = await get_user_drafts(user_id, templates_only=True)
        if not drafts:
            await callback.answer("📋 Hələ öz şablonunuz yoxdur.", show_alert=True)
            return
        await callback.message.edit_text(
            f"⭐ <b>Öz Şablonlarım</b>\n\nCəmi: {len(drafts)} şablon",
            reply_markup=drafts_keyboard(drafts),
        )
        await callback.answer()
        return

    tpl = BUILTIN_TEMPLATES.get(tpl_key)
    if not tpl:
        await callback.answer("❌ Şablon tapılmadı", show_alert=True)
        return

    post = PostData()
    post.text = tpl["text"]
    for btn_data in tpl.get("buttons", []):
        post.buttons.append(ButtonData.from_dict(btn_data))

    await state.update_data(post_data=post.to_dict())
    await state.set_state(PostStates.post_menu)

    await callback.message.edit_text(
        f"✅ <b>{tpl['name']}</b> şablonu tətbiq edildi!\n\nMətni və düymələri öz məlumatlarınıza uyğun dəyişdirin.",
        reply_markup=post_builder_keyboard(post, lang),
    )
    await callback.answer()
