"""
Köməkçi funksiyalar - URL yoxlama, format çevirmə və s.
"""

import re
import json
import html
import hashlib
from typing import Optional, Tuple, List
from datetime import datetime
from urllib.parse import urlparse, urlencode, urlunparse, parse_qs, urljoin


def is_valid_url(url: str) -> bool:
    """URL etibarlılığını yoxla"""
    try:
        result = urlparse(url)
        return all([result.scheme in ("http", "https"), result.netloc])
    except Exception:
        return False


def is_valid_https_url(url: str) -> bool:
    """HTTPS URL yoxla (Web App üçün)"""
    try:
        result = urlparse(url)
        return result.scheme == "https" and bool(result.netloc)
    except Exception:
        return False


def is_valid_telegram_url(url: str) -> bool:
    """Telegram URL-ini yoxla (t.me və s.)"""
    valid_schemes = {"http", "https", "tg"}
    try:
        result = urlparse(url)
        return result.scheme in valid_schemes and bool(result.netloc)
    except Exception:
        return False


def sanitize_html(text: str) -> str:
    """HTML mətni təhlükəsizləşdir (izin verilən teqləri saxla)"""
    ALLOWED_TAGS = {
        "b", "strong", "i", "em", "u", "s", "strike", "del",
        "tg-spoiler", "code", "pre", "a", "blockquote",
    }

    # Sadə yanaşma: yalnız izin verilən teqləri saxla
    def replace_tag(match):
        tag = match.group(1).lower().split()[0].lstrip("/")
        full_match = match.group(0)
        if tag in ALLOWED_TAGS:
            return full_match
        return html.escape(full_match)

    result = re.sub(r"<[^>]+>", replace_tag, text)
    return result


def markdown_to_html(text: str) -> str:
    """Markdown-ı HTML-ə çevir"""
    # Qalın
    text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text, flags=re.DOTALL)
    text = re.sub(r"__(.+?)__", r"<b>\1</b>", text, flags=re.DOTALL)
    # Kursiv
    text = re.sub(r"\*(.+?)\*", r"<i>\1</i>", text, flags=re.DOTALL)
    text = re.sub(r"_(.+?)_", r"<i>\1</i>", text, flags=re.DOTALL)
    # Üstüxətt
    text = re.sub(r"~~(.+?)~~", r"<s>\1</s>", text, flags=re.DOTALL)
    # Kod bloku
    text = re.sub(r"```(.+?)```", r"<pre>\1</pre>", text, flags=re.DOTALL)
    # Sətir kodu
    text = re.sub(r"`(.+?)`", r"<code>\1</code>", text)
    # Keçidlər
    text = re.sub(r"\[(.+?)\]\((.+?)\)", r'<a href="\2">\1</a>', text)
    return text


def html_to_markdown(text: str) -> str:
    """HTML-i Markdown-a çevir"""
    # Qalın
    text = re.sub(r"<b>(.+?)</b>", r"**\1**", text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r"<strong>(.+?)</strong>", r"**\1**", text, flags=re.DOTALL | re.IGNORECASE)
    # Kursiv
    text = re.sub(r"<i>(.+?)</i>", r"*\1*", text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r"<em>(.+?)</em>", r"*\1*", text, flags=re.DOTALL | re.IGNORECASE)
    # Altıxətt (Markdown-da yoxdur, saxla)
    text = re.sub(r"<u>(.+?)</u>", r"\1", text, flags=re.DOTALL | re.IGNORECASE)
    # Üstüxətt
    text = re.sub(r"<s>(.+?)</s>", r"~~\1~~", text, flags=re.DOTALL | re.IGNORECASE)
    # Pre
    text = re.sub(r"<pre>(.+?)</pre>", r"```\1```", text, flags=re.DOTALL | re.IGNORECASE)
    # Kod
    text = re.sub(r"<code>(.+?)</code>", r"`\1`", text, flags=re.DOTALL | re.IGNORECASE)
    # Keçidlər
    text = re.sub(r'<a href="(.+?)">(.+?)</a>', r"[\2](\1)", text, flags=re.DOTALL | re.IGNORECASE)
    # Qalan teqləri sil
    text = re.sub(r"<[^>]+>", "", text)
    return text


def generate_deep_link(bot_username: str, parameter: str = "") -> Tuple[str, str]:
    """Deep link yarat"""
    username = bot_username.lstrip("@")
    base_url = f"https://t.me/{username}"

    if parameter:
        start_link = f"{base_url}?start={parameter}"
        startgroup_link = f"{base_url}?startgroup={parameter}"
    else:
        start_link = base_url
        startgroup_link = f"{base_url}?startgroup"

    return start_link, startgroup_link


def generate_utm_url(
    url: str,
    source: str,
    medium: str,
    campaign: str,
    term: str = "",
    content: str = "",
) -> str:
    """UTM parametrli URL yarat"""
    params = {
        "utm_source": source,
        "utm_medium": medium,
        "utm_campaign": campaign,
    }
    if term:
        params["utm_term"] = term
    if content:
        params["utm_content"] = content

    parsed = urlparse(url)
    existing = parse_qs(parsed.query)
    existing.update({k: [v] for k, v in params.items()})

    query_string = "&".join(
        f"{k}={v[0]}" for k, v in existing.items()
    )

    new_parsed = parsed._replace(query=query_string)
    return urlunparse(new_parsed)


def parse_date_time(date_str: str, time_str: str) -> Optional[datetime]:
    """Tarix və vaxt mətnlərini datetime-a çevir"""
    try:
        dt = datetime.strptime(f"{date_str} {time_str}", "%d.%m.%Y %H:%M")
        if dt <= datetime.utcnow():
            return None
        return dt
    except ValueError:
        return None


def estimate_message_size(text: str) -> dict:
    """Mesajın ölçüsünü qiymətləndir"""
    char_count = len(text) if text else 0
    byte_size = len(text.encode("utf-8")) if text else 0

    return {
        "characters": char_count,
        "bytes": byte_size,
        "max_text": 4096,
        "max_caption": 1024,
        "text_remaining": max(0, 4096 - char_count),
        "caption_remaining": max(0, 1024 - char_count),
        "within_text_limit": char_count <= 4096,
        "within_caption_limit": char_count <= 1024,
    }


def validate_json_keyboard(json_str: str) -> Tuple[bool, str, int]:
    """JSON keyboard-u yoxla
    Returns: (is_valid, error_message, button_count)
    """
    try:
        data = json.loads(json_str)

        if isinstance(data, dict):
            keyboard = data.get("inline_keyboard", [])
        elif isinstance(data, list):
            keyboard = data
        else:
            return False, "JSON siyahı və ya obyekt olmalıdır", 0

        if not isinstance(keyboard, list):
            return False, "inline_keyboard siyahı olmalıdır", 0

        button_count = 0
        for row_idx, row in enumerate(keyboard):
            if not isinstance(row, list):
                return False, f"Sətir {row_idx + 1} siyahı deyil", 0

            for col_idx, btn in enumerate(row):
                if not isinstance(btn, dict):
                    return False, f"Düymə [{row_idx}][{col_idx}] obyekt deyil", 0

                if "text" not in btn:
                    return False, f"Düymə [{row_idx}][{col_idx}]-də 'text' sahəsi yoxdur", 0

                valid_fields = {
                    "url", "callback_data", "web_app", "switch_inline_query",
                    "switch_inline_query_current_chat", "copy_text",
                    "login_url", "callback_game", "pay",
                }

                has_action = any(f in btn for f in valid_fields)
                if not has_action:
                    return False, f"Düymə [{row_idx}][{col_idx}]-də hərəkət sahəsi yoxdur", 0

                button_count += 1

        return True, "", button_count

    except json.JSONDecodeError as e:
        return False, f"JSON sintaksis xətası: {e}", 0
    except Exception as e:
        return False, str(e), 0


def format_file_size(size_bytes: int) -> str:
    """Fayl ölçüsünü formatla"""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.1f} MB"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"


def truncate_text(text: str, max_length: int = 50, suffix: str = "...") -> str:
    """Mətni kəs"""
    if len(text) <= max_length:
        return text
    return text[: max_length - len(suffix)] + suffix


def escape_html(text: str) -> str:
    """HTML simvollarından qaç"""
    return (
        text
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def get_media_type_emoji(media_type: str) -> str:
    """Media növü üçün emoji"""
    emojis = {
        "photo": "🖼",
        "video": "🎥",
        "audio": "🎵",
        "voice": "🎤",
        "animation": "🎬",
        "document": "📄",
        "group": "📸",
    }
    return emojis.get(media_type, "📎")


def get_button_type_emoji(button_type: str) -> str:
    """Düymə növü üçün emoji"""
    emojis = {
        "url": "🔗",
        "callback": "📡",
        "webapp": "🌐",
        "share": "📤",
        "switch_inline": "🔄",
        "switch_current": "💬",
        "copy": "📋",
        "login": "🔑",
        "game": "🎮",
        "pay": "💳",
    }
    return emojis.get(button_type, "🔘")


def split_long_text(text: str, max_length: int = 4096) -> List[str]:
    """Uzun mətni hissələrə böl"""
    if len(text) <= max_length:
        return [text]

    parts = []
    while text:
        if len(text) <= max_length:
            parts.append(text)
            break

        # Ən yaxın sözün sonunda böl
        cut_at = text.rfind(" ", 0, max_length)
        if cut_at == -1:
            cut_at = max_length

        parts.append(text[:cut_at])
        text = text[cut_at:].lstrip()

    return parts
