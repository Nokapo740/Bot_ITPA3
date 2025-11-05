"""
Клавиатуры для администраторов
"""
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


def get_admin_menu() -> InlineKeyboardMarkup:
    """Главное меню администратора"""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(text="📊 Статистика", callback_data="admin_stats")
    )
    builder.row(
        InlineKeyboardButton(text="📚 Управление каталогом", callback_data="admin_catalog")
    )
    builder.row(
        InlineKeyboardButton(text="📋 Заказы", callback_data="admin_orders")
    )
    builder.row(
        InlineKeyboardButton(text="📢 Рассылка", callback_data="admin_broadcast")
    )
    builder.row(
        InlineKeyboardButton(text="👥 Пользователи", callback_data="admin_users")
    )
    builder.row(
        InlineKeyboardButton(text="📁 Категории", callback_data="admin_categories")
    )
    builder.row(
        InlineKeyboardButton(text="◀️ Пользовательское меню", callback_data="main_menu")
    )
    
    return builder.as_markup()


def get_admin_catalog_menu() -> InlineKeyboardMarkup:
    """Меню управления каталогом"""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(text="➕ Добавить новый проект", callback_data="admin_add_project")
    )
    builder.row(
        InlineKeyboardButton(text="📋 Все проекты (редактировать/удалить)", callback_data="admin_list_projects")
    )
    builder.row(
        InlineKeyboardButton(text="◀️ Назад в админ-меню", callback_data="admin_menu")
    )
    
    return builder.as_markup()


def get_admin_orders_menu() -> InlineKeyboardMarkup:
    """Меню управления заказами"""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(text="🆕 Новые заказы", callback_data="admin_orders_new")
    )
    builder.row(
        InlineKeyboardButton(text="⚙️ В работе", callback_data="admin_orders_in_progress")
    )
    builder.row(
        InlineKeyboardButton(text="✅ Завершенные", callback_data="admin_orders_completed")
    )
    builder.row(
        InlineKeyboardButton(text="📋 Все заказы", callback_data="admin_orders_all")
    )
    builder.row(
        InlineKeyboardButton(text="◀️ Назад", callback_data="admin_menu")
    )
    
    return builder.as_markup()


def get_admin_order_actions_keyboard(order_id: int, current_status: str) -> InlineKeyboardMarkup:
    """Клавиатура действий с заказом"""
    builder = InlineKeyboardBuilder()
    
    # Кнопки изменения статуса в зависимости от текущего
    if current_status == "new":
        builder.row(
            InlineKeyboardButton(text="✅ Принять", callback_data=f"admin_order_accept_{order_id}"),
            InlineKeyboardButton(text="❌ Отклонить", callback_data=f"admin_order_reject_{order_id}")
        )
    elif current_status == "accepted":
        builder.row(
            InlineKeyboardButton(text="⚙️ Начать работу", callback_data=f"admin_order_start_{order_id}")
        )
    elif current_status == "in_progress":
        builder.row(
            InlineKeyboardButton(text="📋 Готово к проверке", callback_data=f"admin_order_ready_{order_id}")
        )
    elif current_status == "ready_for_check":
        builder.row(
            InlineKeyboardButton(text="✅ Завершить", callback_data=f"admin_order_complete_{order_id}")
        )
    
    builder.row(
        InlineKeyboardButton(text="💰 Установить цену", callback_data=f"admin_order_price_{order_id}")
    )
    builder.row(
        InlineKeyboardButton(text="📎 Прикрепить файлы", callback_data=f"admin_order_files_{order_id}")
    )
    builder.row(
        InlineKeyboardButton(text="💬 Добавить комментарий", callback_data=f"admin_order_comment_{order_id}")
    )
    builder.row(
        InlineKeyboardButton(text="◀️ Назад", callback_data="admin_orders")
    )
    
    return builder.as_markup()


def get_admin_broadcast_menu() -> InlineKeyboardMarkup:
    """Меню рассылки"""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(text="📢 Создать рассылку", callback_data="admin_create_broadcast")
    )
    builder.row(
        InlineKeyboardButton(text="📊 История рассылок", callback_data="admin_broadcast_history")
    )
    builder.row(
        InlineKeyboardButton(text="◀️ Назад", callback_data="admin_menu")
    )
    
    return builder.as_markup()


def get_broadcast_audience_keyboard() -> InlineKeyboardMarkup:
    """Выбор аудитории для рассылки"""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(text="👥 Всем пользователям", callback_data="broadcast_audience_all")
    )
    builder.row(
        InlineKeyboardButton(text="💎 С покупками", callback_data="broadcast_audience_buyers")
    )
    builder.row(
        InlineKeyboardButton(text="🆕 Без покупок", callback_data="broadcast_audience_non_buyers")
    )
    builder.row(
        InlineKeyboardButton(text="🔥 Активным", callback_data="broadcast_audience_active")
    )
    builder.row(
        InlineKeyboardButton(text="◀️ Назад", callback_data="admin_broadcast")
    )
    
    return builder.as_markup()


def get_admin_categories_menu() -> InlineKeyboardMarkup:
    """Меню управления категориями"""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(text="➕ Добавить категорию", callback_data="admin_add_category")
    )
    builder.row(
        InlineKeyboardButton(text="📝 Редактировать категорию", callback_data="admin_edit_category")
    )
    builder.row(
        InlineKeyboardButton(text="🗑 Удалить категорию", callback_data="admin_delete_category")
    )
    builder.row(
        InlineKeyboardButton(text="📋 Список категорий", callback_data="admin_list_categories")
    )
    builder.row(
        InlineKeyboardButton(text="◀️ Назад", callback_data="admin_menu")
    )
    
    return builder.as_markup()


def get_admin_users_menu() -> InlineKeyboardMarkup:
    """Меню управления пользователями"""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(text="👥 Список пользователей", callback_data="admin_list_users")
    )
    builder.row(
        InlineKeyboardButton(text="🔍 Поиск пользователя", callback_data="admin_search_user")
    )
    builder.row(
        InlineKeyboardButton(text="🚫 Заблокированные", callback_data="admin_blocked_users")
    )
    builder.row(
        InlineKeyboardButton(text="◀️ Назад", callback_data="admin_menu")
    )
    
    return builder.as_markup()


def get_admin_user_actions_keyboard(user_id: int, is_blocked: bool) -> InlineKeyboardMarkup:
    """Действия с пользователем"""
    builder = InlineKeyboardBuilder()
    
    if is_blocked:
        builder.row(
            InlineKeyboardButton(text="✅ Разблокировать", callback_data=f"admin_unblock_{user_id}")
        )
    else:
        builder.row(
            InlineKeyboardButton(text="🚫 Заблокировать", callback_data=f"admin_block_{user_id}")
        )
    
    builder.row(
        InlineKeyboardButton(text="📦 История заказов", callback_data=f"admin_user_orders_{user_id}")
    )
    builder.row(
        InlineKeyboardButton(text="◀️ Назад", callback_data="admin_users")
    )
    
    return builder.as_markup()

