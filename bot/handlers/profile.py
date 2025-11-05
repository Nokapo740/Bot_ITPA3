"""
Обработчики профиля пользователя
"""
from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from bot.database import crud
from bot.keyboards import user as kb
from bot.states.order import EditProfileStates
from bot.utils.helpers import format_datetime

router = Router()


@router.callback_query(F.data == "profile")
async def callback_profile(callback: CallbackQuery, session: AsyncSession):
    """Показать профиль"""
    user = await crud.get_user_by_telegram_id(session, callback.from_user.id)
    
    if not user:
        await callback.answer("❌ Ошибка", show_alert=True)
        return
    
    # Получаем статистику
    purchases = await crud.get_user_purchases(session, user.id)
    orders = await crud.get_user_orders(session, user.id)
    
    profile_text = (
        "👤 <b>Ваш профиль</b>\n\n"
        f"<b>Имя:</b> {user.first_name or 'Не указано'}"
    )
    
    if user.last_name:
        profile_text += f" {user.last_name}"
    
    profile_text += (
        f"\n<b>Username:</b> @{user.username or 'не указан'}\n"
        f"<b>Telegram ID:</b> {user.telegram_id}\n\n"
    )
    
    if user.phone:
        profile_text += f"<b>Телефон:</b> {user.phone}\n"
    
    if user.email:
        profile_text += f"<b>Email:</b> {user.email}\n"
    
    profile_text += (
        f"\n<b>Регистрация:</b> {format_datetime(user.created_at)}\n\n"
        f"📊 <b>Статистика:</b>\n"
        f"💎 Покупок: {len(purchases)}\n"
        f"📝 Заказов: {len(orders)}"
    )
    
    await callback.message.edit_text(
        profile_text,
        reply_markup=kb.get_profile_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data == "profile_stats")
async def callback_profile_stats(callback: CallbackQuery, session: AsyncSession):
    """Детальная статистика"""
    user = await crud.get_user_by_telegram_id(session, callback.from_user.id)
    
    if not user:
        await callback.answer("❌ Ошибка", show_alert=True)
        return
    
    purchases = await crud.get_user_purchases(session, user.id)
    orders = await crud.get_user_orders(session, user.id)
    
    total_spent = sum(p.price for p in purchases)
    
    # Считаем статусы заказов
    from bot.database.models import OrderStatus
    orders_by_status = {}
    for order in orders:
        status = order.status.value
        orders_by_status[status] = orders_by_status.get(status, 0) + 1
    
    stats_text = (
        "📊 <b>Детальная статистика</b>\n\n"
        f"<b>Всего покупок:</b> {len(purchases)}\n"
        f"<b>Потрачено:</b> {total_spent:,.0f} ₸\n\n"
        f"<b>Индивидуальные заказы:</b> {len(orders)}\n"
    )
    
    if orders_by_status:
        stats_text += "\n<b>По статусам:</b>\n"
        status_names = {
            'new': '🆕 Новые',
            'under_review': '👀 На рассмотрении',
            'accepted': '✅ Приняты',
            'in_progress': '⚙️ В работе',
            'ready_for_check': '📋 Готовы',
            'completed': '✅ Завершены',
            'rejected': '❌ Отклонены'
        }
        
        for status, count in orders_by_status.items():
            status_name = status_names.get(status, status)
            stats_text += f"• {status_name}: {count}\n"
    
    await callback.message.edit_text(
        stats_text,
        reply_markup=kb.get_back_button("profile"),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data == "edit_profile")
async def callback_edit_profile(callback: CallbackQuery):
    """Редактировать профиль"""
    await callback.message.edit_text(
        "✏️ <b>Редактирование профиля</b>\n\n"
        "Функция в разработке...\n"
        "Скоро вы сможете редактировать свои данные.",
        reply_markup=kb.get_back_button("profile"),
        parse_mode="HTML"
    )
    await callback.answer()

