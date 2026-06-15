"""
Admin Handler - Admin panel, statistika, broadcast, blok
"""

import asyncio
import logging
import time
from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from aiogram.exceptions import TelegramForbiddenError

from states import AdminStates
from keyboards import admin_keyboard, confirm_keyboard, back_cancel_keyboard
from locales import get_user_lang, t
from database import get_stats, get_all_users, block_user, log_action
from config import settings

router = Router()
logger = logging.getLogger(__name__)


def get_lang(user): return get_user_lang(getattr(user, "language_code", "az"))


def is_admin(user_id: int) -> bool:
    return user_id in settings.ADMIN_IDS


# ─── Admin menyusu ──────────────────────────────────────────────────────────

@router.callback_query(F.data == "admin:stats")
async def cb_admin_stats(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ İcazəniz yoxdur.", show_alert=True)
        return

    stats = await get_stats()
    await callback.message.edit_text(
        t("stats_text", "az",
          total_users=stats["total_users"],
          active_users=stats["active_users"],
          total_drafts=stats["total_drafts"],
          total_templates=stats["total_templates"]),
        reply_markup=admin_keyboard(),
    )
    await callback.answer()


@router.callback_query(F.data == "admin:broadcast")
async def cb_admin_broadcast(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ İcazəniz yoxdur.", show_alert=True)
        return

    await state.set_state(AdminStates.waiting_broadcast)
    await callback.message.edit_text(
        t("waiting_broadcast", "az"),
        reply_markup=back_cancel_keyboard("admin:cancel", "az"),
    )
    await callback.answer()


@router.message(AdminStates.waiting_broadcast)
async def handle_broadcast_message(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return

    text = message.text or message.caption
    if not text:
        await message.answer("❌ Boş mesaj göndərmək olmaz.")
        return

    users = await get_all_users()
    await state.update_data(broadcast_text=text)
    await state.set_state(AdminStates.confirming_broadcast)

    preview = text[:200] + ("..." if len(text) > 200 else "")
    await message.answer(
        f"📢 <b>Broadcast Təsdiqləmə</b>\n\n"
        f"Mesaj önizləməsi:\n<i>{preview}</i>\n\n"
        f"Göndəriləcək istifadəçi: <b>{len(users)}</b>\n\n"
        f"Göndərməyi təsdiqləyin?",
        reply_markup=confirm_keyboard("admin:broadcast_send", "admin:cancel"),
    )


@router.callback_query(AdminStates.confirming_broadcast, F.data == "admin:broadcast_send")
async def cb_broadcast_send(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ İcazəniz yoxdur.", show_alert=True)
        return

    data = await state.get_data()
    text = data.get("broadcast_text", "")
    bot: Bot = callback.bot

    status_msg = await callback.message.edit_text("📢 Broadcast başladıldı...")
    await state.clear()

    users = await get_all_users()
    success = 0
    failed = 0
    start_time = time.time()

    for user in users:
        try:
            await bot.send_message(chat_id=user.id, text=text, parse_mode="HTML")
            success += 1
        except TelegramForbiddenError:
            failed += 1
            await block_user(user.id, True)
        except Exception:
            failed += 1
        await asyncio.sleep(0.05)

    elapsed = round(time.time() - start_time, 1)
    await status_msg.edit_text(
        t("broadcast_done", "az", success=success, failed=failed, time=elapsed),
        reply_markup=admin_keyboard(),
    )
    await log_action(callback.from_user.id, "broadcast", {"success": success, "failed": failed})


@router.callback_query(F.data == "admin:block")
async def cb_admin_block(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ İcazəniz yoxdur.", show_alert=True)
        return

    await state.set_state(AdminStates.waiting_user_id)
    await state.update_data(block_action="block")
    await callback.message.edit_text(
        t("waiting_user_id_block", "az"),
        reply_markup=back_cancel_keyboard("admin:cancel", "az"),
    )
    await callback.answer()


@router.callback_query(F.data == "admin:unblock")
async def cb_admin_unblock(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ İcazəniz yoxdur.", show_alert=True)
        return

    await state.set_state(AdminStates.waiting_user_id)
    await state.update_data(block_action="unblock")
    await callback.message.edit_text(
        t("waiting_user_id_unblock", "az"),
        reply_markup=back_cancel_keyboard("admin:cancel", "az"),
    )
    await callback.answer()


@router.message(AdminStates.waiting_user_id)
async def handle_user_id_block(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return

    try:
        user_id = int(message.text.strip())
    except ValueError:
        await message.answer("❌ Düzgün istifadəçi ID-si daxil edin (rəqəm).")
        return

    data = await state.get_data()
    action = data.get("block_action", "block")
    do_block = action == "block"

    await block_user(user_id, do_block)
    await state.clear()

    if do_block:
        await message.answer(t("user_blocked", "az", user_id=user_id), reply_markup=admin_keyboard())
    else:
        await message.answer(t("user_unblocked", "az", user_id=user_id), reply_markup=admin_keyboard())


@router.callback_query(F.data == "admin:maintenance")
async def cb_maintenance(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ İcazəniz yoxdur.", show_alert=True)
        return

    settings.MAINTENANCE_MODE = not settings.MAINTENANCE_MODE
    status = "aktivləşdirildi ✅" if settings.MAINTENANCE_MODE else "söndürüldü ✅"
    await callback.answer(f"🔧 Texniki xidmət rejimi {status}", show_alert=True)
    await callback.message.edit_reply_markup(reply_markup=admin_keyboard())


@router.callback_query(F.data == "admin:logs")
async def cb_admin_logs(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ İcazəniz yoxdur.", show_alert=True)
        return

    try:
        with open("bot.log", "r", encoding="utf-8") as f:
            lines = f.readlines()
        last_lines = "".join(lines[-20:])
        text = f"📋 <b>Son 20 log sətri:</b>\n\n<pre>{last_lines[-3000:]}</pre>"
    except FileNotFoundError:
        text = "📋 Log faylı tapılmadı."

    await callback.message.edit_text(text, reply_markup=admin_keyboard())
    await callback.answer()


@router.callback_query(F.data == "admin:cancel")
async def cb_admin_cancel(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text("⚙️ <b>Admin Paneli</b>", reply_markup=admin_keyboard())
    await callback.answer()
