"""
Обработчики корзины покупок
"""
from aiogram import Router, F
from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from bot.database import crud
from bot.keyboards import user as kb
from bot.utils.helpers import format_price

router = Router()


@router.callback_query(F.data == "cart")
async def callback_cart(callback: CallbackQuery, session: AsyncSession):
    """Показать корзину"""
    user = await crud.get_user_by_telegram_id(session, callback.from_user.id)
    
    if not user:
        await callback.answer("❌ Ошибка: пользователь не найден", show_alert=True)
        return
    
    cart_items = await crud.get_user_cart(session, user.id)
    
    if not cart_items:
        await callback.message.edit_text(
            "🛒 <b>Ваша корзина пуста</b>\n\n"
            "Добавьте проекты из каталога!",
            reply_markup=kb.get_cart_keyboard(has_items=False),
            parse_mode="HTML"
        )
        await callback.answer()
        return
    
    # Формируем текст корзины
    cart_text = "🛒 <b>Ваша корзина</b>\n\n"
    total_price = 0
    
    for i, item in enumerate(cart_items, start=1):
        project = item.project
        price = project.discount_price if project.discount_price else project.price
        total_price += price
        
        cart_text += (
            f"{i}. <b>{project.title}</b>\n"
            f"   💰 {format_price(price)}\n"
            f"   /project_{project.id}\n\n"
        )
    
    cart_text += f"\n💳 <b>Итого:</b> {format_price(total_price)}"
    
    await callback.message.edit_text(
        cart_text,
        reply_markup=kb.get_cart_keyboard(has_items=True),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data == "clear_cart")
async def callback_clear_cart(callback: CallbackQuery, session: AsyncSession):
    """Очистить корзину"""
    user = await crud.get_user_by_telegram_id(session, callback.from_user.id)
    
    if not user:
        await callback.answer("❌ Ошибка", show_alert=True)
        return
    
    await crud.clear_cart(session, user.id)
    
    await callback.message.edit_text(
        "🗑 <b>Корзина очищена</b>\n\n"
        "Добавьте новые проекты из каталога!",
        reply_markup=kb.get_cart_keyboard(has_items=False),
        parse_mode="HTML"
    )
    await callback.answer("🗑 Корзина очищена")


@router.callback_query(F.data == "checkout")
async def callback_checkout(callback: CallbackQuery, session: AsyncSession):
    """Оформление заказа"""
    user = await crud.get_user_by_telegram_id(session, callback.from_user.id)
    
    if not user:
        await callback.answer("❌ Ошибка", show_alert=True)
        return
    
    cart_items = await crud.get_user_cart(session, user.id)
    
    if not cart_items:
        await callback.answer("🛒 Корзина пуста", show_alert=True)
        return
    
    # Здесь будет интеграция с платежной системой
    # Пока просто имитируем покупку
    
    total_price = 0
    purchased_projects = []
    
    for item in cart_items:
        project = item.project
        price = project.discount_price if project.discount_price else project.price
        total_price += price
        
        # Создаем покупку
        await crud.create_purchase(
            session,
            user_id=user.id,
            project_id=project.id,
            price=price,
            payment_method="test"
        )
        
        purchased_projects.append(project.title)
    
    # Очищаем корзину
    await crud.clear_cart(session, user.id)
    
    success_text = (
        "✅ <b>Оплата прошла успешно!</b>\n\n"
        f"💰 Сумма: {format_price(total_price)}\n\n"
        "<b>Приобретенные проекты:</b>\n"
    )
    
    for i, title in enumerate(purchased_projects, start=1):
        success_text += f"{i}. {title}\n"
    
    success_text += (
        "\n📦 Скачать проекты можно в разделе 'Мои заказы'\n"
        "Спасибо за покупку! 🎉"
    )
    
    await callback.message.edit_text(
        success_text,
        reply_markup=kb.get_back_button("main_menu"),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data.startswith("buy_now_"))
async def callback_buy_now(callback: CallbackQuery, session: AsyncSession):
    """Купить проект сразу"""
    project_id = int(callback.data.split("_")[-1])
    
    user = await crud.get_user_by_telegram_id(session, callback.from_user.id)
    
    if not user:
        await callback.answer("❌ Ошибка", show_alert=True)
        return
    
    project = await crud.get_project_by_id(session, project_id)
    
    if not project:
        await callback.answer("❌ Проект не найден", show_alert=True)
        return
    
    # Проверяем, не куплен ли уже
    is_purchased = await crud.has_user_purchased_project(session, user.id, project_id)
    if is_purchased:
        await callback.answer("✅ Вы уже купили этот проект", show_alert=True)
        return
    
    # Здесь должна быть интеграция с платежной системой
    # Пока просто имитируем покупку
    
    price = project.discount_price if project.discount_price else project.price
    
    await crud.create_purchase(
        session,
        user_id=user.id,
        project_id=project_id,
        price=price,
        payment_method="test"
    )
    
    success_text = (
        "✅ <b>Оплата прошла успешно!</b>\n\n"
        f"📦 Проект: {project.title}\n"
        f"💰 Сумма: {format_price(price)}\n\n"
        "📥 Вы можете скачать проект прямо сейчас или в разделе 'Мои заказы'\n"
        "Спасибо за покупку! 🎉"
    )
    
    from bot.keyboards.user import InlineKeyboardBuilder, InlineKeyboardButton
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="📥 Скачать", callback_data=f"download_{project_id}"))
    builder.row(InlineKeyboardButton(text="📦 Мои заказы", callback_data="my_purchases"))
    builder.row(InlineKeyboardButton(text="◀️ Главное меню", callback_data="main_menu"))
    
    await callback.message.edit_text(
        success_text,
        reply_markup=builder.as_markup(),
        parse_mode="HTML"
    )
    await callback.answer()

