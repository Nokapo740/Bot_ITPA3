"""
Состояния для оформления индивидуального заказа
"""
from aiogram.fsm.state import State, StatesGroup


class OrderStates(StatesGroup):
    """Состояния для создания заказа"""
    waiting_for_type = State()
    waiting_for_description = State()
    waiting_for_technologies = State()
    waiting_for_deadline = State()
    waiting_for_budget = State()
    waiting_for_contact = State()
    waiting_for_files = State()
    confirm = State()


class EditProfileStates(StatesGroup):
    """Состояния для редактирования профиля"""
    waiting_for_name = State()
    waiting_for_phone = State()
    waiting_for_email = State()


class SupportStates(StatesGroup):
    """Состояния для обращения в поддержку"""
    waiting_for_subject = State()
    waiting_for_message = State()


class AdminProjectStates(StatesGroup):
    """Состояния для управления проектами (админ)"""
    waiting_for_title = State()
    waiting_for_description = State()
    waiting_for_category = State()
    waiting_for_type = State()
    waiting_for_level = State()
    waiting_for_technologies = State()
    waiting_for_languages = State()
    waiting_for_price = State()
    waiting_for_files = State()
    waiting_for_image = State()
    confirm = State()
    
    # Для редактирования
    edit_select_project = State()
    edit_select_field = State()
    edit_waiting_value = State()


class AdminOrderStates(StatesGroup):
    """Состояния для управления заказами (админ)"""
    select_order = State()
    waiting_for_price = State()
    waiting_for_comment = State()
    waiting_for_files = State()
    waiting_for_rejection_reason = State()


class AdminBroadcastStates(StatesGroup):
    """Состояния для рассылки (админ)"""
    waiting_for_message = State()
    waiting_for_audience = State()
    waiting_for_media = State()
    confirm = State()


class AdminCategoryStates(StatesGroup):
    """Состояния для управления категориями (админ)"""
    waiting_for_name = State()
    waiting_for_description = State()
    waiting_for_icon = State()
    confirm = State()

