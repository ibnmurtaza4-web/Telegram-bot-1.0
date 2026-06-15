"""
FSM State-lər - Bütün bot vəziyyətləri
"""

from aiogram.fsm.state import State, StatesGroup


class PostStates(StatesGroup):
    """Post qurma vəziyyətləri"""
    # Ana menyular
    main_menu = State()
    post_menu = State()

    # Mətn
    waiting_text = State()
    editing_text = State()

    # Media
    waiting_media = State()
    waiting_media_caption = State()
    waiting_media_group = State()

    # Önizləmə
    preview = State()


class ButtonStates(StatesGroup):
    """Düymə qurma vəziyyətləri"""
    button_menu = State()

    # Düymə növü seçimi
    choosing_type = State()

    # URL düymə
    waiting_url_text = State()
    waiting_url = State()

    # Callback düymə
    waiting_callback_text = State()
    waiting_callback_data = State()

    # Web App düymə
    waiting_webapp_text = State()
    waiting_webapp_url = State()

    # Share düymə
    waiting_share_text = State()
    waiting_share_url = State()

    # Switch Inline
    waiting_switch_text = State()
    waiting_switch_query = State()

    # Copy Text
    waiting_copy_text = State()
    waiting_copy_value = State()

    # Login URL
    waiting_login_text = State()
    waiting_login_url = State()

    # Düymə redaktəsi
    editing_button = State()
    waiting_new_button_text = State()
    waiting_new_button_value = State()


class SendStates(StatesGroup):
    """Göndərmə vəziyyətləri"""
    choosing_target_type = State()
    waiting_chat_id = State()
    waiting_multiple_targets = State()
    confirming_send = State()

    # Planlaşdırma
    waiting_schedule_date = State()
    waiting_schedule_time = State()

    # Təkrarlanan
    choosing_recur_interval = State()


class DraftStates(StatesGroup):
    """Qaralama vəziyyətləri"""
    viewing_drafts = State()
    waiting_draft_name = State()
    managing_draft = State()
    confirming_delete = State()


class JsonStates(StatesGroup):
    """JSON rejimi vəziyyətləri"""
    main = State()
    waiting_import = State()
    editing_json = State()


class AdminStates(StatesGroup):
    """Admin vəziyyətləri"""
    main = State()
    waiting_broadcast = State()
    confirming_broadcast = State()
    waiting_user_id = State()
    viewing_stats = State()
    maintenance_confirm = State()


class TemplateStates(StatesGroup):
    """Şablon vəziyyətləri"""
    choosing_template = State()
    editing_template = State()
    saving_as_template = State()
    waiting_template_name = State()


class PremiumStates(StatesGroup):
    """Premium xüsusiyyət vəziyyətləri"""
    main = State()
    deep_link = State()
    waiting_deep_link_bot = State()
    waiting_deep_link_param = State()
    utm_generator = State()
    waiting_utm_url = State()
    waiting_utm_source = State()
    waiting_utm_medium = State()
    waiting_utm_campaign = State()
    qr_code = State()
    waiting_qr_text = State()
    markdown_html = State()
    waiting_convert_text = State()
