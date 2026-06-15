"""
Lokalizasiya - Azərbaycan, Rus, İngilis dil dəstəyi
"""

from typing import Dict, Any

STRINGS: Dict[str, Dict[str, str]] = {
    "az": {
        # ─── Ümumi ──────────────────────────────────────────────
        "welcome": (
            "👋 <b>PostBuilder Pro</b>-ya xoş gəldiniz!\n\n"
            "🔥 <b>Versiya {version}</b>\n\n"
            "Bu bot ilə siz:\n"
            "✅ Peşəkar postlar yarada bilərsiniz\n"
            "✅ Müxtəlif növ düymələr əlavə edə bilərsiniz\n"
            "✅ İstənilən kanala/qrupa göndərə bilərsiniz\n"
            "✅ Hazır şablonlardan istifadə edə bilərsiniz\n\n"
            "Başlamaq üçün aşağıdakı menyudan istifadə edin 👇"
        ),
        "main_menu": "🏠 <b>Ana Menyu</b>",
        "back": "⬅️ Geri",
        "cancel": "❌ Ləğv et",
        "done": "✅ Hazır",
        "save": "💾 Saxla",
        "delete": "🗑 Sil",
        "edit": "✏️ Redaktə et",
        "confirm": "✅ Təsdiqlə",
        "yes": "✅ Bəli",
        "no": "❌ Xeyr",
        "error": "❌ Xəta baş verdi. Yenidən cəhd edin.",
        "success": "✅ Uğurla tamamlandı!",
        "loading": "⏳ Yüklənir...",
        "not_found": "❌ Tapılmadı.",
        "blocked": "🚫 Siz bloklanmısınız.",
        "maintenance": "🔧 Bot texniki xidmətdədir. Zəhmət olmasa gözləyin.",

        # ─── Düymə adları ────────────────────────────────────────
        "btn_new_post": "📝 Yeni Post",
        "btn_my_drafts": "📁 Qaralamalarım",
        "btn_templates": "📋 Şablonlar",
        "btn_json_mode": "🔧 JSON Rejimi",
        "btn_premium": "⭐ Premium Alətlər",
        "btn_help": "❓ Kömək",
        "btn_settings": "⚙️ Parametrlər",

        # ─── Post qurucusu ────────────────────────────────────────
        "post_builder_menu": (
            "📝 <b>Post Qurucusu</b>\n\n"
            "Aşağıdakı seçimlərdən istifadə edərək postunuzu qurun:"
        ),
        "btn_add_text": "✏️ Mətn əlavə et",
        "btn_add_media": "🖼 Media əlavə et",
        "btn_add_buttons": "🔘 Düymələr əlavə et",
        "btn_preview": "👁 Önizləmə",
        "btn_send_post": "📤 Göndər",
        "btn_save_draft": "💾 Qaralama saxla",
        "btn_clear": "🗑 Təmizlə",
        "btn_format": "🎨 Format",

        "waiting_text": (
            "✏️ <b>Mətn daxil edin:</b>\n\n"
            "<b>Dəstəklənən formatlar:</b>\n"
            "• <code>&lt;b&gt;Qalın&lt;/b&gt;</code>\n"
            "• <code>&lt;i&gt;Kursiv&lt;/i&gt;</code>\n"
            "• <code>&lt;u&gt;Altıxətt&lt;/u&gt;</code>\n"
            "• <code>&lt;s&gt;Üstüxətt&lt;/s&gt;</code>\n"
            "• <code>&lt;tg-spoiler&gt;Spoiler&lt;/tg-spoiler&gt;</code>\n"
            "• <code>&lt;code&gt;Kod&lt;/code&gt;</code>\n"
            "• <code>&lt;pre&gt;Blok kod&lt;/pre&gt;</code>\n"
            "• <code>&lt;blockquote&gt;Sitat&lt;/blockquote&gt;</code>\n"
            "• <code>&lt;a href='URL'&gt;Keçid&lt;/a&gt;</code>"
        ),
        "text_added": "✅ Mətn əlavə edildi!",
        "text_too_long": "❌ Mətn çox uzundur. Maksimum {max} simvol.",

        # ─── Formatlaşdırma düymələri ─────────────────────────────
        "btn_bold": "𝐁 Qalın",
        "btn_italic": "𝐼 Kursiv",
        "btn_underline": "U̲ Altıxətt",
        "btn_strikethrough": "S̶ Üstüxətt",
        "btn_spoiler": "👁 Spoiler",
        "btn_code": "</> Kod",
        "btn_pre": "📦 Blok kod",
        "btn_quote": "💬 Sitat",
        "btn_link": "🔗 Keçid",
        "btn_mono": "🔤 Mono",

        # ─── Media ───────────────────────────────────────────────
        "media_menu": (
            "🖼 <b>Media seçin:</b>\n\n"
            "Göndərmək istədiyiniz media növünü seçin:"
        ),
        "btn_photo": "🖼 Şəkil",
        "btn_video": "🎥 Video",
        "btn_audio": "🎵 Audio",
        "btn_voice": "🎤 Səs mesajı",
        "btn_gif": "🎬 GIF/Animasiya",
        "btn_document": "📄 Sənəd",
        "btn_media_group": "📸 Albom (çox media)",
        "btn_no_media": "⭕ Mediasız",

        "waiting_photo": "🖼 Şəkil göndərin:",
        "waiting_video": "🎥 Video göndərin:",
        "waiting_audio": "🎵 Audio faylı göndərin:",
        "waiting_voice": "🎤 Səs mesajı göndərin:",
        "waiting_gif": "🎬 GIF/Animasiya göndərin:",
        "waiting_document": "📄 Sənəd göndərin:",
        "waiting_caption": "📝 Caption daxil edin (və ya keçin):",
        "btn_skip_caption": "⏭ Caption olmadan",
        "media_added": "✅ Media əlavə edildi!",
        "waiting_media_group": "📸 Mediyaları göndərin (2-10 arası). Bitirdikdən sonra /done yazın:",
        "media_group_added": "✅ {count} media əlavə edildi!",

        # ─── Düymələr ────────────────────────────────────────────
        "button_menu": (
            "🔘 <b>Düymə Menyusu</b>\n\n"
            "Cari düymələr: {button_count}\n\n"
            "Əməliyyat seçin:"
        ),
        "btn_add_button": "➕ Düymə əlavə et",
        "btn_view_buttons": "👁 Düymələrə bax",
        "btn_edit_button": "✏️ Düymə redaktə et",
        "btn_delete_button": "🗑 Düymə sil",
        "btn_clear_buttons": "🗑 Hamısını sil",
        "btn_new_row": "↵ Yeni sətir",

        "choose_button_type": (
            "🔘 <b>Düymə növünü seçin:</b>\n\n"
            "Hər növün funksionallığı fərqlidir:"
        ),
        "btn_type_url": "🔗 URL Düymə",
        "btn_type_callback": "📡 Callback Düymə",
        "btn_type_webapp": "🌐 Web App Düymə",
        "btn_type_share": "📤 Paylaş Düymə",
        "btn_type_switch_inline": "🔄 Switch Inline",
        "btn_type_switch_current": "💬 Switch Current Chat",
        "btn_type_copy": "📋 Mətn kopyala",
        "btn_type_login": "🔑 Login URL",
        "btn_type_game": "🎮 Oyun",
        "btn_type_pay": "💳 Ödəniş",

        "waiting_url_button_text": "✏️ Düymə mətni daxil edin:",
        "waiting_url_button_url": "🔗 URL daxil edin (https:// ilə başlamalıdır):",
        "waiting_callback_text": "✏️ Düymə mətni daxil edin:",
        "waiting_callback_data": "📡 Callback data daxil edin (1-64 simvol):",
        "waiting_webapp_text": "✏️ Düymə mətni daxil edin:",
        "waiting_webapp_url": "🌐 Web App URL daxil edin (https:// ilə başlamalıdır):",
        "waiting_copy_text": "✏️ Düymə mətni daxil edin:",
        "waiting_copy_value": "📋 Kopyalanacaq mətn daxil edin:",
        "waiting_switch_text": "✏️ Düymə mətni daxil edin:",
        "waiting_switch_query": "🔄 Inline sorğu daxil edin (boş ola bilər):",
        "waiting_login_text": "✏️ Düymə mətni daxil edin:",
        "waiting_login_url": "🔑 Login URL daxil edin:",

        "button_added": "✅ Düymə əlavə edildi!",
        "button_deleted": "✅ Düymə silindi!",
        "buttons_cleared": "✅ Bütün düymələr silindi!",
        "no_buttons": "ℹ️ Hələ düymə yoxdur.",
        "invalid_url": "❌ Düzgün URL deyil. https:// ilə başlamalıdır.",
        "callback_too_long": "❌ Callback data çox uzundur. Maksimum 64 simvol.",
        "max_buttons_per_row": "❌ Bir sətirdə maksimum {max} düymə ola bilər.",
        "max_button_rows": "❌ Maksimum {max} sətir ola bilər.",

        # ─── Düymə stilləri ───────────────────────────────────────
        "choose_button_style": "🎨 Düymə stilini seçin:",
        "btn_style_default": "⬜ Standart",
        "btn_style_primary": "🔵 Əsas (Mavi)",
        "btn_style_success": "🟢 Uğur (Yaşıl)",
        "btn_style_danger": "🔴 Təhlükə (Qırmızı)",

        # ─── Göndərmə ─────────────────────────────────────────────
        "send_menu": (
            "📤 <b>Göndərmə Menyusu</b>\n\n"
            "Postunuzu hara göndərməк istərsiniz?"
        ),
        "btn_send_to_chat": "💬 Çata göndər",
        "btn_send_to_channel": "📢 Kanala göndər",
        "btn_send_to_group": "👥 Qrupa göndər",
        "btn_send_multiple": "📡 Çox hədəfə göndər",
        "btn_schedule": "⏰ Planlaşdır",
        "btn_send_me": "👤 Özümə göndər",

        "waiting_chat_id": (
            "💬 <b>Chat ID və ya username daxil edin:</b>\n\n"
            "Nümunələr:\n"
            "• <code>@kanal_adı</code>\n"
            "• <code>-1001234567890</code>\n"
            "• <code>1234567890</code>"
        ),
        "waiting_multiple_targets": (
            "📡 <b>Bir neçə hədəf daxil edin:</b>\n\n"
            "Hər birini ayrı sətirdə yazın:\n"
            "<code>@kanal1\n@kanal2\n-1001234567890</code>"
        ),
        "sending": "📤 Göndərilir...",
        "sent_success": "✅ Post uğurla göndərildi!\n📊 {success}/{total} hədəfə çatdı.",
        "sent_partial": "⚠️ Qismən göndərildi: {success}/{total} uğurlu, {failed} uğursuz.",
        "send_failed": "❌ Göndərmə uğursuz oldu: {error}",
        "confirm_send": (
            "✅ <b>Göndərməyi təsdiqləyin</b>\n\n"
            "Hədəf: <code>{target}</code>\n"
            "Düymə sayı: {button_count}\n"
            "Media: {has_media}"
        ),

        # ─── Planlaşdırma ─────────────────────────────────────────
        "waiting_schedule_date": "📅 Tarixi daxil edin (DD.MM.YYYY formatında):",
        "waiting_schedule_time": "⏰ Vaxtı daxil edin (HH:MM formatında):",
        "schedule_saved": "⏰ Post planlaşdırıldı: {datetime}",
        "invalid_date": "❌ Düzgün tarix formatı deyil. DD.MM.YYYY şəklində daxil edin.",
        "invalid_time": "❌ Düzgün vaxt formatı deyil. HH:MM şəklində daxil edin.",
        "past_date": "❌ Keçmiş tarix seçilə bilməz.",

        # ─── Qaralamalar ──────────────────────────────────────────
        "my_drafts": "📁 <b>Qaralamalarım</b>\n\nCəmi: {count} qaralama",
        "no_drafts": "📁 Hələ heç bir qaralama yoxdur.",
        "waiting_draft_name": "💾 Qaralama adını daxil edin:",
        "draft_saved": "✅ '<b>{name}</b>' adlı qaralama saxlandı!",
        "draft_deleted": "✅ Qaralama silindi!",
        "confirm_delete_draft": "❓ Bu qaralamani silmək istədiyinizə əminsinizmi?",
        "max_drafts": "❌ Maksimum {max} qaralama saxlaya bilərsiniz.",

        # ─── Şablonlar ────────────────────────────────────────────
        "templates_menu": "📋 <b>Şablonlar</b>\n\nHazır şablonlardan seçin:",
        "my_templates": "📋 <b>Öz Şablonlarım</b>",
        "no_templates": "📋 Hələ öz şablonunuz yoxdur.",
        "btn_builtin_templates": "📦 Hazır şablonlar",
        "btn_my_templates": "⭐ Öz şablonlarım",
        "template_applied": "✅ Şablon tətbiq edildi!",

        # ─── JSON rejimi ──────────────────────────────────────────
        "json_menu": (
            "🔧 <b>JSON Rejimi</b>\n\n"
            "Bu rejimdə inline keyboard JSON-unu idxal/ixrac edə bilərsiniz."
        ),
        "btn_export_json": "📤 JSON ixrac et",
        "btn_import_json": "📥 JSON idxal et",
        "btn_validate_json": "✅ JSON yoxla",
        "waiting_json_import": "📥 JSON mətnini göndərin:",
        "json_valid": "✅ JSON etibarlıdır!\n\nDüymə sayı: {count}",
        "json_invalid": "❌ JSON etibarsızdır:\n<code>{error}</code>",
        "json_imported": "✅ JSON idxal edildi! {count} düymə əlavə edildi.",

        # ─── Premium alətlər ──────────────────────────────────────
        "premium_menu": "⭐ <b>Premium Alətlər</b>\n\nGüclü əlavə funksiyalar:",
        "btn_deep_link": "🔗 Deep Link Generatoru",
        "btn_utm": "📊 UTM Generator",
        "btn_qr_code": "📱 QR Kod",
        "btn_md_html": "🔄 Markdown ↔ HTML",
        "btn_post_history": "📜 Post Tarixçəsi",
        "btn_check_limits": "📏 Limit Yoxlayıcı",

        "waiting_deep_link_bot": "🤖 Bot username daxil edin (@username):",
        "waiting_deep_link_param": "🔗 Parametr daxil edin (boş ola bilər):",
        "deep_link_result": (
            "🔗 <b>Deep Link:</b>\n\n"
            "<code>{link}</code>\n\n"
            "📱 <b>Start link:</b>\n"
            "<code>{start_link}</code>"
        ),

        "waiting_utm_url": "🌐 Əsas URL daxil edin:",
        "waiting_utm_source": "📊 UTM Source daxil edin (məs: telegram):",
        "waiting_utm_medium": "📊 UTM Medium daxil edin (məs: post):",
        "waiting_utm_campaign": "📊 UTM Campaign daxil edin:",
        "utm_result": "🔗 <b>UTM Link:</b>\n\n<code>{url}</code>",

        "waiting_qr_text": "📱 QR kod üçün mətn/URL daxil edin:",
        "qr_generating": "⏳ QR kod yaradılır...",
        "qr_generated": "✅ QR kod hazırdır!",

        "waiting_convert": "🔄 Çevirmək istədiyiniz mətni daxil edin:",
        "btn_md_to_html": "📄 Markdown → HTML",
        "btn_html_to_md": "📄 HTML → Markdown",
        "convert_result": "✅ <b>Nəticə:</b>\n\n<code>{result}</code>",

        # ─── Admin ────────────────────────────────────────────────
        "admin_menu": "⚙️ <b>Admin Paneli</b>",
        "btn_stats": "📊 Statistika",
        "btn_broadcast": "📢 Broadcast",
        "btn_block_user": "🚫 İstifadəçi blokla",
        "btn_unblock_user": "✅ İstifadəçi açma",
        "btn_maintenance": "🔧 Texniki xidmət",
        "btn_view_logs": "📋 Loglar",

        "stats_text": (
            "📊 <b>Bot Statistikası</b>\n\n"
            "👥 Cəmi istifadəçi: <b>{total_users}</b>\n"
            "✅ Aktiv istifadəçi: <b>{active_users}</b>\n"
            "📁 Cəmi qaralama: <b>{total_drafts}</b>\n"
            "📋 Cəmi şablon: <b>{total_templates}</b>"
        ),

        "waiting_broadcast": "📢 Broadcast mesajını daxil edin (HTML dəstəkləyir):",
        "confirm_broadcast": (
            "📢 <b>Broadcast Təsdiqləmə</b>\n\n"
            "Mesaj: {message}\n\n"
            "Göndəriləcək istifadəçi sayı: <b>{count}</b>\n\n"
            "Davam etmək istəyirsinizmi?"
        ),
        "broadcast_started": "📢 Broadcast başladıldı...",
        "broadcast_done": (
            "✅ <b>Broadcast tamamlandı!</b>\n\n"
            "✅ Uğurlu: {success}\n"
            "❌ Uğursuz: {failed}\n"
            "⏱ Vaxt: {time}s"
        ),

        "waiting_user_id_block": "🚫 Bloklanacaq istifadəçi ID-sini daxil edin:",
        "waiting_user_id_unblock": "✅ Blokdan çıxarılacaq istifadəçi ID-sini daxil edin:",
        "user_blocked": "✅ İstifadəçi {user_id} bloklandı.",
        "user_unblocked": "✅ İstifadəçi {user_id} blokdan çıxarıldı.",
        "maintenance_on": "🔧 Texniki xidmət rejimi <b>aktivləşdirildi</b>.",
        "maintenance_off": "✅ Texniki xidmət rejimi <b>söndürüldü</b>.",
        "not_admin": "❌ Bu əməliyyat yalnız adminlər üçündür.",

        # ─── Kömək ───────────────────────────────────────────────
        "help_text": (
            "❓ <b>Kömək Menyusu</b>\n\n"
            "📝 <b>Post Qurucusu:</b>\n"
            "• Mətn yazın, formatlaşdırın\n"
            "• Media əlavə edin\n"
            "• Düymələr əlavə edin\n"
            "• Önizləmə görün\n"
            "• İstənilən yərə göndərin\n\n"
            "🔘 <b>Düymə Növləri:</b>\n"
            "• URL - vebsayta keçid\n"
            "• Callback - bot reaksiyası\n"
            "• Web App - mini proqram\n"
            "• Share - paylaşım\n"
            "• Switch Inline - inline sorğu\n"
            "• Copy - mətn kopyala\n\n"
            "📋 <b>Şablonlar:</b>\n"
            "Hazır şablonlardan istifadə edin\n\n"
            "⭐ <b>Premium Alətlər:</b>\n"
            "Deep Link, UTM, QR Kod və s."
        ),

        # ─── Önizləmə ─────────────────────────────────────────────
        "preview_header": "👁 <b>Önizləmə</b>",
        "no_content": "⚠️ Post boşdur. Mətn və ya media əlavə edin.",
        "btn_edit_text": "✏️ Mətni redaktə et",
        "btn_edit_media": "🖼 Medianı dəyiş",
        "btn_edit_buttons": "🔘 Düymələri redaktə et",
        "btn_options": "⚙️ Parametrlər",
        "btn_disable_preview": "🔇 Link önizləməsini söndür",
        "btn_enable_preview": "🔊 Link önizləməsini aç",
        "btn_protect_content": "🔒 Kopyalamadan qoru",
        "btn_unprotect_content": "🔓 Kopyalama qorumasını çıxar",
    },

    "ru": {
        "welcome": (
            "👋 Добро пожаловать в <b>PostBuilder Pro</b>!\n\n"
            "🔥 <b>Версия {version}</b>\n\n"
            "С этим ботом вы можете:\n"
            "✅ Создавать профессиональные посты\n"
            "✅ Добавлять различные кнопки\n"
            "✅ Отправлять в любой канал/группу\n"
            "✅ Использовать готовые шаблоны\n\n"
            "Используйте меню ниже 👇"
        ),
        "main_menu": "🏠 <b>Главное меню</b>",
        "back": "⬅️ Назад",
        "cancel": "❌ Отмена",
        "done": "✅ Готово",
        "save": "💾 Сохранить",
        "delete": "🗑 Удалить",
        "edit": "✏️ Редактировать",
        "confirm": "✅ Подтвердить",
        "yes": "✅ Да",
        "no": "❌ Нет",
        "error": "❌ Произошла ошибка. Попробуйте снова.",
        "success": "✅ Успешно завершено!",
        "loading": "⏳ Загрузка...",
        "not_found": "❌ Не найдено.",
        "blocked": "🚫 Вы заблокированы.",
        "maintenance": "🔧 Бот на техническом обслуживании. Пожалуйста, подождите.",
        "btn_new_post": "📝 Новый пост",
        "btn_my_drafts": "📁 Мои черновики",
        "btn_templates": "📋 Шаблоны",
        "btn_json_mode": "🔧 Режим JSON",
        "btn_premium": "⭐ Premium инструменты",
        "btn_help": "❓ Помощь",
        "btn_settings": "⚙️ Настройки",
        "not_admin": "❌ Эта операция только для администраторов.",
    },

    "en": {
        "welcome": (
            "👋 Welcome to <b>PostBuilder Pro</b>!\n\n"
            "🔥 <b>Version {version}</b>\n\n"
            "With this bot you can:\n"
            "✅ Create professional posts\n"
            "✅ Add various button types\n"
            "✅ Send to any channel/group\n"
            "✅ Use ready-made templates\n\n"
            "Use the menu below 👇"
        ),
        "main_menu": "🏠 <b>Main Menu</b>",
        "back": "⬅️ Back",
        "cancel": "❌ Cancel",
        "done": "✅ Done",
        "save": "💾 Save",
        "delete": "🗑 Delete",
        "edit": "✏️ Edit",
        "confirm": "✅ Confirm",
        "yes": "✅ Yes",
        "no": "❌ No",
        "error": "❌ An error occurred. Please try again.",
        "success": "✅ Successfully completed!",
        "loading": "⏳ Loading...",
        "not_found": "❌ Not found.",
        "blocked": "🚫 You are blocked.",
        "maintenance": "🔧 Bot is under maintenance. Please wait.",
        "btn_new_post": "📝 New Post",
        "btn_my_drafts": "📁 My Drafts",
        "btn_templates": "📋 Templates",
        "btn_json_mode": "🔧 JSON Mode",
        "btn_premium": "⭐ Premium Tools",
        "btn_help": "❓ Help",
        "btn_settings": "⚙️ Settings",
        "not_admin": "❌ This operation is for admins only.",
    },
}


def t(key: str, lang: str = "az", **kwargs) -> str:
    """Lokalizasiya mətnini gətir"""
    strings = STRINGS.get(lang, STRINGS["az"])
    text = strings.get(key, STRINGS["az"].get(key, f"[{key}]"))
    if kwargs:
        try:
            text = text.format(**kwargs)
        except (KeyError, ValueError):
            pass
    return text


def get_user_lang(language_code: str) -> str:
    """Telegram dil kodunu dəstəklənən dilə çevir"""
    if language_code and language_code.startswith("az"):
        return "az"
    elif language_code and language_code.startswith("ru"):
        return "ru"
    elif language_code and language_code.startswith("en"):
        return "en"
    return "az"
