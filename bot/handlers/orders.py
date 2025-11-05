"""
Обработчики заказов (индивидуальных и покупок)
"""
from aiogram import Router, F
from aiogram.types import CallbackQuery, Message, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from bot.database import crud
from bot.database.models import ProjectType, OrderStatus
from bot.keyboards import user as kb
from bot.states.order import OrderStates
from bot.utils.helpers import format_price, format_datetime, get_order_status_emoji, get_order_status_text

router = Router()


# ============== МОИ ЗАКАЗЫ ==============

@router.callback_query(F.data == "my_orders")
async def callback_my_orders(callback: CallbackQuery):
    """Раздел 'Мои заказы'"""
    await callback.message.edit_text(
        "📦 <b>Мои заказы</b>\n\n"
        "Выберите раздел:",
        reply_markup=kb.get_my_orders_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data == "my_purchases")
async def callback_my_purchases(callback: CallbackQuery, session: AsyncSession):
    """История покупок"""
    user = await crud.get_user_by_telegram_id(session, callback.from_user.id)
    
    if not user:
        await callback.answer("❌ Ошибка", show_alert=True)
        return
    
    purchases = await crud.get_user_purchases(session, user.id)
    
    if not purchases:
        await callback.message.edit_text(
            "📭 <b>У вас пока нет покупок</b>\n\n"
            "Приобретите проекты из каталога!",
            reply_markup=kb.get_back_button("my_orders"),
            parse_mode="HTML"
        )
        await callback.answer()
        return
    
    purchases_text = "📦 <b>Мои покупки</b>\n\n"
    
    for i, purchase in enumerate(purchases, start=1):
        project = purchase.project
        purchases_text += (
            f"{i}. <b>{project.title}</b>\n"
            f"   💰 {format_price(purchase.price)}\n"
            f"   📅 {format_datetime(purchase.created_at)}\n"
            f"   📥 /download_{project.id}\n\n"
        )
    
    await callback.message.edit_text(
        purchases_text,
        reply_markup=kb.get_back_button("my_orders"),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data == "my_custom_orders")
async def callback_my_custom_orders(callback: CallbackQuery, session: AsyncSession):
    """Индивидуальные заказы"""
    user = await crud.get_user_by_telegram_id(session, callback.from_user.id)
    
    if not user:
        await callback.answer("❌ Ошибка", show_alert=True)
        return
    
    orders = await crud.get_user_orders(session, user.id)
    
    if not orders:
        await callback.message.edit_text(
            "📭 <b>У вас пока нет индивидуальных заказов</b>\n\n"
            "Создайте заказ в главном меню!",
            reply_markup=kb.get_back_button("my_orders"),
            parse_mode="HTML"
        )
        await callback.answer()
        return
    
    orders_text = "📝 <b>Мои индивидуальные заказы</b>\n\n"
    
    from aiogram.utils.keyboard import InlineKeyboardBuilder
    builder = InlineKeyboardBuilder()
    
    for i, order in enumerate(orders, start=1):
        status_emoji = get_order_status_emoji(order.status.value)
        status_text = get_order_status_text(order.status.value)
        
        orders_text += (
            f"{i}. <b>Заказ #{order.id}</b>\n"
            f"   {status_emoji} Статус: {status_text}\n"
            f"   📅 {format_datetime(order.created_at)}\n\n"
        )
        
        builder.row(InlineKeyboardButton(
            text=f"{status_emoji} Заказ #{order.id}",
            callback_data=f"order_details_{order.id}"
        ))
    
    builder.row(InlineKeyboardButton(text="◀️ Назад", callback_data="my_orders"))
    
    await callback.message.edit_text(
        orders_text,
        reply_markup=builder.as_markup(),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data.startswith("order_details_"))
async def callback_order_details(callback: CallbackQuery, session: AsyncSession):
    """Показать детали заказа"""
    order_id = int(callback.data.split("_")[-1])
    
    user = await crud.get_user_by_telegram_id(session, callback.from_user.id)
    if not user:
        await callback.answer("❌ Ошибка", show_alert=True)
        return
    
    order = await crud.get_order_by_id(session, order_id)
    
    if not order or order.user_id != user.id:
        await callback.answer("❌ Заказ не найден", show_alert=True)
        return
    
    status_emoji = get_order_status_emoji(order.status.value)
    status_text = get_order_status_text(order.status.value)
    
    type_names = {
        'diploma': '🎓 Диплом',
        'coursework': '📖 Курсовая',
        'presentation': '📊 Презентация',
        'project': '💻 Проект'
    }
    
    order_details = (
        f"╔═══════════════════════════════╗\n"
        f"     📝 <b>ЗАКАЗ #{order.id}</b>     \n"
        f"╚═══════════════════════════════╝\n\n"
        f"🔹 <b>Статус:</b> {status_emoji} {status_text}\n\n"
        f"═══════════════════════════════\n\n"
        f"📚 <b>Тип работы:</b> {type_names.get(order.project_type.value, order.project_type.value)}\n\n"
        f"═══════════════════════════════\n\n"
        f"📋 <b>ТЕХНИЧЕСКОЕ ЗАДАНИЕ (ТЗ):</b>\n\n"
        f"{order.description}\n\n"
    )
    
    if order.technologies:
        order_details += (
            f"═══════════════════════════════\n\n"
            f"💻 <b>Технологии/Требования:</b>\n{order.technologies}\n\n"
        )
    
    order_details += f"═══════════════════════════════\n\n"
    
    if order.deadline:
        order_details += f"📅 <b>Желаемый срок выполнения:</b>\n{order.deadline}\n\n"
    
    if order.budget:
        order_details += f"💰 <b>Ваш бюджет:</b>\n{order.budget}\n\n"
    
    if order.price:
        order_details += f"💵 <b>Цена от администрации:</b>\n{format_price(order.price)}\n\n"
    
    if order.admin_comment:
        order_details += (
            f"═══════════════════════════════\n\n"
            f"💬 <b>Комментарий администратора:</b>\n\n"
            f"{order.admin_comment}\n\n"
        )
    
    if order.rejection_reason:
        order_details += (
            f"═══════════════════════════════\n\n"
            f"❌ <b>Причина отклонения:</b>\n\n"
            f"{order.rejection_reason}\n\n"
        )
    
    order_details += (
        f"═══════════════════════════════\n\n"
        f"📆 <b>Дата создания:</b> {format_datetime(order.created_at)}\n"
    )
    
    if order.completed_at:
        order_details += f"✅ <b>Дата завершения:</b> {format_datetime(order.completed_at)}\n"
    
    order_details += f"\n╚═══════════════════════════════╝"
    
    await callback.message.edit_text(
        order_details,
        reply_markup=kb.get_order_details_keyboard(order_id),
        parse_mode="HTML"
    )
    await callback.answer()


# ============== СОЗДАНИЕ ЗАКАЗА ==============

@router.callback_query(F.data == "create_order")
async def callback_create_order(callback: CallbackQuery, state: FSMContext):
    """Начать создание заказа"""
    await callback.message.edit_text(
        "📝 <b>Создание индивидуального заказа</b>\n\n"
        "Выберите тип работы:",
        reply_markup=kb.get_order_types_keyboard(),
        parse_mode="HTML"
    )
    await state.set_state(OrderStates.waiting_for_type)
    await callback.answer()


@router.callback_query(OrderStates.waiting_for_type, F.data.startswith("order_type_"))
async def callback_order_type(callback: CallbackQuery, state: FSMContext):
    """Выбран тип заказа"""
    project_type = callback.data.split("_")[-1]
    
    await state.update_data(project_type=project_type)
    
    type_names = {
        'diploma': '🎓 Диплом',
        'coursework': '📖 Курсовая',
        'presentation': '📊 Презентация',
        'project': '💻 Проект'
    }
    
    await callback.message.edit_text(
        f"Тип работы: {type_names.get(project_type, project_type)}\n\n"
        "📝 <b>Опишите детально ваше техническое задание:</b>\n\n"
        "Укажите:\n"
        "• Тему работы\n"
        "• Основные требования\n"
        "• Что должно быть реализовано\n"
        "• Любые важные детали",
        reply_markup=kb.get_back_button("main_menu"),
        parse_mode="HTML"
    )
    await state.set_state(OrderStates.waiting_for_description)
    await callback.answer()


@router.message(OrderStates.waiting_for_description)
async def process_order_description(message: Message, state: FSMContext):
    """Получено описание заказа"""
    await state.update_data(description=message.text)
    
    await message.answer(
        "💻 <b>Укажите языки программирования и технологии:</b>\n\n"
        "Например: Python, Django, PostgreSQL, Docker",
        reply_markup=kb.get_back_button("main_menu"),
        parse_mode="HTML"
    )
    await state.set_state(OrderStates.waiting_for_technologies)


@router.message(OrderStates.waiting_for_technologies)
async def process_order_technologies(message: Message, state: FSMContext):
    """Получены технологии"""
    await state.update_data(technologies=message.text)
    
    await message.answer(
        "📅 <b>Укажите желаемый срок выполнения:</b>\n\n"
        "Например: 2 недели, до 15 декабря, срочно",
        reply_markup=kb.get_skip_button("skip_deadline"),
        parse_mode="HTML"
    )
    await state.set_state(OrderStates.waiting_for_deadline)


@router.message(OrderStates.waiting_for_deadline)
async def process_order_deadline(message: Message, state: FSMContext):
    """Получен срок"""
    await state.update_data(deadline=message.text)
    
    await message.answer(
        "💰 <b>Укажите ваш бюджет:</b>\n\n"
        "Например: до 5000 рублей, договорная",
        reply_markup=kb.get_skip_button("skip_budget"),
        parse_mode="HTML"
    )
    await state.set_state(OrderStates.waiting_for_budget)


@router.callback_query(OrderStates.waiting_for_deadline, F.data == "skip_deadline")
async def skip_deadline(callback: CallbackQuery, state: FSMContext):
    """Пропустить срок"""
    await callback.message.edit_text(
        "💰 <b>Укажите ваш бюджет:</b>\n\n"
        "Например: до 5000 рублей, договорная",
        reply_markup=kb.get_skip_button("skip_budget"),
        parse_mode="HTML"
    )
    await state.set_state(OrderStates.waiting_for_budget)
    await callback.answer()


@router.message(OrderStates.waiting_for_budget)
async def process_order_budget(message: Message, state: FSMContext):
    """Получен бюджет"""
    await state.update_data(budget=message.text)
    
    await message.answer(
        "📞 <b>Укажите контактные данные для связи:</b>\n\n"
        "Например: @username, email, телефон",
        reply_markup=kb.get_skip_button("skip_contact"),
        parse_mode="HTML"
    )
    await state.set_state(OrderStates.waiting_for_contact)


@router.callback_query(OrderStates.waiting_for_budget, F.data == "skip_budget")
async def skip_budget(callback: CallbackQuery, state: FSMContext):
    """Пропустить бюджет"""
    await callback.message.edit_text(
        "📞 <b>Укажите контактные данные для связи:</b>\n\n"
        "Например: @username, email, телефон",
        reply_markup=kb.get_skip_button("skip_contact"),
        parse_mode="HTML"
    )
    await state.set_state(OrderStates.waiting_for_contact)
    await callback.answer()


@router.message(OrderStates.waiting_for_contact)
async def process_order_contact(message: Message, state: FSMContext):
    """Получены контакты"""
    await state.update_data(contact_info=message.text)
    await finalize_order(message, state)


@router.callback_query(OrderStates.waiting_for_contact, F.data == "skip_contact")
async def skip_contact(callback: CallbackQuery, state: FSMContext):
    """Пропустить контакты"""
    await state.update_data(contact_info=None)
    await finalize_order(callback.message, state)
    await callback.answer()


async def finalize_order(message: Message, state: FSMContext):
    """Завершить создание заказа"""
    data = await state.get_data()
    
    # Формируем сводку заказа
    type_names = {
        'diploma': '🎓 Диплом',
        'coursework': '📖 Курсовая',
        'presentation': '📊 Презентация',
        'project': '💻 Проект'
    }
    
    summary = (
        "📝 <b>Подтвердите ваш заказ:</b>\n\n"
        f"<b>Тип работы:</b> {type_names.get(data['project_type'], data['project_type'])}\n\n"
        f"<b>Описание:</b>\n{data['description']}\n\n"
        f"<b>Технологии:</b>\n{data['technologies']}\n\n"
    )
    
    if data.get('deadline'):
        summary += f"<b>Срок:</b> {data['deadline']}\n\n"
    
    if data.get('budget'):
        summary += f"<b>Бюджет:</b> {data['budget']}\n\n"
    
    if data.get('contact_info'):
        summary += f"<b>Контакты:</b> {data['contact_info']}\n\n"
    
    summary += "Подтвердите создание заказа:"
    
    await message.answer(
        summary,
        reply_markup=kb.get_confirm_keyboard("confirm_order", "main_menu"),
        parse_mode="HTML"
    )
    await state.set_state(OrderStates.confirm)


@router.callback_query(OrderStates.confirm, F.data == "confirm_order")
async def callback_confirm_order(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    """Подтверждение создания заказа"""
    data = await state.get_data()
    
    user = await crud.get_user_by_telegram_id(session, callback.from_user.id)
    
    if not user:
        await callback.answer("❌ Ошибка", show_alert=True)
        return
    
    # Создаем заказ
    order = await crud.create_order(
        session,
        user_id=user.id,
        project_type=ProjectType(data['project_type']),
        description=data['description'],
        technologies=data['technologies'],
        deadline=data.get('deadline'),
        budget=data.get('budget'),
        contact_info=data.get('contact_info')
    )
    
    await callback.message.edit_text(
        f"✅ <b>Заказ #{order.id} успешно создан!</b>\n\n"
        "Наши менеджеры свяжутся с вами в ближайшее время.\n"
        "Отслеживайте статус заказа в разделе 'Мои заказы'",
        reply_markup=kb.get_back_button("main_menu"),
        parse_mode="HTML"
    )
    
    await state.clear()
    await callback.answer()

