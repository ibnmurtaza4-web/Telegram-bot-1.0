"""
Post məlumat modeli - İstifadəçinin cari post vəziyyəti
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
import json


@dataclass
class ButtonData:
    """Bir düymənin məlumatları"""
    text: str
    button_type: str  # url, callback, webapp, share, switch_inline, switch_current, copy, login, game, pay
    value: str = ""  # URL, callback data, webapp URL, switch query, copy text, login URL
    row: int = 0
    col: int = 0
    style: str = "default"  # default, primary, success, danger

    def to_inline_button(self) -> dict:
        """aiogram InlineKeyboardButton parametrlərinə çevir"""
        base = {"text": self.text}

        if self.button_type == "url":
            base["url"] = self.value
        elif self.button_type == "callback":
            base["callback_data"] = self.value
        elif self.button_type == "webapp":
            base["web_app"] = {"url": self.value}
        elif self.button_type == "switch_inline":
            base["switch_inline_query"] = self.value
        elif self.button_type == "switch_current":
            base["switch_inline_query_current_chat"] = self.value
        elif self.button_type == "copy":
            base["copy_text"] = {"text": self.value}
        elif self.button_type == "login":
            base["login_url"] = {"url": self.value}
        elif self.button_type == "game":
            base["callback_game"] = {}
        elif self.button_type == "pay":
            base["pay"] = True

        return base

    def to_dict(self) -> dict:
        return {
            "text": self.text,
            "button_type": self.button_type,
            "value": self.value,
            "row": self.row,
            "col": self.col,
            "style": self.style,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "ButtonData":
        return cls(
            text=data.get("text", ""),
            button_type=data.get("button_type", "url"),
            value=data.get("value", ""),
            row=data.get("row", 0),
            col=data.get("col", 0),
            style=data.get("style", "default"),
        )


@dataclass
class MediaItem:
    """Media elementi"""
    media_type: str  # photo, video, audio, voice, animation, document
    file_id: str
    caption: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "media_type": self.media_type,
            "file_id": self.file_id,
            "caption": self.caption,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "MediaItem":
        return cls(
            media_type=data.get("media_type", "photo"),
            file_id=data.get("file_id", ""),
            caption=data.get("caption"),
        )


@dataclass
class PostData:
    """Cari post məlumatları"""
    text: Optional[str] = None
    parse_mode: str = "HTML"
    media: Optional[MediaItem] = None
    media_group: List[MediaItem] = field(default_factory=list)
    buttons: List[ButtonData] = field(default_factory=list)
    disable_preview: bool = False
    protect_content: bool = False
    current_row: int = 0  # cari sətir indeksi

    def has_content(self) -> bool:
        """Postun məzmunu var mı?"""
        return bool(self.text or self.media or self.media_group)

    def get_button_count(self) -> int:
        return len(self.buttons)

    def get_buttons_as_rows(self) -> List[List[ButtonData]]:
        """Düymələri sətirlərlə qruplaşdır"""
        if not self.buttons:
            return []

        max_row = max(b.row for b in self.buttons) + 1
        rows = [[] for _ in range(max_row)]
        for btn in sorted(self.buttons, key=lambda b: (b.row, b.col)):
            rows[btn.row].append(btn)
        return [row for row in rows if row]

    def get_inline_keyboard(self) -> Optional[List[List[dict]]]:
        """InlineKeyboardMarkup üçün sətirləri qaytar"""
        rows = self.get_buttons_as_rows()
        if not rows:
            return None
        return [[btn.to_inline_button() for btn in row] for row in rows]

    def add_button(self, button: ButtonData, new_row: bool = False) -> None:
        """Düymə əlavə et"""
        if new_row or not self.buttons:
            self.current_row = max((b.row for b in self.buttons), default=-1) + 1

        row_buttons = [b for b in self.buttons if b.row == self.current_row]
        button.row = self.current_row
        button.col = len(row_buttons)
        self.buttons.append(button)

    def remove_button(self, index: int) -> bool:
        """İndeksi ilə düymə sil"""
        if 0 <= index < len(self.buttons):
            self.buttons.pop(index)
            self._reindex_buttons()
            return True
        return False

    def _reindex_buttons(self):
        """Düymə indekslərini yenilə"""
        rows: Dict[int, List[ButtonData]] = {}
        for btn in self.buttons:
            rows.setdefault(btn.row, []).append(btn)

        new_buttons = []
        for new_row_idx, (_, row_btns) in enumerate(sorted(rows.items())):
            for col_idx, btn in enumerate(sorted(row_btns, key=lambda b: b.col)):
                btn.row = new_row_idx
                btn.col = col_idx
                new_buttons.append(btn)
        self.buttons = new_buttons
        if self.buttons:
            self.current_row = max(b.row for b in self.buttons)

    def to_dict(self) -> dict:
        return {
            "text": self.text,
            "parse_mode": self.parse_mode,
            "media": self.media.to_dict() if self.media else None,
            "media_group": [m.to_dict() for m in self.media_group],
            "buttons": [b.to_dict() for b in self.buttons],
            "disable_preview": self.disable_preview,
            "protect_content": self.protect_content,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "PostData":
        post = cls(
            text=data.get("text"),
            parse_mode=data.get("parse_mode", "HTML"),
            disable_preview=data.get("disable_preview", False),
            protect_content=data.get("protect_content", False),
        )
        if data.get("media"):
            post.media = MediaItem.from_dict(data["media"])
        post.media_group = [MediaItem.from_dict(m) for m in data.get("media_group", [])]
        post.buttons = [ButtonData.from_dict(b) for b in data.get("buttons", [])]
        return post

    def to_json(self) -> str:
        """Inline keyboard JSON-a çevir (Bot API formatı)"""
        keyboard = self.get_inline_keyboard()
        if not keyboard:
            return "[]"

        api_keyboard = []
        for row in keyboard:
            api_row = []
            for btn in row:
                api_row.append(btn)
            api_keyboard.append(api_row)

        return json.dumps({"inline_keyboard": api_keyboard}, ensure_ascii=False, indent=2)

    @classmethod
    def from_json_keyboard(cls, json_str: str) -> "PostData":
        """Bot API JSON-dan PostData yarat"""
        data = json.loads(json_str)
        keyboard = data.get("inline_keyboard", data if isinstance(data, list) else [])

        post = cls()
        for row_idx, row in enumerate(keyboard):
            for col_idx, btn_data in enumerate(row):
                btn_type = "url"
                value = ""

                if "url" in btn_data:
                    btn_type = "url"
                    value = btn_data["url"]
                elif "callback_data" in btn_data:
                    btn_type = "callback"
                    value = btn_data["callback_data"]
                elif "web_app" in btn_data:
                    btn_type = "webapp"
                    value = btn_data["web_app"].get("url", "")
                elif "switch_inline_query" in btn_data:
                    btn_type = "switch_inline"
                    value = btn_data["switch_inline_query"]
                elif "switch_inline_query_current_chat" in btn_data:
                    btn_type = "switch_current"
                    value = btn_data["switch_inline_query_current_chat"]
                elif "copy_text" in btn_data:
                    btn_type = "copy"
                    value = btn_data["copy_text"].get("text", "")
                elif "login_url" in btn_data:
                    btn_type = "login"
                    value = btn_data["login_url"].get("url", "")
                elif "callback_game" in btn_data:
                    btn_type = "game"
                elif "pay" in btn_data:
                    btn_type = "pay"

                button = ButtonData(
                    text=btn_data.get("text", ""),
                    button_type=btn_type,
                    value=value,
                    row=row_idx,
                    col=col_idx,
                )
                post.buttons.append(button)

        return post
