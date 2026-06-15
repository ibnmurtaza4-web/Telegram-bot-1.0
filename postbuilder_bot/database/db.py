"""
Verilənlər bazası - Modellər və inisializasiya
SQLAlchemy asinxron ORM ilə
"""

from datetime import datetime
from typing import Optional, List
import json

from sqlalchemy import (
    Column, Integer, BigInteger, String, Text, Boolean,
    DateTime, JSON, ForeignKey, Index, select, update, delete
)
from sqlalchemy.ext.asyncio import (
    AsyncSession, AsyncEngine, create_async_engine, async_sessionmaker
)
from sqlalchemy.orm import DeclarativeBase, relationship

from config import settings

import logging

logger = logging.getLogger(__name__)


class Base(DeclarativeBase):
    """Baza model sinfi"""
    pass


class User(Base):
    """İstifadəçi modeli"""
    __tablename__ = "users"

    id = Column(BigInteger, primary_key=True)  # Telegram user ID
    username = Column(String(64), nullable=True)
    first_name = Column(String(256), nullable=True)
    last_name = Column(String(256), nullable=True)
    language_code = Column(String(10), default="az")
    is_blocked = Column(Boolean, default=False)
    is_premium = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_active = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    total_posts = Column(Integer, default=0)

    drafts = relationship("Draft", back_populates="user", cascade="all, delete-orphan")
    logs = relationship("ActionLog", back_populates="user", cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_users_username", "username"),
    )

    def __repr__(self):
        return f"<User id={self.id} username={self.username}>"


class Draft(Base):
    """Qaralama modeli"""
    __tablename__ = "drafts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("users.id"), nullable=False)
    name = Column(String(256), nullable=False)
    post_text = Column(Text, nullable=True)
    parse_mode = Column(String(16), default="HTML")
    media_type = Column(String(32), nullable=True)  # photo, video, audio, document, animation
    media_file_id = Column(String(256), nullable=True)
    media_group = Column(JSON, nullable=True)  # albom üçün
    buttons_json = Column(JSON, nullable=True)  # inline keyboard
    disable_preview = Column(Boolean, default=False)
    protect_content = Column(Boolean, default=False)
    is_template = Column(Boolean, default=False)
    template_name = Column(String(128), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="drafts")

    __table_args__ = (
        Index("idx_drafts_user_id", "user_id"),
        Index("idx_drafts_is_template", "is_template"),
    )

    def __repr__(self):
        return f"<Draft id={self.id} name={self.name}>"

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "post_text": self.post_text,
            "parse_mode": self.parse_mode,
            "media_type": self.media_type,
            "media_file_id": self.media_file_id,
            "media_group": self.media_group,
            "buttons_json": self.buttons_json,
            "disable_preview": self.disable_preview,
            "protect_content": self.protect_content,
            "is_template": self.is_template,
            "template_name": self.template_name,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class ScheduledPost(Base):
    """Planlaşdırılmış göndəriş"""
    __tablename__ = "scheduled_posts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("users.id"), nullable=False)
    draft_id = Column(Integer, ForeignKey("drafts.id"), nullable=True)
    targets = Column(JSON, nullable=False)  # göndəriləcək chat ID-lər
    scheduled_at = Column(DateTime, nullable=False)
    is_recurring = Column(Boolean, default=False)
    recur_interval = Column(String(32), nullable=True)  # daily, weekly, etc.
    sent = Column(Boolean, default=False)
    sent_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index("idx_scheduled_user", "user_id"),
        Index("idx_scheduled_sent", "sent"),
        Index("idx_scheduled_at", "scheduled_at"),
    )


class ActionLog(Base):
    """Əməliyyat logu"""
    __tablename__ = "action_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("users.id"), nullable=False)
    action = Column(String(128), nullable=False)
    details = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="logs")

    __table_args__ = (
        Index("idx_logs_user_id", "user_id"),
        Index("idx_logs_action", "action"),
        Index("idx_logs_created_at", "created_at"),
    )


class BroadcastMessage(Base):
    """Broadcast mesajları"""
    __tablename__ = "broadcast_messages"

    id = Column(Integer, primary_key=True, autoincrement=True)
    admin_id = Column(BigInteger, nullable=False)
    message_text = Column(Text, nullable=False)
    total_users = Column(Integer, default=0)
    sent_count = Column(Integer, default=0)
    failed_count = Column(Integer, default=0)
    status = Column(String(32), default="pending")  # pending, running, done, failed
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)


# ─── Engine və Session ──────────────────────────────────────────────────────

engine: Optional[AsyncEngine] = None
async_session: Optional[async_sessionmaker] = None


async def init_db():
    """Verilənlər bazasını inisializasiya et"""
    global engine, async_session

    engine = create_async_engine(
        settings.DATABASE_URL,
        echo=False,
        pool_pre_ping=True,
    )

    async_session = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    logger.info("Verilənlər bazası inisializasiya edildi")


def get_session() -> AsyncSession:
    """Yeni session qaytar"""
    return async_session()


# ─── Repository funksiyaları ────────────────────────────────────────────────

async def get_or_create_user(
    user_id: int,
    username: Optional[str] = None,
    first_name: Optional[str] = None,
    last_name: Optional[str] = None,
    language_code: Optional[str] = "az",
) -> User:
    """İstifadəçini tap və ya yarat"""
    async with get_session() as session:
        result = await session.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()

        if user is None:
            user = User(
                id=user_id,
                username=username,
                first_name=first_name,
                last_name=last_name,
                language_code=language_code or "az",
            )
            session.add(user)
        else:
            user.username = username
            user.first_name = first_name
            user.last_name = last_name
            user.last_active = datetime.utcnow()

        await session.commit()
        await session.refresh(user)
        return user


async def get_user(user_id: int) -> Optional[User]:
    """İstifadəçini tap"""
    async with get_session() as session:
        result = await session.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()


async def block_user(user_id: int, blocked: bool = True):
    """İstifadəçini blokla/açma"""
    async with get_session() as session:
        await session.execute(
            update(User).where(User.id == user_id).values(is_blocked=blocked)
        )
        await session.commit()


async def get_all_users() -> List[User]:
    """Bütün istifadəçiləri gətir"""
    async with get_session() as session:
        result = await session.execute(select(User).where(User.is_blocked == False))
        return result.scalars().all()


async def get_user_count() -> int:
    """İstifadəçi sayını qaytar"""
    async with get_session() as session:
        from sqlalchemy import func
        result = await session.execute(select(func.count(User.id)))
        return result.scalar() or 0


async def save_draft(
    user_id: int,
    name: str,
    post_text: Optional[str] = None,
    parse_mode: str = "HTML",
    media_type: Optional[str] = None,
    media_file_id: Optional[str] = None,
    media_group: Optional[list] = None,
    buttons_json: Optional[list] = None,
    disable_preview: bool = False,
    protect_content: bool = False,
    is_template: bool = False,
    template_name: Optional[str] = None,
    draft_id: Optional[int] = None,
) -> Draft:
    """Qaralama saxla və ya yenilə"""
    async with get_session() as session:
        if draft_id:
            result = await session.execute(
                select(Draft).where(Draft.id == draft_id, Draft.user_id == user_id)
            )
            draft = result.scalar_one_or_none()
            if draft:
                draft.name = name
                draft.post_text = post_text
                draft.parse_mode = parse_mode
                draft.media_type = media_type
                draft.media_file_id = media_file_id
                draft.media_group = media_group
                draft.buttons_json = buttons_json
                draft.disable_preview = disable_preview
                draft.protect_content = protect_content
                draft.is_template = is_template
                draft.template_name = template_name
                draft.updated_at = datetime.utcnow()
                await session.commit()
                await session.refresh(draft)
                return draft

        draft = Draft(
            user_id=user_id,
            name=name,
            post_text=post_text,
            parse_mode=parse_mode,
            media_type=media_type,
            media_file_id=media_file_id,
            media_group=media_group,
            buttons_json=buttons_json,
            disable_preview=disable_preview,
            protect_content=protect_content,
            is_template=is_template,
            template_name=template_name,
        )
        session.add(draft)
        await session.commit()
        await session.refresh(draft)
        return draft


async def get_user_drafts(user_id: int, templates_only: bool = False) -> List[Draft]:
    """İstifadəçinin qaralamalarını gətir"""
    async with get_session() as session:
        query = select(Draft).where(Draft.user_id == user_id)
        if templates_only:
            query = query.where(Draft.is_template == True)
        query = query.order_by(Draft.updated_at.desc())
        result = await session.execute(query)
        return result.scalars().all()


async def get_draft(draft_id: int, user_id: int) -> Optional[Draft]:
    """Qaralama tap"""
    async with get_session() as session:
        result = await session.execute(
            select(Draft).where(Draft.id == draft_id, Draft.user_id == user_id)
        )
        return result.scalar_one_or_none()


async def delete_draft(draft_id: int, user_id: int) -> bool:
    """Qaralama sil"""
    async with get_session() as session:
        result = await session.execute(
            delete(Draft).where(Draft.id == draft_id, Draft.user_id == user_id)
        )
        await session.commit()
        return result.rowcount > 0


async def log_action(user_id: int, action: str, details: Optional[dict] = None):
    """Əməliyyatı logla"""
    async with get_session() as session:
        log = ActionLog(user_id=user_id, action=action, details=details)
        session.add(log)
        await session.commit()


async def get_stats() -> dict:
    """Statistika qaytar"""
    async with get_session() as session:
        from sqlalchemy import func

        user_count = (await session.execute(select(func.count(User.id)))).scalar() or 0
        active_count = (
            await session.execute(
                select(func.count(User.id)).where(User.is_blocked == False)
            )
        ).scalar() or 0
        draft_count = (await session.execute(select(func.count(Draft.id)))).scalar() or 0
        template_count = (
            await session.execute(
                select(func.count(Draft.id)).where(Draft.is_template == True)
            )
        ).scalar() or 0

        return {
            "total_users": user_count,
            "active_users": active_count,
            "total_drafts": draft_count,
            "total_templates": template_count,
        }
