"""
Обработчики каталога проектов
"""
from aiogram import Router, F
from aiogram.types import CallbackQuery, FSInputFile, BufferedInputFile
from sqlalchemy.ext.asyncio import AsyncSession
import os

from bot.database import crud
from bot.database.models import ProjectType
from bot.keyboards import user as kb
from bot.utils.helpers import format_price, get_project_type_emoji, get_level_emoji
from config import settings

router = Router()

ITEMS_PER_PAGE = 5


@router.callback_query(F.data == "catalog")
async def callback_catalog(callback: CallbackQuery):
    """Показать меню каталога"""
    await callback.message.edit_text(
        "╔═══════════════════════╗\n"
        "       🛍 <b>КАТАЛОГ ПРОЕКТОВ</b>       \n"
        "╚═══════════════════════╝\n\n"
        "🎯 <b>Выберите категорию:</b>\n\n"
        "📚 <b>Все проекты</b> — Весь каталог\n"
        "🎓 <b>Дипломы</b> — Дипломные работы\n"
        "📖 <b>Курсовые</b> — Курсовые проекты\n"
        "📊 <b>Презентации</b> — Готовые презентации\n"
        "💻 <b>Проекты</b> — IT-проекты\n\n"
        "═══════════════════════\n"
        "💡 <i>Используйте поиск для быстрого результата!</i>",
        reply_markup=kb.get_catalog_menu(),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data == "catalog_all")
async def callback_catalog_all(callback: CallbackQuery, session: AsyncSession):
    """Показать все проекты"""
    await show_projects_page(callback, session, page=0)


@router.callback_query(F.data.startswith("catalog_type_"))
async def callback_catalog_by_type(callback: CallbackQuery, session: AsyncSession):
    """Показать проекты по типу"""
    project_type = callback.data.split("_")[-1]
    await show_projects_page(callback, session, page=0, project_type=ProjectType(project_type))


@router.callback_query(F.data.startswith("catalog_page_"))
async def callback_catalog_page(callback: CallbackQuery, session: AsyncSession):
    """Пагинация каталога"""
    page = int(callback.data.split("_")[-1])
    await show_projects_page(callback, session, page=page)


@router.callback_query(F.data.startswith("project_"))
async def callback_project_details(callback: CallbackQuery, session: AsyncSession):
    """Показать детали проекта"""
    project_id = int(callback.data.split("_")[1])
    
    project = await crud.get_project_by_id(session, project_id)
    
    if not project:
        await callback.answer("❌ Проект не найден", show_alert=True)
        return
    
    # Увеличиваем счетчик просмотров
    await crud.increment_project_views(session, project_id)
    
    # Проверяем, куплен ли проект
    user = await crud.get_user_by_telegram_id(session, callback.from_user.id)
    is_purchased = await crud.has_user_purchased_project(session, user.id, project_id) if user else False
    
    # Проверяем, есть ли в корзине
    in_cart = False
    if user:
        cart = await crud.get_user_cart(session, user.id)
        in_cart = any(item.project_id == project_id for item in cart)
    
    # Формируем описание проекта
    price_text = format_price(project.discount_price if project.discount_price else project.price)
    if project.discount_price:
        old_price = format_price(project.price)
        price_text = f"<s>{old_price}</s> ➡️ {price_text} 🔥"
    
    # Красивая карточка проекта
    project_text = (
        f"╔═══════════════════════╗\n"
        f"  {get_project_type_emoji(project.project_type.value)} <b>{project.title}</b>\n"
        f"╚═══════════════════════╝\n\n"
        f"📋 <b>Описание:</b>\n"
        f"<i>{project.description}</i>\n\n"
        f"═══════════════════════\n"
        f"📁 <b>Детали проекта:</b>\n\n"
        f"🏷 Категория: <b>{project.category.name}</b>\n"
        f"💻 Языки: <code>{project.programming_languages}</code>\n"
        f"🔧 Технологии: <code>{project.technologies}</code>\n"
        f"📊 Сложность: {get_level_emoji(project.level.value)} <b>{project.level.value.title()}</b>\n\n"
        f"═══════════════════════\n"
        f"💰 <b>ЦЕНА:</b> {price_text}\n"
        f"═══════════════════════\n\n"
        f"📈 <b>Статистика:</b>\n"
        f"👁 Просмотров: {project.views_count}\n"
        f"🛒 Покупок: {project.purchases_count}"
    )
    
    if is_purchased:
        project_text += (
            f"\n\n╔═══════════════════════╗\n"
            f"  ✅ <b>ВЫ УЖЕ ВЛАДЕЕТЕ</b>  \n"
            f"╚═══════════════════════╝"
        )
    
    await callback.message.edit_text(
        project_text,
        reply_markup=kb.get_project_card_keyboard(project_id, in_cart, is_purchased),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data.startswith("add_cart_"))
async def callback_add_to_cart(callback: CallbackQuery, session: AsyncSession):
    """Добавить проект в корзину"""
    project_id = int(callback.data.split("_")[-1])
    
    user = await crud.get_user_by_telegram_id(session, callback.from_user.id)
    
    if not user:
        await callback.answer("❌ Ошибка: пользователь не найден", show_alert=True)
        return
    
    # Проверяем, не куплен ли уже проект
    is_purchased = await crud.has_user_purchased_project(session, user.id, project_id)
    if is_purchased:
        await callback.answer("✅ Вы уже купили этот проект", show_alert=True)
        return
    
    await crud.add_to_cart(session, user.id, project_id)
    
    await callback.answer("✅ Проект добавлен в корзину", show_alert=True)
    
    # Обновляем кнопки
    project = await crud.get_project_by_id(session, project_id)
    if project:
        await callback_project_details(callback, session)


@router.callback_query(F.data.startswith("remove_cart_"))
async def callback_remove_from_cart(callback: CallbackQuery, session: AsyncSession):
    """Удалить проект из корзины"""
    project_id = int(callback.data.split("_")[-1])
    
    user = await crud.get_user_by_telegram_id(session, callback.from_user.id)
    
    if not user:
        await callback.answer("❌ Ошибка: пользователь не найден", show_alert=True)
        return
    
    await crud.remove_from_cart(session, user.id, project_id)
    
    await callback.answer("🗑 Проект удален из корзины")
    
    # Если находимся на странице проекта, обновляем кнопки
    if callback.message.text and "Описание:" in callback.message.text:
        await callback_project_details(callback, session)


async def show_projects_page(
    callback: CallbackQuery,
    session: AsyncSession,
    page: int = 0,
    project_type: ProjectType = None
):
    """Показать страницу с проектами"""
    # Получаем проекты
    projects = await crud.get_all_projects(
        session,
        is_active=True,
        project_type=project_type,
        limit=ITEMS_PER_PAGE,
        offset=page * ITEMS_PER_PAGE
    )
    
    # Получаем общее количество
    total_count = await crud.get_projects_count(
        session,
        is_active=True,
        project_type=project_type
    )
    
    if not projects:
        await callback.message.edit_text(
            "📭 В этой категории пока нет проектов",
            reply_markup=kb.get_back_button("catalog")
        )
        await callback.answer()
        return
    
    total_pages = (total_count + ITEMS_PER_PAGE - 1) // ITEMS_PER_PAGE
    
    # Формируем текст со списком проектов
    projects_text = (
        f"╔═══════════════════════╗\n"
        f"     🛍 <b>КАТАЛОГ ПРОЕКТОВ</b>     \n"
        f"╚═══════════════════════╝\n\n"
        f"📊 Найдено: <b>{total_count}</b> проектов\n"
        f"📄 Страница: <b>{page + 1}</b> из <b>{total_pages}</b>\n\n"
        f"═══════════════════════\n\n"
    )
    
    for i, project in enumerate(projects, start=1):
        price = format_price(project.discount_price if project.discount_price else project.price)
        
        # Добавляем визуальные индикаторы
        popularity = "🔥" if project.purchases_count > 5 else "⭐" if project.purchases_count > 0 else "🆕"
        
        projects_text += (
            f"{popularity} <b>{i}. {project.title}</b>\n"
            f"   {get_project_type_emoji(project.project_type.value)} {project.category.name} | "
            f"{get_level_emoji(project.level.value)}\n"
            f"   💰 <b>{price}</b> | 🛒 {project.purchases_count}\n"
            f"   👉 /project_{project.id}\n\n"
        )
    
    projects_text += (
        f"═══════════════════════\n"
        f"💡 <i>Нажмите на проект для подробностей</i>"
    )
    
    await callback.message.edit_text(
        projects_text,
        reply_markup=kb.get_pagination_keyboard(page, total_pages),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data == "current_page")
async def callback_current_page(callback: CallbackQuery):
    """Текущая страница (ничего не делаем)"""
    await callback.answer()


@router.callback_query(F.data.startswith("download_"))
async def callback_download_project(callback: CallbackQuery, session: AsyncSession):
    """Скачать купленный проект"""
    project_id = int(callback.data.split("_")[-1])
    
    user = await crud.get_user_by_telegram_id(session, callback.from_user.id)
    
    if not user:
        await callback.answer("❌ Ошибка: пользователь не найден", show_alert=True)
        return
    
    # Проверяем, куплен ли проект
    is_purchased = await crud.has_user_purchased_project(session, user.id, project_id)
    if not is_purchased:
        await callback.answer("❌ Вы не приобретали этот проект", show_alert=True)
        return
    
    project = await crud.get_project_by_id(session, project_id)
    
    if not project or not project.file_path:
        await callback.answer("❌ Файл проекта не найден", show_alert=True)
        return
    
    await callback.answer("📥 Подготавливаю файлы...")
    
    # Отправляем файл
    file_path = project.file_path
    if os.path.exists(file_path):
        try:
            document = FSInputFile(file_path)
            await callback.message.answer_document(
                document=document,
                caption=f"📦 {project.title}\n\nСпасибо за покупку! 🎉"
            )
        except Exception as e:
            await callback.message.answer(
                f"❌ Ошибка при отправке файла: {str(e)}\n"
                "Обратитесь в поддержку."
            )
    else:
        await callback.message.answer(
            "❌ Файл не найден на сервере. Обратитесь в поддержку."
        )

