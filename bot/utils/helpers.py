"""
Вспомогательные функции
"""
from datetime import datetime
from typing import Optional


def format_price(price: float) -> str:
    """Форматировать цену"""
    return f"{price:,.0f}".replace(',', ' ') + " ₸"


def format_datetime(dt: datetime) -> str:
    """Форматировать дату и время"""
    return dt.strftime("%d.%m.%Y %H:%M")


def format_date(dt: datetime) -> str:
    """Форматировать дату"""
    return dt.strftime("%d.%m.%Y")


def truncate_text(text: str, max_length: int = 100) -> str:
    """Обрезать текст до определенной длины"""
    if len(text) <= max_length:
        return text
    return text[:max_length-3] + "..."


def escape_markdown(text: str) -> str:
    """Экранировать специальные символы для Markdown"""
    escape_chars = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
    for char in escape_chars:
        text = text.replace(char, f'\\{char}')
    return text


def get_project_type_emoji(project_type: str) -> str:
    """Получить эмодзи для типа проекта"""
    emojis = {
        'diploma': '🎓',
        'coursework': '📚',
        'presentation': '📊',
        'project': '💻'
    }
    return emojis.get(project_type, '📁')


def get_order_status_emoji(status: str) -> str:
    """Получить эмодзи для статуса заказа"""
    emojis = {
        'new': '🆕',
        'under_review': '👀',
        'accepted': '✅',
        'in_progress': '⚙️',
        'ready_for_check': '📋',
        'completed': '✅',
        'rejected': '❌'
    }
    return emojis.get(status, '❓')


def get_order_status_text(status: str) -> str:
    """Получить текст для статуса заказа"""
    statuses = {
        'new': 'Новый',
        'under_review': 'На рассмотрении',
        'accepted': 'Принят в работу',
        'in_progress': 'Выполняется',
        'ready_for_check': 'Готов к проверке',
        'completed': 'Завершен',
        'rejected': 'Отклонен'
    }
    return statuses.get(status, 'Неизвестно')


def get_level_emoji(level: str) -> str:
    """Получить эмодзи для уровня сложности"""
    emojis = {
        'basic': '⭐',
        'intermediate': '⭐⭐',
        'advanced': '⭐⭐⭐'
    }
    return emojis.get(level, '⭐')


def generate_referral_code(user_id: int) -> str:
    """Сгенерировать реферальный код"""
    import hashlib
    import time
    
    data = f"{user_id}{time.time()}"
    return hashlib.md5(data.encode()).hexdigest()[:8].upper()

