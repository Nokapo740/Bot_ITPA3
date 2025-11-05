"""
Обработчики поддержки
"""
from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from bot.database import crud
from bot.keyboards import user as kb
from bot.states.order import SupportStates
from bot.utils.helpers import format_datetime

router = Router()


@router.callback_query(F.data == "support")
async def callback_support(callback: CallbackQuery):
    """Меню поддержки"""
    await callback.message.edit_text(
        "💬 <b>Поддержка</b>\n\n"
        "Выберите действие:",
        reply_markup=kb.get_support_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data == "faq")
async def callback_faq(callback: CallbackQuery):
    """FAQ"""
    faq_text = (
        "❓ <b>Часто задаваемые вопросы</b>\n\n"
        "<b>1. Как купить проект?</b>\n"
        "Выберите проект в каталоге, добавьте в корзину и оформите заказ.\n\n"
        "<b>2. Как заказать индивидуальный проект?</b>\n"
        "Нажмите 'Заказать проект' в главном меню и заполните форму.\n\n"
        "<b>3. Сколько времени займет выполнение?</b>\n"
        "Зависит от сложности проекта. Обычно 3-7 дней.\n\n"
        "<b>4. Можно ли внести изменения в готовый проект?</b>\n"
        "Да, мы предоставляем поддержку и правки после покупки.\n\n"
        "<b>5. Как связаться с поддержкой?</b>\n"
        "Создайте обращение через бота или напишите напрямую.\n\n"
        "<b>6. Какие способы оплаты доступны?</b>\n"
        "Банковские карты, электронные кошельки, криптовалюта.\n\n"
        "Не нашли ответ? Создайте обращение в поддержку!"
    )
    
    await callback.message.edit_text(
        faq_text,
        reply_markup=kb.get_back_button("support"),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data == "create_ticket")
async def callback_create_ticket(callback: CallbackQuery, state: FSMContext):
    """Создать обращение"""
    await callback.message.edit_text(
        "📝 <b>Создание обращения</b>\n\n"
        "Введите тему обращения:",
        reply_markup=kb.get_back_button("support"),
        parse_mode="HTML"
    )
    await state.set_state(SupportStates.waiting_for_subject)
    await callback.answer()


@router.message(SupportStates.waiting_for_subject)
async def process_ticket_subject(message: Message, state: FSMContext):
    """Получена тема"""
    await state.update_data(subject=message.text)
    
    await message.answer(
        "💬 <b>Опишите вашу проблему или вопрос:</b>\n\n"
        "Чем подробнее вы опишете ситуацию, тем быстрее мы сможем помочь.",
        reply_markup=kb.get_back_button("support"),
        parse_mode="HTML"
    )
    await state.set_state(SupportStates.waiting_for_message)


@router.message(SupportStates.waiting_for_message)
async def process_ticket_message(message: Message, state: FSMContext, session: AsyncSession):
    """Получено сообщение"""
    data = await state.get_data()
    
    user = await crud.get_user_by_telegram_id(session, message.from_user.id)
    
    if not user:
        await message.answer("❌ Ошибка")
        await state.clear()
        return
    
    # Создаем тикет
    ticket = await crud.create_support_ticket(
        session,
        user_id=user.id,
        subject=data['subject'],
        message=message.text
    )
    
    await message.answer(
        f"✅ <b>Обращение #{ticket.id} создано!</b>\n\n"
        "Наши специалисты ответят вам в ближайшее время.\n"
        "Проверить статус можно в разделе 'Мои обращения'",
        reply_markup=kb.get_back_button("support"),
        parse_mode="HTML"
    )
    
    await state.clear()


@router.callback_query(F.data == "my_tickets")
async def callback_my_tickets(callback: CallbackQuery, session: AsyncSession):
    """Мои обращения"""
    user = await crud.get_user_by_telegram_id(session, callback.from_user.id)
    
    if not user:
        await callback.answer("❌ Ошибка", show_alert=True)
        return
    
    tickets = await crud.get_user_tickets(session, user.id)
    
    if not tickets:
        await callback.message.edit_text(
            "📭 <b>У вас пока нет обращений</b>\n\n"
            "Создайте обращение, если у вас есть вопросы!",
            reply_markup=kb.get_back_button("support"),
            parse_mode="HTML"
        )
        await callback.answer()
        return
    
    tickets_text = "📋 <b>Мои обращения</b>\n\n"
    
    status_emoji = {
        'open': '🔓',
        'in_progress': '⚙️',
        'closed': '✅'
    }
    
    status_names = {
        'open': 'Открыто',
        'in_progress': 'В работе',
        'closed': 'Закрыто'
    }
    
    for i, ticket in enumerate(tickets, start=1):
        emoji = status_emoji.get(ticket.status.value, '❓')
        status_name = status_names.get(ticket.status.value, ticket.status.value)
        
        tickets_text += (
            f"{i}. <b>{ticket.subject}</b>\n"
            f"   {emoji} {status_name}\n"
            f"   📅 {format_datetime(ticket.created_at)}\n"
        )
        
        if ticket.admin_response:
            tickets_text += f"   💬 Есть ответ\n"
        
        tickets_text += "\n"
    
    await callback.message.edit_text(
        tickets_text,
        reply_markup=kb.get_back_button("support"),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data.startswith("support_order_"))
async def callback_support_order(callback: CallbackQuery, state: FSMContext):
    """Поддержка по конкретному заказу"""
    order_id = callback.data.split("_")[-1]
    
    await state.update_data(order_id=order_id)
    await callback_create_ticket(callback, state)

