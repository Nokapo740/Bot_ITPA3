"""
Обработчики админ-панели
"""
from aiogram import Router, F
from aiogram.types import CallbackQuery, Message, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta

from bot.database import crud
from bot.database.models import OrderStatus, ProjectType, ProjectLevel, UserRole
from bot.keyboards import admin as kb_admin
from bot.keyboards import user as kb_user
from bot.states.order import (
    AdminProjectStates, AdminOrderStates, AdminBroadcastStates, AdminCategoryStates
)
from bot.utils.helpers import format_price, format_datetime, get_order_status_text

router = Router()


# Middleware для проверки прав админа
async def check_admin(callback: CallbackQuery, session: AsyncSession) -> bool:
    """Проверка прав администратора"""
    is_admin = await crud.is_admin(session, callback.from_user.id)
    if not is_admin:
        await callback.answer("❌ У вас нет прав администратора", show_alert=True)
        return False
    return True


# ============== ГЛАВНОЕ МЕНЮ АДМИНА ==============

@router.callback_query(F.data == "admin_menu")
async def callback_admin_menu(callback: CallbackQuery, session: AsyncSession):
    """Админ-панель"""
    if not await check_admin(callback, session):
        return
    
    await callback.message.edit_text(
        "🔐 <b>Админ-панель</b>\n\n"
        "Выберите раздел:",
        reply_markup=kb_admin.get_admin_menu(),
        parse_mode="HTML"
    )
    await callback.answer()


# ============== СТАТИСТИКА ==============

@router.callback_query(F.data == "admin_stats")
async def callback_admin_stats(callback: CallbackQuery, session: AsyncSession):
    """Статистика"""
    if not await check_admin(callback, session):
        return
    
    # Получаем статистику
    total_users = await crud.get_users_count(session)
    all_users = await crud.get_all_users(session)
    
    # Новые пользователи за последние 7 дней
    week_ago = datetime.utcnow() - timedelta(days=7)
    new_users = len([u for u in all_users if u.created_at >= week_ago])
    
    # Заблокированные пользователи
    blocked_users = len([u for u in all_users if u.is_blocked])
    
    # Проекты
    projects = await crud.get_all_projects(session, is_active=True, limit=10000)
    total_projects = len(projects)
    
    # Заказы
    new_orders = await crud.get_orders_by_status(session, OrderStatus.NEW)
    
    # Категории
    categories = await crud.get_all_categories(session)
    
    stats_text = (
        "📊 <b>Статистика бота</b>\n\n"
        f"👥 <b>Пользователи:</b>\n"
        f"• Всего: {total_users}\n"
        f"• Новых за неделю: {new_users}\n"
        f"• Заблокировано: {blocked_users}\n\n"
        f"📚 <b>Каталог:</b>\n"
        f"• Проектов: {total_projects}\n"
        f"• Категорий: {len(categories)}\n\n"
        f"📋 <b>Заказы:</b>\n"
        f"• Новых: {len(new_orders)}\n"
    )
    
    await callback.message.edit_text(
        stats_text,
        reply_markup=kb_user.get_back_button("admin_menu"),
        parse_mode="HTML"
    )
    await callback.answer()


# ============== УПРАВЛЕНИЕ КАТАЛОГОМ ==============

@router.callback_query(F.data == "admin_catalog")
async def callback_admin_catalog(callback: CallbackQuery, session: AsyncSession):
    """Меню управления каталогом"""
    if not await check_admin(callback, session):
        return
    
    # Получаем статистику
    projects = await crud.get_all_projects(session, is_active=True, limit=1000)
    total_projects = len(projects)
    
    await callback.message.edit_text(
        "╔═══════════════════════╗\n"
        "   📚 <b>УПРАВЛЕНИЕ КАТАЛОГОМ</b>   \n"
        "╚═══════════════════════╝\n\n"
        f"📊 <b>Проектов в каталоге:</b> {total_projects}\n\n"
        "═══════════════════════\n\n"
        "🎯 <b>Что вы можете сделать:</b>\n\n"
        "➕ <b>Добавить новый проект</b>\n"
        "   └ Создать проект за 8 шагов\n\n"
        "📋 <b>Все проекты</b>\n"
        "   ├ Просмотреть список\n"
        "   ├ Редактировать проект\n"
        "   ├ Изменить цену\n"
        "   ├ Активировать/Деактивировать\n"
        "   └ Удалить проект\n\n"
        "═══════════════════════\n"
        "💡 <i>Выберите действие ниже:</i>",
        reply_markup=kb_admin.get_admin_catalog_menu(),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data == "admin_list_projects")
async def callback_admin_list_projects(callback: CallbackQuery, session: AsyncSession):
    """Список всех проектов"""
    if not await check_admin(callback, session):
        return
    
    projects = await crud.get_all_projects(session, is_active=True, limit=50)
    
    if not projects:
        await callback.message.edit_text(
            "📭 Проектов пока нет",
            reply_markup=kb_user.get_back_button("admin_catalog"),
            parse_mode="HTML"
        )
        await callback.answer()
        return
    
    projects_text = "📚 <b>Список проектов</b>\n\n"
    
    from aiogram.utils.keyboard import InlineKeyboardBuilder
    builder = InlineKeyboardBuilder()
    
    for i, project in enumerate(projects[:20], start=1):
        projects_text += (
            f"{i}. <b>{project.title}</b>\n"
            f"   💰 {format_price(project.price)} | "
            f"👁 {project.views_count} | "
            f"🛒 {project.purchases_count}\n"
            f"   📝 /edit_project_{project.id}\n\n"
        )
        
        builder.row(InlineKeyboardButton(
            text=f"✏️ {i}. {project.title[:30]}...",
            callback_data=f"admin_edit_proj_{project.id}"
        ))
    
    if len(projects) > 20:
        projects_text += f"\n<i>Показаны первые 20 из {len(projects)} проектов</i>"
    
    builder.row(InlineKeyboardButton(text="◀️ Назад", callback_data="admin_catalog"))
    
    await callback.message.edit_text(
        projects_text,
        reply_markup=builder.as_markup(),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data.startswith("admin_edit_proj_"))
async def callback_admin_edit_project_menu(callback: CallbackQuery, session: AsyncSession):
    """Меню редактирования проекта"""
    if not await check_admin(callback, session):
        return
    
    project_id = int(callback.data.split("_")[-1])
    project = await crud.get_project_by_id(session, project_id)
    
    if not project:
        await callback.answer("❌ Проект не найден", show_alert=True)
        return
    
    from aiogram.utils.keyboard import InlineKeyboardBuilder
    builder = InlineKeyboardBuilder()
    
    builder.row(InlineKeyboardButton(text="✏️ Название", callback_data=f"edit_title_{project_id}"))
    builder.row(InlineKeyboardButton(text="📄 Описание", callback_data=f"edit_desc_{project_id}"))
    builder.row(InlineKeyboardButton(text="💰 Цена", callback_data=f"edit_price_{project_id}"))
    builder.row(InlineKeyboardButton(text="💻 Языки", callback_data=f"edit_langs_{project_id}"))
    builder.row(InlineKeyboardButton(text="🔧 Технологии", callback_data=f"edit_tech_{project_id}"))
    builder.row(InlineKeyboardButton(
        text=f"{'🔴 Деактивировать' if project.is_active else '🟢 Активировать'}",
        callback_data=f"toggle_active_{project_id}"
    ))
    builder.row(InlineKeyboardButton(text="🗑 Удалить проект", callback_data=f"delete_proj_{project_id}"))
    builder.row(InlineKeyboardButton(text="◀️ К списку", callback_data="admin_list_projects"))
    
    project_info = (
        f"✏️ <b>Редактирование проекта</b>\n\n"
        f"📝 <b>Название:</b> {project.title}\n"
        f"💰 <b>Цена:</b> {format_price(project.price)}\n"
        f"💻 <b>Языки:</b> {project.programming_languages}\n"
        f"🔧 <b>Технологии:</b> {project.technologies}\n"
        f"📊 <b>Статус:</b> {'🟢 Активен' if project.is_active else '🔴 Неактивен'}\n"
        f"👁 <b>Просмотры:</b> {project.views_count}\n"
        f"🛒 <b>Покупки:</b> {project.purchases_count}\n\n"
        "Выберите что изменить:"
    )
    
    await callback.message.edit_text(
        project_info,
        reply_markup=builder.as_markup(),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data.startswith("edit_title_"))
async def callback_edit_title(callback: CallbackQuery, state: FSMContext):
    """Редактировать название"""
    project_id = int(callback.data.split("_")[-1])
    await state.update_data(edit_project_id=project_id, edit_field='title')
    
    await callback.message.edit_text(
        "✏️ <b>Редактирование названия</b>\n\n"
        "Введите новое название проекта:",
        parse_mode="HTML"
    )
    await state.set_state(AdminProjectStates.edit_waiting_value)
    await callback.answer()


@router.callback_query(F.data.startswith("edit_desc_"))
async def callback_edit_desc(callback: CallbackQuery, state: FSMContext):
    """Редактировать описание"""
    project_id = int(callback.data.split("_")[-1])
    await state.update_data(edit_project_id=project_id, edit_field='description')
    
    await callback.message.edit_text(
        "✏️ <b>Редактирование описания</b>\n\n"
        "Введите новое описание проекта:",
        parse_mode="HTML"
    )
    await state.set_state(AdminProjectStates.edit_waiting_value)
    await callback.answer()


@router.callback_query(F.data.startswith("edit_price_"))
async def callback_edit_price(callback: CallbackQuery, state: FSMContext):
    """Редактировать цену"""
    project_id = int(callback.data.split("_")[-1])
    await state.update_data(edit_project_id=project_id, edit_field='price')
    
    await callback.message.edit_text(
        "💰 <b>Редактирование цены</b>\n\n"
        "Введите новую цену в рублях (например: 5000):",
        parse_mode="HTML"
    )
    await state.set_state(AdminProjectStates.edit_waiting_value)
    await callback.answer()


@router.callback_query(F.data.startswith("edit_langs_"))
async def callback_edit_langs(callback: CallbackQuery, state: FSMContext):
    """Редактировать языки"""
    project_id = int(callback.data.split("_")[-1])
    await state.update_data(edit_project_id=project_id, edit_field='programming_languages')
    
    await callback.message.edit_text(
        "💻 <b>Редактирование языков</b>\n\n"
        "Введите языки программирования (например: Python, JavaScript):",
        parse_mode="HTML"
    )
    await state.set_state(AdminProjectStates.edit_waiting_value)
    await callback.answer()


@router.callback_query(F.data.startswith("edit_tech_"))
async def callback_edit_tech(callback: CallbackQuery, state: FSMContext):
    """Редактировать технологии"""
    project_id = int(callback.data.split("_")[-1])
    await state.update_data(edit_project_id=project_id, edit_field='technologies')
    
    await callback.message.edit_text(
        "🔧 <b>Редактирование технологий</b>\n\n"
        "Введите технологии (например: Django, PostgreSQL):",
        parse_mode="HTML"
    )
    await state.set_state(AdminProjectStates.edit_waiting_value)
    await callback.answer()


@router.message(AdminProjectStates.edit_waiting_value)
async def process_edit_value(message: Message, state: FSMContext, session: AsyncSession):
    """Обработка нового значения"""
    data = await state.get_data()
    project_id = data['edit_project_id']
    field = data['edit_field']
    
    project = await crud.get_project_by_id(session, project_id)
    
    if not project:
        await message.answer("❌ Проект не найден")
        await state.clear()
        return
    
    # Обработка в зависимости от поля
    if field == 'price':
        try:
            new_value = float(message.text.replace(" ", "").replace(",", "."))
            if new_value < 0:
                await message.answer("❌ Цена не может быть отрицательной")
                return
        except ValueError:
            await message.answer("❌ Некорректная цена. Введите число:")
            return
    else:
        new_value = message.text
    
    # Обновляем проект
    await crud.update_project(session, project, **{field: new_value})
    
    field_names = {
        'title': 'название',
        'description': 'описание',
        'price': 'цена',
        'programming_languages': 'языки программирования',
        'technologies': 'технологии'
    }
    
    await message.answer(
        f"✅ <b>Успешно обновлено!</b>\n\n"
        f"Поле '{field_names.get(field, field)}' изменено.",
        parse_mode="HTML"
    )
    
    # Возвращаемся к меню редактирования
    await state.clear()
    
    from aiogram.types import CallbackQuery
    fake_callback = type('obj', (object,), {
        'data': f'admin_edit_proj_{project_id}',
        'message': message,
        'answer': lambda x=None, show_alert=False: None,
        'from_user': message.from_user
    })()
    
    await callback_admin_edit_project_menu(fake_callback, session)


@router.callback_query(F.data.startswith("toggle_active_"))
async def callback_toggle_active(callback: CallbackQuery, session: AsyncSession):
    """Переключить активность проекта"""
    if not await check_admin(callback, session):
        return
    
    project_id = int(callback.data.split("_")[-1])
    project = await crud.get_project_by_id(session, project_id)
    
    if not project:
        await callback.answer("❌ Проект не найден", show_alert=True)
        return
    
    new_status = not project.is_active
    await crud.update_project(session, project, is_active=new_status)
    
    status_text = "🟢 активирован" if new_status else "🔴 деактивирован"
    await callback.answer(f"✅ Проект {status_text}", show_alert=True)
    
    # Обновляем меню
    await callback_admin_edit_project_menu(callback, session)


@router.callback_query(F.data.startswith("delete_proj_"))
async def callback_delete_project_confirm(callback: CallbackQuery, session: AsyncSession):
    """Подтверждение удаления проекта"""
    if not await check_admin(callback, session):
        return
    
    project_id = int(callback.data.split("_")[-1])
    project = await crud.get_project_by_id(session, project_id)
    
    if not project:
        await callback.answer("❌ Проект не найден", show_alert=True)
        return
    
    from aiogram.utils.keyboard import InlineKeyboardBuilder
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="✅ Да, удалить", callback_data=f"confirm_delete_{project_id}"),
        InlineKeyboardButton(text="❌ Отмена", callback_data=f"admin_edit_proj_{project_id}")
    )
    
    await callback.message.edit_text(
        f"⚠️ <b>Подтверждение удаления</b>\n\n"
        f"Вы уверены, что хотите удалить проект?\n\n"
        f"📝 {project.title}\n"
        f"💰 {format_price(project.price)}\n\n"
        f"⚠️ Это действие нельзя отменить!",
        reply_markup=builder.as_markup(),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data.startswith("confirm_delete_"))
async def callback_confirm_delete(callback: CallbackQuery, session: AsyncSession):
    """Удалить проект"""
    if not await check_admin(callback, session):
        return
    
    project_id = int(callback.data.split("_")[-1])
    
    success = await crud.delete_project(session, project_id)
    
    if success:
        await callback.message.edit_text(
            "✅ <b>Проект удален</b>\n\n"
            "Проект успешно удален из каталога.",
            reply_markup=kb_user.get_back_button("admin_catalog"),
            parse_mode="HTML"
        )
        await callback.answer("✅ Удалено")
    else:
        await callback.answer("❌ Ошибка при удалении", show_alert=True)


@router.callback_query(F.data == "admin_add_project")
async def callback_admin_add_project(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    """Добавить проект"""
    if not await check_admin(callback, session):
        return
    
    categories = await crud.get_all_categories(session)
    
    if not categories:
        await callback.message.edit_text(
            "⚠️ <b>Сначала создайте категории!</b>\n\n"
            "Перейдите в раздел 'Категории' и добавьте хотя бы одну категорию.",
            reply_markup=kb_user.get_back_button("admin_catalog"),
            parse_mode="HTML"
        )
        await callback.answer()
        return
    
    await callback.message.edit_text(
        "➕ <b>Добавление проекта</b>\n\n"
        "Шаг 1/8\n\n"
        "📝 Введите <b>название проекта</b>:\n\n"
        "<i>Например: Телеграм-бот для интернет-магазина</i>",
        reply_markup=kb_user.get_back_button("admin_catalog"),
        parse_mode="HTML"
    )
    await state.set_state(AdminProjectStates.waiting_for_title)
    await callback.answer()


@router.message(AdminProjectStates.waiting_for_title)
async def process_project_title(message: Message, state: FSMContext):
    """Получено название проекта"""
    await state.update_data(title=message.text)
    
    await message.answer(
        "➕ <b>Добавление проекта</b>\n\n"
        "Шаг 2/8\n\n"
        "📄 Введите <b>подробное описание</b> проекта:\n\n"
        "<i>Опишите, что делает проект, какие функции реализованы, что входит в комплект.</i>",
        parse_mode="HTML"
    )
    await state.set_state(AdminProjectStates.waiting_for_description)


@router.message(AdminProjectStates.waiting_for_description)
async def process_project_description(message: Message, state: FSMContext, session: AsyncSession):
    """Получено описание"""
    await state.update_data(description=message.text)
    
    # Показываем категории
    categories = await crud.get_all_categories(session)
    
    cat_text = "➕ <b>Добавление проекта</b>\n\nШаг 3/8\n\n📁 Выберите категорию:\n\n"
    
    from aiogram.utils.keyboard import InlineKeyboardBuilder
    builder = InlineKeyboardBuilder()
    
    for cat in categories:
        icon = cat.icon or "📁"
        cat_text += f"{icon} {cat.name} - /cat_{cat.id}\n"
        builder.row(InlineKeyboardButton(
            text=f"{icon} {cat.name}",
            callback_data=f"project_cat_{cat.id}"
        ))
    
    builder.row(InlineKeyboardButton(text="❌ Отмена", callback_data="admin_catalog"))
    
    await message.answer(cat_text, reply_markup=builder.as_markup(), parse_mode="HTML")
    await state.set_state(AdminProjectStates.waiting_for_category)


@router.callback_query(AdminProjectStates.waiting_for_category, F.data.startswith("project_cat_"))
async def process_project_category(callback: CallbackQuery, state: FSMContext):
    """Выбрана категория"""
    category_id = int(callback.data.split("_")[-1])
    await state.update_data(category_id=category_id)
    
    from aiogram.utils.keyboard import InlineKeyboardBuilder
    builder = InlineKeyboardBuilder()
    
    builder.row(InlineKeyboardButton(text="🎓 Диплом", callback_data="project_type_diploma"))
    builder.row(InlineKeyboardButton(text="📖 Курсовая", callback_data="project_type_coursework"))
    builder.row(InlineKeyboardButton(text="📊 Презентация", callback_data="project_type_presentation"))
    builder.row(InlineKeyboardButton(text="💻 Проект", callback_data="project_type_project"))
    builder.row(InlineKeyboardButton(text="❌ Отмена", callback_data="admin_catalog"))
    
    await callback.message.edit_text(
        "➕ <b>Добавление проекта</b>\n\n"
        "Шаг 4/8\n\n"
        "📚 Выберите <b>тип работы</b>:",
        reply_markup=builder.as_markup(),
        parse_mode="HTML"
    )
    await state.set_state(AdminProjectStates.waiting_for_type)
    await callback.answer()


@router.callback_query(AdminProjectStates.waiting_for_type, F.data.startswith("project_type_"))
async def process_project_type(callback: CallbackQuery, state: FSMContext):
    """Выбран тип"""
    project_type = callback.data.split("_")[-1]
    await state.update_data(project_type=project_type)
    
    from aiogram.utils.keyboard import InlineKeyboardBuilder
    builder = InlineKeyboardBuilder()
    
    builder.row(InlineKeyboardButton(text="⭐ Базовый", callback_data="project_level_basic"))
    builder.row(InlineKeyboardButton(text="⭐⭐ Средний", callback_data="project_level_intermediate"))
    builder.row(InlineKeyboardButton(text="⭐⭐⭐ Продвинутый", callback_data="project_level_advanced"))
    builder.row(InlineKeyboardButton(text="❌ Отмена", callback_data="admin_catalog"))
    
    await callback.message.edit_text(
        "➕ <b>Добавление проекта</b>\n\n"
        "Шаг 5/8\n\n"
        "📊 Выберите <b>уровень сложности</b>:",
        reply_markup=builder.as_markup(),
        parse_mode="HTML"
    )
    await state.set_state(AdminProjectStates.waiting_for_level)
    await callback.answer()


@router.callback_query(AdminProjectStates.waiting_for_level, F.data.startswith("project_level_"))
async def process_project_level(callback: CallbackQuery, state: FSMContext):
    """Выбран уровень"""
    level = callback.data.split("_")[-1]
    await state.update_data(level=level)
    
    await callback.message.edit_text(
        "➕ <b>Добавление проекта</b>\n\n"
        "Шаг 6/8\n\n"
        "💻 Введите <b>языки программирования</b>:\n\n"
        "<i>Например: Python, JavaScript\n"
        "Или: C++, Qt</i>",
        parse_mode="HTML"
    )
    await state.set_state(AdminProjectStates.waiting_for_languages)
    await callback.answer()


@router.message(AdminProjectStates.waiting_for_languages)
async def process_project_languages(message: Message, state: FSMContext):
    """Получены языки"""
    await state.update_data(programming_languages=message.text)
    
    await message.answer(
        "➕ <b>Добавление проекта</b>\n\n"
        "Шаг 7/8\n\n"
        "🔧 Введите <b>технологии</b>:\n\n"
        "<i>Например: Django, PostgreSQL, Redis\n"
        "Или: React, Node.js, MongoDB</i>",
        parse_mode="HTML"
    )
    await state.set_state(AdminProjectStates.waiting_for_technologies)


@router.message(AdminProjectStates.waiting_for_technologies)
async def process_project_technologies(message: Message, state: FSMContext):
    """Получены технологии"""
    await state.update_data(technologies=message.text)
    
    await message.answer(
        "➕ <b>Добавление проекта</b>\n\n"
        "Шаг 8/8\n\n"
        "💰 Введите <b>цену в рублях</b>:\n\n"
        "<i>Например: 5000\n"
        "Или: 12500</i>",
        parse_mode="HTML"
    )
    await state.set_state(AdminProjectStates.waiting_for_price)


@router.message(AdminProjectStates.waiting_for_price)
async def process_project_price(message: Message, state: FSMContext):
    """Получена цена"""
    try:
        price = float(message.text.replace(" ", "").replace(",", "."))
        
        if price < 0:
            await message.answer("❌ Цена не может быть отрицательной. Введите корректную цену:")
            return
        
        await state.update_data(price=price)
        
        # Показываем сводку
        data = await state.get_data()
        
        type_names = {
            'diploma': '🎓 Диплом',
            'coursework': '📖 Курсовая',
            'presentation': '📊 Презентация',
            'project': '💻 Проект'
        }
        
        level_names = {
            'basic': '⭐ Базовый',
            'intermediate': '⭐⭐ Средний',
            'advanced': '⭐⭐⭐ Продвинутый'
        }
        
        summary = (
            "✅ <b>Проверьте данные проекта:</b>\n\n"
            f"📝 <b>Название:</b>\n{data['title']}\n\n"
            f"📄 <b>Описание:</b>\n{data['description'][:200]}{'...' if len(data['description']) > 200 else ''}\n\n"
            f"📚 <b>Тип:</b> {type_names.get(data['project_type'], data['project_type'])}\n"
            f"📊 <b>Уровень:</b> {level_names.get(data['level'], data['level'])}\n"
            f"💻 <b>Языки:</b> {data['programming_languages']}\n"
            f"🔧 <b>Технологии:</b> {data['technologies']}\n"
            f"💰 <b>Цена:</b> {format_price(price)}\n\n"
            "Создать проект?"
        )
        
        await message.answer(
            summary,
            reply_markup=kb_user.get_confirm_keyboard("confirm_create_project", "admin_catalog"),
            parse_mode="HTML"
        )
        await state.set_state(AdminProjectStates.confirm)
        
    except ValueError:
        await message.answer("❌ Некорректная цена. Введите число (например: 5000):")


@router.callback_query(AdminProjectStates.confirm, F.data == "confirm_create_project")
async def confirm_create_project(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    """Подтверждение создания проекта"""
    data = await state.get_data()
    
    # Создаем проект
    project = await crud.create_project(
        session,
        title=data['title'],
        description=data['description'],
        category_id=data['category_id'],
        project_type=ProjectType(data['project_type']),
        level=ProjectLevel(data['level']),
        programming_languages=data['programming_languages'],
        technologies=data['technologies'],
        price=data['price'],
        is_active=True
    )
    
    await callback.message.edit_text(
        f"✅ <b>Проект создан!</b>\n\n"
        f"📝 {project.title}\n"
        f"💰 {format_price(project.price)}\n"
        f"🆔 ID: {project.id}\n\n"
        "Проект добавлен в каталог и доступен пользователям.",
        reply_markup=kb_user.get_back_button("admin_catalog"),
        parse_mode="HTML"
    )
    
    await state.clear()
    await callback.answer("✅ Проект создан!")


# ============== УПРАВЛЕНИЕ ЗАКАЗАМИ ==============

@router.callback_query(F.data == "admin_orders")
async def callback_admin_orders(callback: CallbackQuery, session: AsyncSession):
    """Меню заказов"""
    if not await check_admin(callback, session):
        return
    
    await callback.message.edit_text(
        "📋 <b>Управление заказами</b>\n\n"
        "Выберите раздел:",
        reply_markup=kb_admin.get_admin_orders_menu(),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data == "admin_orders_new")
async def callback_admin_orders_new(callback: CallbackQuery, session: AsyncSession):
    """Новые заказы"""
    if not await check_admin(callback, session):
        return
    
    orders = await crud.get_orders_by_status(session, OrderStatus.NEW)
    
    if not orders:
        await callback.message.edit_text(
            "📭 <b>Новых заказов нет</b>",
            reply_markup=kb_user.get_back_button("admin_orders"),
            parse_mode="HTML"
        )
        await callback.answer()
        return
    
    orders_text = "🆕 <b>Новые заказы</b>\n\n"
    
    for i, order in enumerate(orders, start=1):
        user = order.user
        orders_text += (
            f"{i}. <b>Заказ #{order.id}</b>\n"
            f"   👤 {user.first_name} (@{user.username or 'нет'})\n"
            f"   📝 {order.project_type.value}\n"
            f"   📅 {format_datetime(order.created_at)}\n"
            f"   /order_details_{order.id}\n\n"
        )
    
    await callback.message.edit_text(
        orders_text,
        reply_markup=kb_user.get_back_button("admin_orders"),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data == "admin_orders_in_progress")
async def callback_admin_orders_in_progress(callback: CallbackQuery, session: AsyncSession):
    """Заказы в работе"""
    if not await check_admin(callback, session):
        return
    
    orders = await crud.get_orders_by_status(session, OrderStatus.IN_PROGRESS)
    
    if not orders:
        await callback.message.edit_text(
            "📭 <b>Заказов в работе нет</b>",
            reply_markup=kb_user.get_back_button("admin_orders"),
            parse_mode="HTML"
        )
        await callback.answer()
        return
    
    orders_text = "⚙️ <b>Заказы в работе</b>\n\n"
    
    for i, order in enumerate(orders, start=1):
        user = order.user
        orders_text += (
            f"{i}. <b>Заказ #{order.id}</b>\n"
            f"   👤 {user.first_name}\n"
            f"   📝 {order.project_type.value}\n"
            f"   /order_details_{order.id}\n\n"
        )
    
    await callback.message.edit_text(
        orders_text,
        reply_markup=kb_user.get_back_button("admin_orders"),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data == "admin_orders_completed")
async def callback_admin_orders_completed(callback: CallbackQuery, session: AsyncSession):
    """Завершенные заказы"""
    if not await check_admin(callback, session):
        return
    
    orders = await crud.get_orders_by_status(session, OrderStatus.COMPLETED)
    
    if not orders:
        await callback.message.edit_text(
            "📭 <b>Завершенных заказов нет</b>",
            reply_markup=kb_user.get_back_button("admin_orders"),
            parse_mode="HTML"
        )
        await callback.answer()
        return
    
    orders_text = "✅ <b>Завершенные заказы</b>\n\n"
    
    for i, order in enumerate(orders[:20], start=1):  # Показываем последние 20
        user = order.user
        orders_text += (
            f"{i}. <b>Заказ #{order.id}</b>\n"
            f"   👤 {user.first_name}\n"
            f"   📅 {format_datetime(order.completed_at or order.updated_at)}\n\n"
        )
    
    await callback.message.edit_text(
        orders_text,
        reply_markup=kb_user.get_back_button("admin_orders"),
        parse_mode="HTML"
    )
    await callback.answer()


# ============== РАССЫЛКА ==============

@router.callback_query(F.data == "admin_broadcast")
async def callback_admin_broadcast(callback: CallbackQuery, session: AsyncSession):
    """Меню рассылки"""
    if not await check_admin(callback, session):
        return
    
    await callback.message.edit_text(
        "📢 <b>Рассылка</b>\n\n"
        "Выберите действие:",
        reply_markup=kb_admin.get_admin_broadcast_menu(),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data == "admin_create_broadcast")
async def callback_admin_create_broadcast(callback: CallbackQuery, state: FSMContext):
    """Создать рассылку"""
    await callback.message.edit_text(
        "📢 <b>Создание рассылки</b>\n\n"
        "Введите текст сообщения для рассылки:",
        reply_markup=kb_user.get_back_button("admin_broadcast"),
        parse_mode="HTML"
    )
    await state.set_state(AdminBroadcastStates.waiting_for_message)
    await callback.answer()


@router.message(AdminBroadcastStates.waiting_for_message)
async def process_broadcast_message(message: Message, state: FSMContext):
    """Получен текст рассылки"""
    await state.update_data(broadcast_message=message.text)
    
    await message.answer(
        "👥 <b>Выберите целевую аудиторию:</b>",
        reply_markup=kb_admin.get_broadcast_audience_keyboard(),
        parse_mode="HTML"
    )
    await state.set_state(AdminBroadcastStates.waiting_for_audience)


@router.callback_query(AdminBroadcastStates.waiting_for_audience, F.data.startswith("broadcast_audience_"))
async def callback_broadcast_audience(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    """Выбрана аудитория"""
    audience = callback.data.split("_")[-1]
    data = await state.get_data()
    
    # Получаем список пользователей в зависимости от аудитории
    if audience == "all":
        users = await crud.get_all_users(session, is_blocked=False)
        audience_text = "всем пользователям"
    elif audience == "buyers":
        # Пользователи с покупками
        all_users = await crud.get_all_users(session, is_blocked=False)
        users = []
        for user in all_users:
            purchases = await crud.get_user_purchases(session, user.id)
            if purchases:
                users.append(user)
        audience_text = "пользователям с покупками"
    elif audience == "non_buyers":
        # Пользователи без покупок
        all_users = await crud.get_all_users(session, is_blocked=False)
        users = []
        for user in all_users:
            purchases = await crud.get_user_purchases(session, user.id)
            if not purchases:
                users.append(user)
        audience_text = "пользователям без покупок"
    else:
        users = await crud.get_all_users(session, is_blocked=False)
        audience_text = "активным пользователям"
    
    # Создаем рассылку в БД
    broadcast = await crud.create_broadcast(
        session,
        admin_id=callback.from_user.id,
        message=data['broadcast_message'],
        target_audience=audience
    )
    
    # Отправляем рассылку
    from aiogram import Bot
    bot = callback.bot
    
    successful = 0
    failed = 0
    
    for user in users:
        try:
            await bot.send_message(
                user.telegram_id,
                f"📢 <b>Рассылка</b>\n\n{data['broadcast_message']}",
                parse_mode="HTML"
            )
            successful += 1
        except Exception:
            failed += 1
    
    # Обновляем статистику рассылки
    broadcast.total_sent = len(users)
    broadcast.successful = successful
    broadcast.failed = failed
    broadcast.sent_at = datetime.utcnow()
    await session.commit()
    
    await callback.message.edit_text(
        f"✅ <b>Рассылка завершена!</b>\n\n"
        f"📊 <b>Статистика:</b>\n"
        f"• Целевая аудитория: {audience_text}\n"
        f"• Всего: {len(users)}\n"
        f"• Успешно: {successful}\n"
        f"• Ошибок: {failed}",
        reply_markup=kb_user.get_back_button("admin_broadcast"),
        parse_mode="HTML"
    )
    
    await state.clear()
    await callback.answer()


# ============== КАТЕГОРИИ ==============

@router.callback_query(F.data == "admin_categories")
async def callback_admin_categories(callback: CallbackQuery, session: AsyncSession):
    """Меню категорий"""
    if not await check_admin(callback, session):
        return
    
    await callback.message.edit_text(
        "📁 <b>Управление категориями</b>\n\n"
        "Выберите действие:",
        reply_markup=kb_admin.get_admin_categories_menu(),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data == "admin_list_categories")
async def callback_admin_list_categories(callback: CallbackQuery, session: AsyncSession):
    """Список категорий"""
    if not await check_admin(callback, session):
        return
    
    categories = await crud.get_all_categories(session)
    
    if not categories:
        await callback.message.edit_text(
            "📭 <b>Категорий пока нет</b>\n\n"
            "Создайте первую категорию!",
            reply_markup=kb_user.get_back_button("admin_categories"),
            parse_mode="HTML"
        )
        await callback.answer()
        return
    
    categories_text = (
        "╔═══════════════════════╗\n"
        "     📁 <b>СПИСОК КАТЕГОРИЙ</b>     \n"
        "╚═══════════════════════╝\n\n"
    )
    
    from aiogram.utils.keyboard import InlineKeyboardBuilder
    builder = InlineKeyboardBuilder()
    
    for i, category in enumerate(categories, start=1):
        icon = category.icon or "📁"
        categories_text += (
            f"{i}. {icon} <b>{category.name}</b>\n"
            f"   📝 {category.description or 'Без описания'}\n"
            f"   🆔 ID: {category.id}\n\n"
        )
        
        builder.row(InlineKeyboardButton(
            text=f"{icon} {category.name}",
            callback_data=f"admin_edit_cat_{category.id}"
        ))
    
    builder.row(InlineKeyboardButton(text="◀️ Назад", callback_data="admin_categories"))
    
    await callback.message.edit_text(
        categories_text,
        reply_markup=builder.as_markup(),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data == "admin_add_category")
async def callback_admin_add_category(callback: CallbackQuery, state: FSMContext):
    """Добавить категорию"""
    await callback.message.edit_text(
        "➕ <b>Добавление категории</b>\n\n"
        "Шаг 1/3\n\n"
        "📝 Введите название категории:\n\n"
        "<i>Например: Python, JavaScript, Java, C++</i>",
        parse_mode="HTML"
    )
    await state.set_state(AdminCategoryStates.waiting_for_name)
    await callback.answer()


@router.message(AdminCategoryStates.waiting_for_name)
async def process_category_name(message: Message, state: FSMContext):
    """Получено название категории"""
    await state.update_data(name=message.text)
    
    await message.answer(
        "➕ <b>Добавление категории</b>\n\n"
        "Шаг 2/3\n\n"
        "📄 Введите описание (или отправьте '-' чтобы пропустить):\n\n"
        "<i>Например: Проекты на языке Python</i>",
        parse_mode="HTML"
    )
    await state.set_state(AdminCategoryStates.waiting_for_description)


@router.message(AdminCategoryStates.waiting_for_description)
async def process_category_description(message: Message, state: FSMContext):
    """Получено описание"""
    description = None if message.text == '-' else message.text
    await state.update_data(description=description)
    
    await message.answer(
        "➕ <b>Добавление категории</b>\n\n"
        "Шаг 3/3\n\n"
        "😀 Введите эмодзи-иконку (или отправьте '-' чтобы пропустить):\n\n"
        "<i>Например: 🐍 для Python, ☕ для Java, 💻 для Web</i>",
        parse_mode="HTML"
    )
    await state.set_state(AdminCategoryStates.waiting_for_icon)


@router.message(AdminCategoryStates.waiting_for_icon)
async def process_category_icon(message: Message, state: FSMContext):
    """Получена иконка"""
    icon = None if message.text == '-' else message.text
    await state.update_data(icon=icon)
    
    data = await state.get_data()
    
    summary = (
        "✅ <b>Проверьте данные категории:</b>\n\n"
        f"📝 <b>Название:</b> {data['name']}\n"
    )
    
    if data.get('description'):
        summary += f"📄 <b>Описание:</b> {data['description']}\n"
    
    if data.get('icon'):
        summary += f"😀 <b>Иконка:</b> {data['icon']}\n"
    
    summary += "\nСоздать категорию?"
    
    await message.answer(
        summary,
        reply_markup=kb_user.get_confirm_keyboard("confirm_create_category", "admin_categories"),
        parse_mode="HTML"
    )
    await state.set_state(AdminCategoryStates.confirm)


@router.callback_query(AdminCategoryStates.confirm, F.data == "confirm_create_category")
async def confirm_create_category(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    """Подтверждение создания категории"""
    data = await state.get_data()
    
    try:
        category = await crud.create_category(
            session,
            name=data['name'],
            description=data.get('description'),
            icon=data.get('icon')
        )
        
        await callback.message.edit_text(
            f"✅ <b>Категория создана!</b>\n\n"
            f"{category.icon or '📁'} <b>{category.name}</b>\n"
            f"🆔 ID: {category.id}\n\n"
            "Теперь можете создавать проекты в этой категории.",
            reply_markup=kb_user.get_back_button("admin_categories"),
            parse_mode="HTML"
        )
        
    except Exception as e:
        await callback.message.edit_text(
            f"❌ <b>Ошибка создания категории</b>\n\n"
            f"Возможно, такая категория уже существует.\n\n"
            f"Ошибка: {str(e)}",
            reply_markup=kb_user.get_back_button("admin_categories"),
            parse_mode="HTML"
        )
    
    await state.clear()
    await callback.answer()


@router.callback_query(F.data.startswith("admin_edit_cat_"))
async def callback_edit_category(callback: CallbackQuery, session: AsyncSession):
    """Редактировать/удалить категорию"""
    if not await check_admin(callback, session):
        return
    
    category_id = int(callback.data.split("_")[-1])
    category = await crud.get_category_by_id(session, category_id)
    
    if not category:
        await callback.answer("❌ Категория не найдена", show_alert=True)
        return
    
    # Проверяем сколько проектов в категории
    projects = await crud.get_all_projects(session, is_active=True, category_id=category_id, limit=100)
    projects_count = len(projects)
    
    from aiogram.utils.keyboard import InlineKeyboardBuilder
    builder = InlineKeyboardBuilder()
    
    builder.row(InlineKeyboardButton(
        text="🗑 Удалить категорию",
        callback_data=f"delete_cat_{category_id}"
    ))
    builder.row(InlineKeyboardButton(text="◀️ К списку", callback_data="admin_list_categories"))
    
    cat_info = (
        f"╔═══════════════════════╗\n"
        f"     📁 <b>{category.name}</b>     \n"
        f"╚═══════════════════════╝\n\n"
        f"😀 <b>Иконка:</b> {category.icon or 'нет'}\n"
        f"📄 <b>Описание:</b> {category.description or 'нет'}\n"
        f"🆔 <b>ID:</b> {category.id}\n"
        f"📊 <b>Проектов в категории:</b> {projects_count}\n\n"
        f"═══════════════════════\n\n"
        "💡 <i>Примечание: Редактирование категорий пока не реализовано.\n"
        "Вы можете только удалить категорию (если в ней нет проектов).</i>\n\n"
        "Выберите действие:"
    )
    
    await callback.message.edit_text(
        cat_info,
        reply_markup=builder.as_markup(),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data.startswith("delete_cat_"))
async def callback_delete_category(callback: CallbackQuery, session: AsyncSession):
    """Удалить категорию"""
    if not await check_admin(callback, session):
        return
    
    category_id = int(callback.data.split("_")[-1])
    
    from aiogram.utils.keyboard import InlineKeyboardBuilder
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="✅ Да, удалить", callback_data=f"confirm_del_cat_{category_id}"),
        InlineKeyboardButton(text="❌ Отмена", callback_data=f"admin_edit_cat_{category_id}")
    )
    
    await callback.message.edit_text(
        "⚠️ <b>Удаление категории</b>\n\n"
        "Вы уверены? Это удалит категорию, но не проекты в ней.\n\n"
        "⚠️ Действие нельзя отменить!",
        reply_markup=builder.as_markup(),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data.startswith("confirm_del_cat_"))
async def confirm_delete_category(callback: CallbackQuery, session: AsyncSession):
    """Подтверждение удаления категории"""
    if not await check_admin(callback, session):
        return
    
    category_id = int(callback.data.split("_")[-1])
    
    # Проверяем, есть ли проекты в этой категории
    projects = await crud.get_all_projects(session, is_active=True, category_id=category_id, limit=1)
    
    if projects:
        await callback.message.edit_text(
            "⚠️ <b>Невозможно удалить категорию</b>\n\n"
            "В этой категории есть проекты!\n\n"
            "Сначала:\n"
            "1. Удалите все проекты из этой категории\n"
            "2. Или переместите их в другую категорию\n\n"
            "Затем попробуйте удалить категорию снова.",
            reply_markup=kb_user.get_back_button("admin_categories"),
            parse_mode="HTML"
        )
        await callback.answer("❌ В категории есть проекты!", show_alert=True)
        return
    
    success = await crud.delete_category(session, category_id)
    
    if success:
        await callback.message.edit_text(
            "✅ <b>Категория удалена</b>\n\n"
            "Категория успешно удалена из системы.",
            reply_markup=kb_user.get_back_button("admin_categories"),
            parse_mode="HTML"
        )
        await callback.answer("✅ Удалено")
    else:
        await callback.answer("❌ Ошибка при удалении", show_alert=True)


# ============== ПОЛЬЗОВАТЕЛИ ==============

@router.callback_query(F.data == "admin_users")
async def callback_admin_users(callback: CallbackQuery, session: AsyncSession):
    """Меню пользователей"""
    if not await check_admin(callback, session):
        return
    
    await callback.message.edit_text(
        "👥 <b>Управление пользователями</b>\n\n"
        "Выберите действие:",
        reply_markup=kb_admin.get_admin_users_menu(),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data == "admin_list_users")
async def callback_admin_list_users(callback: CallbackQuery, session: AsyncSession):
    """Список пользователей"""
    if not await check_admin(callback, session):
        return
    
    users = await crud.get_all_users(session)
    
    users_text = f"👥 <b>Пользователи ({len(users)})</b>\n\n"
    
    for i, user in enumerate(users[:30], start=1):  # Показываем первых 30
        username = f"@{user.username}" if user.username else "нет"
        users_text += (
            f"{i}. {user.first_name}\n"
            f"   {username} | ID: {user.telegram_id}\n"
            f"   📅 {format_datetime(user.created_at)}\n\n"
        )
    
    if len(users) > 30:
        users_text += f"\n... и еще {len(users) - 30} пользователей"
    
    await callback.message.edit_text(
        users_text,
        reply_markup=kb_user.get_back_button("admin_users"),
        parse_mode="HTML"
    )
    await callback.answer()

