"""
Основные обработчики команд пользователя
"""
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from bot.database import crud
from bot.keyboards import user as kb
from config import settings

router = Router()


@router.message(Command("start"))
async def cmd_start(message: Message, session: AsyncSession):
    """Обработка команды /start"""
    user = await crud.get_user_by_telegram_id(session, message.from_user.id)
    
    if not user:
        # Регистрация нового пользователя
        user = await crud.create_user(
            session,
            telegram_id=message.from_user.id,
            username=message.from_user.username,
            first_name=message.from_user.first_name,
            last_name=message.from_user.last_name
        )
        
        welcome_text = (
            f"╔═══════════════════════╗\n"
            f"    👋 <b>ДОБРО ПОЖАЛОВАТЬ!</b>    \n"
            f"╚═══════════════════════╝\n\n"
            f"Привет, <b>{message.from_user.first_name}</b>! 🎉\n\n"
            f"🎓 <b>Я — ваш помощник по учебным проектам!</b>\n\n"
            f"═══════════════════════\n"
            f"✨ <b>Что я могу:</b>\n\n"
            f"🛍 <b>Готовые проекты</b>\n"
            f"   ├ Дипломы\n"
            f"   ├ Курсовые\n"
            f"   ├ Презентации\n"
            f"   └ IT-проекты\n\n"
            f"📝 <b>Индивидуальные заказы</b>\n"
            f"   └ Разработка под ваши требования\n\n"
            f"💬 <b>Поддержка 24/7</b>\n"
            f"   └ Всегда на связи!\n"
            f"═══════════════════════\n\n"
            f"⬇️ Выберите раздел в меню ниже:"
        )
    else:
        # Получаем немного статистики для персонализации
        purchases = await crud.get_user_purchases(session, user.id)
        orders = await crud.get_user_orders(session, user.id)
        
        welcome_text = (
            f"╔═══════════════════════╗\n"
            f"     🎯 <b>С ВОЗВРАЩЕНИЕМ!</b>     \n"
            f"╚═══════════════════════╝\n\n"
            f"Рады видеть вас снова, <b>{user.first_name}</b>! 👋\n\n"
        )
        
        if purchases or orders:
            welcome_text += f"📊 <b>Ваша активность:</b>\n"
            if purchases:
                welcome_text += f"   💎 Покупок: {len(purchases)}\n"
            if orders:
                welcome_text += f"   📝 Заказов: {len(orders)}\n"
            welcome_text += "\n"
        
        welcome_text += (
            f"═══════════════════════\n"
            f"💡 <b>Чем могу помочь сегодня?</b>\n"
            f"═══════════════════════\n\n"
            f"⬇️ Выберите действие:"
        )
    
    await message.answer(welcome_text, reply_markup=kb.get_main_menu(), parse_mode="HTML")


@router.message(Command("menu"))
async def cmd_menu(message: Message):
    """Показать главное меню"""
    await message.answer("📋 Главное меню:", reply_markup=kb.get_main_menu())


@router.message(Command("admin"))
async def cmd_admin(message: Message, session: AsyncSession):
    """Админ-панель"""
    is_admin = await crud.is_admin(session, message.from_user.id)
    
    if not is_admin and message.from_user.id not in settings.admin_list:
        await message.answer("❌ У вас нет доступа к админ-панели")
        return
    
    # Если админа нет в БД, добавляем
    if message.from_user.id in settings.admin_list and not is_admin:
        from bot.database.models import UserRole
        await crud.create_admin(session, message.from_user.id, UserRole.ADMIN)
    
    from bot.keyboards.admin import get_admin_menu
    await message.answer("🔐 Админ-панель", reply_markup=get_admin_menu())


@router.callback_query(F.data == "main_menu")
async def callback_main_menu(callback: CallbackQuery, state: FSMContext):
    """Возврат в главное меню"""
    await state.clear()
    
    await callback.message.edit_text(
        "📋 Главное меню:",
        reply_markup=kb.get_main_menu()
    )
    await callback.answer()


@router.callback_query(F.data == "cancel")
async def callback_cancel(callback: CallbackQuery, state: FSMContext):
    """Отмена текущего действия"""
    await state.clear()
    
    await callback.message.edit_text(
        "❌ Действие отменено\n\n📋 Главное меню:",
        reply_markup=kb.get_main_menu()
    )
    await callback.answer()


@router.message(Command("help"))
async def cmd_help(message: Message):
    """Помощь"""
    help_text = (
        "📖 <b>Справка по боту</b>\n\n"
        "<b>Основные команды:</b>\n"
        "/start - Начать работу с ботом\n"
        "/menu - Показать главное меню\n"
        "/help - Справка\n"
        "/admin - Админ-панель (для администраторов)\n\n"
        "<b>Основные функции:</b>\n\n"
        "🛍 <b>Каталог проектов</b>\n"
        "Готовые работы по различным дисциплинам и языкам программирования\n\n"
        "📝 <b>Заказать проект</b>\n"
        "Индивидуальный заказ под ваши требования\n\n"
        "🛒 <b>Корзина</b>\n"
        "Добавляйте проекты и оформляйте заказ\n\n"
        "📦 <b>Мои заказы</b>\n"
        "История покупок и статус индивидуальных заказов\n\n"
        "👤 <b>Профиль</b>\n"
        "Ваши данные и статистика\n\n"
        "💬 <b>Поддержка</b>\n"
        "Свяжитесь с нами по любым вопросам\n\n"
        "❓ Возникли вопросы? Обратитесь в поддержку!"
    )
    
    await message.answer(help_text, parse_mode="HTML")

