"""
Klaviatura qurucuları - Bütün inline və reply klaviaturalar
"""

from aiogram.types import (
    InlineKeyboardMarkup, InlineKeyboardButton,
    ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove,
)
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from typing import List, Optional
from utils.post_data import PostData, ButtonData


def main_menu_keyboard(lang: str = "az") -> InlineKeyboardMarkup:
    """Ana menyu klaviaturası"""
    from locales import t
    builder = InlineKeyboardBuilder()

    builder.row(
        InlineKeyboardButton(text=t("btn_new_post", lang), callback_data="new_post"),
        InlineKeyboardButton(text=t("btn_my_drafts", lang), callback_data="my_drafts"),
    )
    builder.row(
        InlineKeyboardButton(text=t("btn_templates", lang), callback_data="templates"),
        InlineKeyboardButton(text=t("btn_json_mode", lang), callback_data="json_mode"),
    )
    builder.row(
        InlineKeyboardButton(text=t("btn_premium", lang), callback_data="premium"),
    )
    builder.row(
        InlineKeyboardButton(text=t("btn_help", lang), callback_data="help"),
        InlineKeyboardButton(text=t("btn_settings", lang), callback_data="settings"),
    )

    return builder.as_markup()


def post_builder_keyboard(post: PostData, lang: str = "az") -> InlineKeyboardMarkup:
    """Post qurucusu klaviaturası"""
    from locales import t
    builder = InlineKeyboardBuilder()

    has_text = bool(post.text)
    has_media = bool(post.media or post.media_group)
    has_buttons = post.get_button_count() > 0

    # Status emoji-ləri
    text_emoji = "✅" if has_text else "➕"
    media_emoji = "✅" if has_media else "➕"
    btn_emoji = f"✅({post.get_button_count()})" if has_buttons else "➕"

    builder.row(
        InlineKeyboardButton(
            text=f"{text_emoji} Mətn",
            callback_data="pb:text"
        ),
        InlineKeyboardButton(
            text=f"{media_emoji} Media",
            callback_data="pb:media"
        ),
    )
    builder.row(
        InlineKeyboardButton(
            text=f"{btn_emoji} Düymələr",
            callback_data="pb:buttons"
        ),
        InlineKeyboardButton(
            text="⚙️ Seçimlər",
            callback_data="pb:options"
        ),
    )

    if post.has_content():
        builder.row(
            InlineKeyboardButton(text="👁 Önizləmə", callback_data="pb:preview"),
            InlineKeyboardButton(text="📤 Göndər", callback_data="pb:send"),
        )
        builder.row(
            InlineKeyboardButton(text="💾 Qaralama saxla", callback_data="pb:save_draft"),
        )

    builder.row(
        InlineKeyboardButton(text="🗑 Sıfırla", callback_data="pb:reset"),
        InlineKeyboardButton(text="🏠 Ana Menyu", callback_data="main_menu"),
    )

    return builder.as_markup()


def text_format_keyboard(lang: str = "az") -> InlineKeyboardMarkup:
    """Mətn formatlaşdırma klaviaturası"""
    builder = InlineKeyboardBuilder()

    builder.row(
        InlineKeyboardButton(text="𝐁 Qalın", callback_data="fmt:bold"),
        InlineKeyboardButton(text="𝐼 Kursiv", callback_data="fmt:italic"),
        InlineKeyboardButton(text="U̲ Altxətt", callback_data="fmt:underline"),
    )
    builder.row(
        InlineKeyboardButton(text="S̶ Üstxətt", callback_data="fmt:strike"),
        InlineKeyboardButton(text="👁 Spoiler", callback_data="fmt:spoiler"),
        InlineKeyboardButton(text="</> Kod", callback_data="fmt:code"),
    )
    builder.row(
        InlineKeyboardButton(text="📦 Pre", callback_data="fmt:pre"),
        InlineKeyboardButton(text="💬 Sitat", callback_data="fmt:quote"),
        InlineKeyboardButton(text="🔗 Keçid", callback_data="fmt:link"),
    )
    builder.row(
        InlineKeyboardButton(text="📏 Ölçü yoxla", callback_data="fmt:check_size"),
    )
    builder.row(
        InlineKeyboardButton(text="✅ Mətni tətbiq et", callback_data="fmt:apply"),
        InlineKeyboardButton(text="⬅️ Geri", callback_data="pb:back"),
    )

    return builder.as_markup()


def media_type_keyboard(lang: str = "az") -> InlineKeyboardMarkup:
    """Media növü seçim klaviaturası"""
    builder = InlineKeyboardBuilder()

    builder.row(
        InlineKeyboardButton(text="🖼 Şəkil", callback_data="media:photo"),
        InlineKeyboardButton(text="🎥 Video", callback_data="media:video"),
    )
    builder.row(
        InlineKeyboardButton(text="🎵 Audio", callback_data="media:audio"),
        InlineKeyboardButton(text="🎤 Səs", callback_data="media:voice"),
    )
    builder.row(
        InlineKeyboardButton(text="🎬 GIF", callback_data="media:animation"),
        InlineKeyboardButton(text="📄 Sənəd", callback_data="media:document"),
    )
    builder.row(
        InlineKeyboardButton(text="📸 Albom", callback_data="media:group"),
    )
    builder.row(
        InlineKeyboardButton(text="🗑 Medianı sil", callback_data="media:remove"),
        InlineKeyboardButton(text="⬅️ Geri", callback_data="pb:back"),
    )

    return builder.as_markup()


def button_type_keyboard(lang: str = "az") -> InlineKeyboardMarkup:
    """Düymə növü seçim klaviaturası"""
    builder = InlineKeyboardBuilder()

    builder.row(
        InlineKeyboardButton(text="🔗 URL Düymə", callback_data="btn_type:url"),
        InlineKeyboardButton(text="📡 Callback", callback_data="btn_type:callback"),
    )
    builder.row(
        InlineKeyboardButton(text="🌐 Web App", callback_data="btn_type:webapp"),
        InlineKeyboardButton(text="📤 Paylaş", callback_data="btn_type:share"),
    )
    builder.row(
        InlineKeyboardButton(text="🔄 Switch Inline", callback_data="btn_type:switch_inline"),
        InlineKeyboardButton(text="💬 Switch Current", callback_data="btn_type:switch_current"),
    )
    builder.row(
        InlineKeyboardButton(text="📋 Mətn kopyala", callback_data="btn_type:copy"),
        InlineKeyboardButton(text="🔑 Login URL", callback_data="btn_type:login"),
    )
    builder.row(
        InlineKeyboardButton(text="🎮 Oyun", callback_data="btn_type:game"),
        InlineKeyboardButton(text="💳 Ödəniş", callback_data="btn_type:pay"),
    )
    builder.row(
        InlineKeyboardButton(text="⬅️ Geri", callback_data="pb:buttons"),
    )

    return builder.as_markup()


def button_menu_keyboard(post: PostData, lang: str = "az") -> InlineKeyboardMarkup:
    """Düymə idarəetmə menyusu"""
    builder = InlineKeyboardBuilder()

    button_count = post.get_button_count()

    builder.row(
        InlineKeyboardButton(text="➕ Düymə əlavə et", callback_data="btn:add"),
    )
    builder.row(
        InlineKeyboardButton(text="↵ Yeni sətir", callback_data="btn:new_row"),
    )

    if button_count > 0:
        builder.row(
            InlineKeyboardButton(text=f"📋 Düymələrə bax ({button_count})", callback_data="btn:view"),
        )
        builder.row(
            InlineKeyboardButton(text="✏️ Düymə redaktə et", callback_data="btn:edit"),
            InlineKeyboardButton(text="🗑 Düymə sil", callback_data="btn:delete"),
        )
        builder.row(
            InlineKeyboardButton(text="🗑 Hamısını sil", callback_data="btn:clear_all"),
        )

    builder.row(
        InlineKeyboardButton(text="🔧 JSON idxal/ixrac", callback_data="btn:json"),
    )
    builder.row(
        InlineKeyboardButton(text="⬅️ Geri", callback_data="pb:back"),
    )

    return builder.as_markup()


def buttons_list_keyboard(post: PostData, action: str = "view") -> InlineKeyboardMarkup:
    """Düymələrin siyahısı"""
    builder = InlineKeyboardBuilder()

    for i, btn in enumerate(post.buttons):
        from utils.helpers import get_button_type_emoji, truncate_text
        emoji = get_button_type_emoji(btn.button_type)
        text = truncate_text(btn.text, 20)
        builder.row(
            InlineKeyboardButton(
                text=f"{emoji} {text} [sır:{btn.row+1}, sütun:{btn.col+1}]",
                callback_data=f"btn_{action}:{i}",
            )
        )

    builder.row(
        InlineKeyboardButton(text="⬅️ Geri", callback_data="btn:menu"),
    )

    return builder.as_markup()


def send_target_keyboard(lang: str = "az") -> InlineKeyboardMarkup:
    """Göndərmə hədəfi seçim klaviaturası"""
    builder = InlineKeyboardBuilder()

    builder.row(
        InlineKeyboardButton(text="👤 Özümə", callback_data="send:me"),
    )
    builder.row(
        InlineKeyboardButton(text="💬 Çat/Kanal/Qrup ID ilə", callback_data="send:custom"),
    )
    builder.row(
        InlineKeyboardButton(text="📡 Çox hədəfə", callback_data="send:multiple"),
    )
    builder.row(
        InlineKeyboardButton(text="⏰ Planlaşdır", callback_data="send:schedule"),
    )
    builder.row(
        InlineKeyboardButton(text="⬅️ Geri", callback_data="pb:back"),
    )

    return builder.as_markup()


def confirm_keyboard(confirm_data: str, cancel_data: str, lang: str = "az") -> InlineKeyboardMarkup:
    """Təsdiqləmə klaviaturası"""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="✅ Təsdiqlə", callback_data=confirm_data),
        InlineKeyboardButton(text="❌ Ləğv et", callback_data=cancel_data),
    )
    return builder.as_markup()


def back_keyboard(back_data: str, lang: str = "az") -> InlineKeyboardMarkup:
    """Geri düymə klaviaturası"""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="⬅️ Geri", callback_data=back_data),
    )
    return builder.as_markup()


def back_cancel_keyboard(back_data: str, lang: str = "az") -> InlineKeyboardMarkup:
    """Geri + Ləğv et klaviaturası"""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="⬅️ Geri", callback_data=back_data),
        InlineKeyboardButton(text="❌ Ləğv et", callback_data="main_menu"),
    )
    return builder.as_markup()


def preview_keyboard(post: PostData, lang: str = "az") -> InlineKeyboardMarkup:
    """Önizləmə klaviaturası"""
    builder = InlineKeyboardBuilder()

    builder.row(
        InlineKeyboardButton(text="✏️ Mətni redaktə et", callback_data="pb:text"),
        InlineKeyboardButton(text="🖼 Medianı dəyiş", callback_data="pb:media"),
    )
    builder.row(
        InlineKeyboardButton(text="🔘 Düymələri redaktə et", callback_data="pb:buttons"),
    )
    builder.row(
        InlineKeyboardButton(
            text="🔇 Link önizləməsini söndür" if not post.disable_preview else "🔊 Link önizləməsini aç",
            callback_data="pb:toggle_preview",
        ),
    )
    builder.row(
        InlineKeyboardButton(
            text="🔒 Məzmunu qoru" if not post.protect_content else "🔓 Qorumadan çıxar",
            callback_data="pb:toggle_protect",
        ),
    )
    builder.row(
        InlineKeyboardButton(text="📤 Göndər", callback_data="pb:send"),
        InlineKeyboardButton(text="💾 Saxla", callback_data="pb:save_draft"),
    )
    builder.row(
        InlineKeyboardButton(text="⬅️ Geri", callback_data="pb:back"),
    )

    return builder.as_markup()


def drafts_keyboard(drafts: list, page: int = 0, per_page: int = 8) -> InlineKeyboardMarkup:
    """Qaralamalar siyahısı klaviaturası"""
    from utils.helpers import truncate_text
    builder = InlineKeyboardBuilder()

    start = page * per_page
    end = start + per_page
    page_drafts = drafts[start:end]

    for draft in page_drafts:
        name = truncate_text(draft.name, 30)
        builder.row(
            InlineKeyboardButton(
                text=f"📄 {name}",
                callback_data=f"draft:load:{draft.id}",
            ),
            InlineKeyboardButton(
                text="🗑",
                callback_data=f"draft:delete:{draft.id}",
            ),
        )

    # Səhifələmə
    nav_buttons = []
    if page > 0:
        nav_buttons.append(
            InlineKeyboardButton(text="◀️ Əvvəl", callback_data=f"draft:page:{page-1}")
        )
    if end < len(drafts):
        nav_buttons.append(
            InlineKeyboardButton(text="Sonra ▶️", callback_data=f"draft:page:{page+1}")
        )
    if nav_buttons:
        builder.row(*nav_buttons)

    builder.row(
        InlineKeyboardButton(text="🏠 Ana Menyu", callback_data="main_menu"),
    )

    return builder.as_markup()


def templates_keyboard(lang: str = "az") -> InlineKeyboardMarkup:
    """Şablonlar klaviaturası"""
    builder = InlineKeyboardBuilder()

    templates = [
        ("📢 Kanal Postu", "tpl:channel"),
        ("📰 Xəbər Postu", "tpl:news"),
        ("📣 Elan", "tpl:announcement"),
        ("🎁 Giveaway", "tpl:giveaway"),
        ("📁 Fayl Paylaşımı", "tpl:file"),
        ("💰 Endirim", "tpl:discount"),
        ("📚 Dərs", "tpl:lesson"),
        ("🗂 Yönləndirici Menyu", "tpl:nav_menu"),
        ("❓ FAQ Menyusu", "tpl:faq"),
        ("🆘 Dəstək Menyusu", "tpl:support"),
        ("🌐 Sosial Şəbəkə", "tpl:social"),
        ("⭐ Premium Abunə", "tpl:premium"),
    ]

    for name, data in templates:
        builder.row(InlineKeyboardButton(text=name, callback_data=data))

    builder.row(
        InlineKeyboardButton(text="⭐ Öz şablonlarım", callback_data="tpl:my"),
    )
    builder.row(
        InlineKeyboardButton(text="⬅️ Geri", callback_data="main_menu"),
    )

    return builder.as_markup()


def json_mode_keyboard(lang: str = "az") -> InlineKeyboardMarkup:
    """JSON rejimi klaviaturası"""
    builder = InlineKeyboardBuilder()

    builder.row(
        InlineKeyboardButton(text="📤 JSON ixrac et", callback_data="json:export"),
        InlineKeyboardButton(text="📥 JSON idxal et", callback_data="json:import"),
    )
    builder.row(
        InlineKeyboardButton(text="✅ JSON yoxla", callback_data="json:validate"),
    )
    builder.row(
        InlineKeyboardButton(text="⬅️ Geri", callback_data="main_menu"),
    )

    return builder.as_markup()


def premium_menu_keyboard(lang: str = "az") -> InlineKeyboardMarkup:
    """Premium alətlər klaviaturası"""
    builder = InlineKeyboardBuilder()

    builder.row(
        InlineKeyboardButton(text="🔗 Deep Link", callback_data="premium:deeplink"),
        InlineKeyboardButton(text="📊 UTM Generator", callback_data="premium:utm"),
    )
    builder.row(
        InlineKeyboardButton(text="📱 QR Kod", callback_data="premium:qr"),
        InlineKeyboardButton(text="🔄 MD↔HTML", callback_data="premium:convert"),
    )
    builder.row(
        InlineKeyboardButton(text="📏 Limit Yoxla", callback_data="premium:limits"),
        InlineKeyboardButton(text="📜 Tarixçə", callback_data="premium:history"),
    )
    builder.row(
        InlineKeyboardButton(text="⬅️ Geri", callback_data="main_menu"),
    )

    return builder.as_markup()


def admin_keyboard(lang: str = "az") -> InlineKeyboardMarkup:
    """Admin panel klaviaturası"""
    builder = InlineKeyboardBuilder()

    builder.row(
        InlineKeyboardButton(text="📊 Statistika", callback_data="admin:stats"),
        InlineKeyboardButton(text="📢 Broadcast", callback_data="admin:broadcast"),
    )
    builder.row(
        InlineKeyboardButton(text="🚫 İstifadəçi blokla", callback_data="admin:block"),
        InlineKeyboardButton(text="✅ İstifadəçi açma", callback_data="admin:unblock"),
    )
    builder.row(
        InlineKeyboardButton(text="🔧 Texniki xidmət", callback_data="admin:maintenance"),
        InlineKeyboardButton(text="📋 Loglar", callback_data="admin:logs"),
    )
    builder.row(
        InlineKeyboardButton(text="🏠 Ana Menyu", callback_data="main_menu"),
    )

    return builder.as_markup()


def build_post_inline_keyboard(post: PostData) -> Optional[InlineKeyboardMarkup]:
    """Postun inline klaviaturasını qur"""
    keyboard = post.get_inline_keyboard()
    if not keyboard:
        return None

    builder = InlineKeyboardBuilder()
    for row in keyboard:
        row_buttons = []
        for btn_data in row:
            try:
                if "url" in btn_data:
                    row_buttons.append(InlineKeyboardButton(
                        text=btn_data["text"], url=btn_data["url"]
                    ))
                elif "callback_data" in btn_data:
                    row_buttons.append(InlineKeyboardButton(
                        text=btn_data["text"], callback_data=btn_data["callback_data"]
                    ))
                elif "web_app" in btn_data:
                    from aiogram.types import WebAppInfo
                    row_buttons.append(InlineKeyboardButton(
                        text=btn_data["text"],
                        web_app=WebAppInfo(url=btn_data["web_app"]["url"])
                    ))
                elif "switch_inline_query" in btn_data:
                    row_buttons.append(InlineKeyboardButton(
                        text=btn_data["text"],
                        switch_inline_query=btn_data["switch_inline_query"]
                    ))
                elif "switch_inline_query_current_chat" in btn_data:
                    row_buttons.append(InlineKeyboardButton(
                        text=btn_data["text"],
                        switch_inline_query_current_chat=btn_data["switch_inline_query_current_chat"]
                    ))
                elif "copy_text" in btn_data:
                    from aiogram.types import CopyTextButton
                    row_buttons.append(InlineKeyboardButton(
                        text=btn_data["text"],
                        copy_text=CopyTextButton(text=btn_data["copy_text"]["text"])
                    ))
                elif "login_url" in btn_data:
                    from aiogram.types import LoginUrl
                    row_buttons.append(InlineKeyboardButton(
                        text=btn_data["text"],
                        login_url=LoginUrl(url=btn_data["login_url"]["url"])
                    ))
            except Exception:
                # Xəta olarsa düymənin üzərindən keç
                continue

        if row_buttons:
            builder.row(*row_buttons)

    markup = builder.as_markup()
    return markup if markup.inline_keyboard else None


def options_keyboard(post: PostData, lang: str = "az") -> InlineKeyboardMarkup:
    """Post seçimləri klaviaturası"""
    builder = InlineKeyboardBuilder()

    preview_icon = "🔇" if post.disable_preview else "🔊"
    preview_text = "Link önizləməsini söndür" if not post.disable_preview else "Link önizləməsini aç"
    protect_icon = "🔒" if not post.protect_content else "🔓"
    protect_text = "Məzmunu qoru" if not post.protect_content else "Qorumadan çıxar"

    builder.row(
        InlineKeyboardButton(
            text=f"{preview_icon} {preview_text}",
            callback_data="opt:toggle_preview",
        )
    )
    builder.row(
        InlineKeyboardButton(
            text=f"{protect_icon} {protect_text}",
            callback_data="opt:toggle_protect",
        )
    )
    builder.row(
        InlineKeyboardButton(text="⬅️ Geri", callback_data="pb:back"),
    )

    return builder.as_markup()
