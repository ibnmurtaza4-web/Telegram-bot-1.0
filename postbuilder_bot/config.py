"""
Konfiqurasiya - Bütün parametrlər
"""

import os
from dataclasses import dataclass, field
from typing import List


@dataclass
class Settings:
    """Bot parametrləri"""

    # ─── Bot Token ───────────────────────────────────────
    BOT_TOKEN: str = field(
        default_factory=lambda: os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")
    )

    # ─── Admin IDs ───────────────────────────────────────
    ADMIN_IDS: List[int] = field(
        default_factory=lambda: [
            int(x)
            for x in os.getenv("ADMIN_IDS", "123456789").split(",")
            if x.strip().isdigit()
        ]
    )

    # ─── Verilənlər bazası ───────────────────────────────
    DATABASE_URL: str = field(
        default_factory=lambda: "sqlite+aiosqlite:///postbuilder.db"
    )

    # ─── Limitlər ────────────────────────────────────────
    MAX_BUTTONS_PER_ROW: int = 8
    MAX_BUTTON_ROWS: int = 100
    MAX_TEXT_LENGTH: int = 4096
    MAX_CAPTION_LENGTH: int = 1024
    MAX_DRAFTS_PER_USER: int = 50
    MAX_TARGETS_AT_ONCE: int = 10

    # ─── Throttling ──────────────────────────────────────
    THROTTLE_RATE: float = 0.5  # saniyə

    # ─── Xüsusiyyətlər ───────────────────────────────────
    MAINTENANCE_MODE: bool = field(
        default_factory=lambda: os.getenv("MAINTENANCE_MODE", "false").lower() == "true"
    )

    # ─── Versiya ─────────────────────────────────────────
    VERSION: str = "2.0.0"
    BOT_NAME: str = "PostBuilder Pro"


settings = Settings()
