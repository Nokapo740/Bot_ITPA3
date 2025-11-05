"""
Клавиатуры для пользователей
"""
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from typing import List, Optional


def get_main_menu() -> InlineKeyboardMarkup:
    """Главное меню пользователя"""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(text="🛍 Каталог проектов", callback_data="catalog")
    )
    builder.row(
        InlineKeyboardButton(text="📝 Заказать проект", callback_data="create_order")
    )
    builder.row(
        InlineKeyboardButton(text="🛒 Корзина", callback_data="cart"),
        InlineKeyboardButton(text="📦 Мои заказы", callback_data="my_orders")
    )
    builder.row(
        InlineKeyboardButton(text="👤 Профиль", callback_data="profile"),
        InlineKeyboardButton(text="💬 Поддержка", callback_data="support")
    )
    
    return builder.as_markup()


def get_back_button(callback_data: str = "main_menu") -> InlineKeyboardMarkup:
    """Кнопка 'Назад'"""
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="◀️ Назад", callback_data=callback_data))
    return builder.as_markup()


def get_catalog_menu() -> InlineKeyboardMarkup:
    """Меню каталога"""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(text="📚 Все проекты", callback_data="catalog_all")
    )
    builder.row(
        InlineKeyboardButton(text="🎓 Дипломы", callback_data="catalog_type_diploma")
    )
    builder.row(
        InlineKeyboardButton(text="📖 Курсовые", callback_data="catalog_type_coursework")
    )
    builder.row(
        InlineKeyboardButton(text="📊 Презентации", callback_data="catalog_type_presentation")
    )
    builder.row(
        InlineKeyboardButton(text="💻 Проекты", callback_data="catalog_type_project")
    )
    builder.row(
        InlineKeyboardButton(text="🔍 Поиск", callback_data="catalog_search")
    )
    builder.row(
        InlineKeyboardButton(text="◀️ Назад", callback_data="main_menu")
    )
    
    return builder.as_markup()


def get_project_card_keyboard(
    project_id: int,
    in_cart: bool = False,
    is_purchased: bool = False,
    page: int = 0
) -> InlineKeyboardMarkup:
    """Клавиатура для карточки проекта"""
    builder = InlineKeyboardBuilder()
    
    if is_purchased:
        builder.row(
            InlineKeyboardButton(text="📥 Скачать", callback_data=f"download_{project_id}")
        )
    else:
        if not in_cart:
            builder.row(
                InlineKeyboardButton(text="🛒 В корзину", callback_data=f"add_cart_{project_id}"),
                InlineKeyboardButton(text="💳 Купить сейчас", callback_data=f"buy_now_{project_id}")
            )
        else:
            builder.row(
                InlineKeyboardButton(text="❌ Убрать из корзины", callback_data=f"remove_cart_{project_id}")
            )
    
    builder.row(
        InlineKeyboardButton(text="◀️ Назад к каталогу", callback_data=f"catalog_page_{page}")
    )
    
    return builder.as_markup()


def get_pagination_keyboard(
    page: int,
    total_pages: int,
    prefix: str = "catalog"
) -> InlineKeyboardMarkup:
    """Клавиатура с пагинацией"""
    builder = InlineKeyboardBuilder()
    
    buttons = []
    
    if page > 0:
        buttons.append(InlineKeyboardButton(text="⬅️", callback_data=f"{prefix}_page_{page-1}"))
    
    buttons.append(InlineKeyboardButton(text=f"📄 {page+1}/{total_pages}", callback_data="current_page"))
    
    if page < total_pages - 1:
        buttons.append(InlineKeyboardButton(text="➡️", callback_data=f"{prefix}_page_{page+1}"))
    
    builder.row(*buttons)
    builder.row(InlineKeyboardButton(text="◀️ Назад", callback_data="catalog"))
    
    return builder.as_markup()


def get_cart_keyboard(has_items: bool = False) -> InlineKeyboardMarkup:
    """Клавиатура корзины"""
    builder = InlineKeyboardBuilder()
    
    if has_items:
        builder.row(
            InlineKeyboardButton(text="💳 Оформить заказ", callback_data="checkout")
        )
        builder.row(
            InlineKeyboardButton(text="🗑 Очистить корзину", callback_data="clear_cart")
        )
    
    builder.row(
        InlineKeyboardButton(text="🛍 Продолжить покупки", callback_data="catalog")
    )
    builder.row(
        InlineKeyboardButton(text="◀️ Главное меню", callback_data="main_menu")
    )
    
    return builder.as_markup()


def get_cart_item_keyboard(project_id: int) -> InlineKeyboardMarkup:
    """Клавиатура для элемента корзины"""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(text="👁 Подробнее", callback_data=f"project_{project_id}"),
        InlineKeyboardButton(text="❌ Удалить", callback_data=f"remove_cart_{project_id}")
    )
    
    return builder.as_markup()


def get_order_types_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура выбора типа заказа"""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(text="🎓 Диплом", callback_data="order_type_diploma")
    )
    builder.row(
        InlineKeyboardButton(text="📖 Курсовая", callback_data="order_type_coursework")
    )
    builder.row(
        InlineKeyboardButton(text="📊 Презентация", callback_data="order_type_presentation")
    )
    builder.row(
        InlineKeyboardButton(text="💻 Проект", callback_data="order_type_project")
    )
    builder.row(
        InlineKeyboardButton(text="❌ Отмена", callback_data="main_menu")
    )
    
    return builder.as_markup()


def get_skip_button(callback_data: str) -> InlineKeyboardMarkup:
    """Кнопка 'Пропустить'"""
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="⏭ Пропустить", callback_data=callback_data))
    builder.row(InlineKeyboardButton(text="❌ Отмена", callback_data="main_menu"))
    return builder.as_markup()


def get_confirm_keyboard(confirm_callback: str, cancel_callback: str = "main_menu") -> InlineKeyboardMarkup:
    """Клавиатура подтверждения"""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(text="✅ Подтвердить", callback_data=confirm_callback),
        InlineKeyboardButton(text="❌ Отмена", callback_data=cancel_callback)
    )
    
    return builder.as_markup()


def get_my_orders_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура раздела 'Мои заказы'"""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(text="📦 Покупки", callback_data="my_purchases")
    )
    builder.row(
        InlineKeyboardButton(text="📝 Индивидуальные заказы", callback_data="my_custom_orders")
    )
    builder.row(
        InlineKeyboardButton(text="◀️ Назад", callback_data="main_menu")
    )
    
    return builder.as_markup()


def get_order_details_keyboard(order_id: int) -> InlineKeyboardMarkup:
    """Клавиатура для деталей заказа"""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(text="💬 Связаться с поддержкой", callback_data=f"support_order_{order_id}")
    )
    builder.row(
        InlineKeyboardButton(text="◀️ Назад", callback_data="my_custom_orders")
    )
    
    return builder.as_markup()


def get_profile_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура профиля"""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(text="✏️ Редактировать профиль", callback_data="edit_profile")
    )
    builder.row(
        InlineKeyboardButton(text="📊 Статистика", callback_data="profile_stats")
    )
    builder.row(
        InlineKeyboardButton(text="◀️ Назад", callback_data="main_menu")
    )
    
    return builder.as_markup()


def get_support_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура поддержки"""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(text="📝 Создать обращение", callback_data="create_ticket")
    )
    builder.row(
        InlineKeyboardButton(text="📋 Мои обращения", callback_data="my_tickets")
    )
    builder.row(
        InlineKeyboardButton(text="❓ FAQ", callback_data="faq")
    )
    builder.row(
        InlineKeyboardButton(text="◀️ Назад", callback_data="main_menu")
    )
    
    return builder.as_markup()

