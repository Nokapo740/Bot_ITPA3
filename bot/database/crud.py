"""
CRUD операции для работы с базой данных
"""
from typing import Optional, List
from sqlalchemy import select, func, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from .models import (
    User, Admin, Category, Project, Order, Purchase, 
    Cart, SupportTicket, Broadcast, Review,
    OrderStatus, ProjectType, TicketStatus, UserRole
)


# ============== USER ==============

async def get_user_by_telegram_id(session: AsyncSession, telegram_id: int) -> Optional[User]:
    """Получить пользователя по telegram_id"""
    result = await session.execute(
        select(User).where(User.telegram_id == telegram_id)
    )
    return result.scalar_one_or_none()


async def create_user(session: AsyncSession, telegram_id: int, **kwargs) -> User:
    """Создать нового пользователя"""
    user = User(telegram_id=telegram_id, **kwargs)
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


async def update_user(session: AsyncSession, user: User, **kwargs) -> User:
    """Обновить данные пользователя"""
    for key, value in kwargs.items():
        setattr(user, key, value)
    await session.commit()
    await session.refresh(user)
    return user


async def get_all_users(session: AsyncSession, is_blocked: Optional[bool] = None) -> List[User]:
    """Получить всех пользователей"""
    query = select(User)
    if is_blocked is not None:
        query = query.where(User.is_blocked == is_blocked)
    result = await session.execute(query)
    return list(result.scalars().all())


async def get_users_count(session: AsyncSession) -> int:
    """Получить количество пользователей"""
    result = await session.execute(select(func.count(User.id)))
    return result.scalar_one()


# ============== ADMIN ==============

async def is_admin(session: AsyncSession, telegram_id: int) -> bool:
    """Проверить, является ли пользователь администратором"""
    result = await session.execute(
        select(Admin).where(Admin.telegram_id == telegram_id)
    )
    return result.scalar_one_or_none() is not None


async def get_admin(session: AsyncSession, telegram_id: int) -> Optional[Admin]:
    """Получить администратора"""
    result = await session.execute(
        select(Admin).where(Admin.telegram_id == telegram_id)
    )
    return result.scalar_one_or_none()


async def create_admin(session: AsyncSession, telegram_id: int, role: UserRole) -> Admin:
    """Создать администратора"""
    admin = Admin(telegram_id=telegram_id, role=role)
    session.add(admin)
    await session.commit()
    await session.refresh(admin)
    return admin


# ============== CATEGORY ==============

async def get_all_categories(session: AsyncSession) -> List[Category]:
    """Получить все категории"""
    result = await session.execute(select(Category))
    return list(result.scalars().all())


async def get_category_by_id(session: AsyncSession, category_id: int) -> Optional[Category]:
    """Получить категорию по ID"""
    result = await session.execute(
        select(Category).where(Category.id == category_id)
    )
    return result.scalar_one_or_none()


async def create_category(session: AsyncSession, name: str, **kwargs) -> Category:
    """Создать категорию"""
    category = Category(name=name, **kwargs)
    session.add(category)
    await session.commit()
    await session.refresh(category)
    return category


async def delete_category(session: AsyncSession, category_id: int) -> bool:
    """Удалить категорию"""
    category = await get_category_by_id(session, category_id)
    if category:
        await session.delete(category)
        await session.commit()
        return True
    return False


# ============== PROJECT ==============

async def get_all_projects(
    session: AsyncSession, 
    is_active: bool = True,
    category_id: Optional[int] = None,
    project_type: Optional[ProjectType] = None,
    limit: int = 10,
    offset: int = 0
) -> List[Project]:
    """Получить все проекты с фильтрами"""
    query = select(Project).where(Project.is_active == is_active)
    
    if category_id:
        query = query.where(Project.category_id == category_id)
    if project_type:
        query = query.where(Project.project_type == project_type)
    
    query = query.options(selectinload(Project.category))
    query = query.limit(limit).offset(offset)
    
    result = await session.execute(query)
    return list(result.scalars().all())


async def get_projects_count(
    session: AsyncSession,
    is_active: bool = True,
    category_id: Optional[int] = None,
    project_type: Optional[ProjectType] = None
) -> int:
    """Получить количество проектов"""
    query = select(func.count(Project.id)).where(Project.is_active == is_active)
    
    if category_id:
        query = query.where(Project.category_id == category_id)
    if project_type:
        query = query.where(Project.project_type == project_type)
    
    result = await session.execute(query)
    return result.scalar_one()


async def get_project_by_id(session: AsyncSession, project_id: int) -> Optional[Project]:
    """Получить проект по ID"""
    result = await session.execute(
        select(Project)
        .where(Project.id == project_id)
        .options(selectinload(Project.category))
    )
    return result.scalar_one_or_none()


async def create_project(session: AsyncSession, **kwargs) -> Project:
    """Создать проект"""
    project = Project(**kwargs)
    session.add(project)
    await session.commit()
    await session.refresh(project)
    return project


async def update_project(session: AsyncSession, project: Project, **kwargs) -> Project:
    """Обновить проект"""
    for key, value in kwargs.items():
        setattr(project, key, value)
    await session.commit()
    await session.refresh(project)
    return project


async def delete_project(session: AsyncSession, project_id: int) -> bool:
    """Удалить проект"""
    project = await get_project_by_id(session, project_id)
    if project:
        await session.delete(project)
        await session.commit()
        return True
    return False


async def increment_project_views(session: AsyncSession, project_id: int):
    """Увеличить счетчик просмотров проекта"""
    project = await get_project_by_id(session, project_id)
    if project:
        project.views_count += 1
        await session.commit()


# ============== CART ==============

async def get_user_cart(session: AsyncSession, user_id: int) -> List[Cart]:
    """Получить корзину пользователя"""
    result = await session.execute(
        select(Cart)
        .where(Cart.user_id == user_id)
        .options(selectinload(Cart.project))
    )
    return list(result.scalars().all())


async def add_to_cart(session: AsyncSession, user_id: int, project_id: int) -> Cart:
    """Добавить проект в корзину"""
    # Проверяем, нет ли уже этого проекта в корзине
    result = await session.execute(
        select(Cart).where(
            and_(Cart.user_id == user_id, Cart.project_id == project_id)
        )
    )
    existing = result.scalar_one_or_none()
    
    if existing:
        return existing
    
    cart_item = Cart(user_id=user_id, project_id=project_id)
    session.add(cart_item)
    await session.commit()
    await session.refresh(cart_item)
    return cart_item


async def remove_from_cart(session: AsyncSession, user_id: int, project_id: int) -> bool:
    """Удалить проект из корзины"""
    result = await session.execute(
        select(Cart).where(
            and_(Cart.user_id == user_id, Cart.project_id == project_id)
        )
    )
    cart_item = result.scalar_one_or_none()
    
    if cart_item:
        await session.delete(cart_item)
        await session.commit()
        return True
    return False


async def clear_cart(session: AsyncSession, user_id: int):
    """Очистить корзину"""
    result = await session.execute(
        select(Cart).where(Cart.user_id == user_id)
    )
    cart_items = result.scalars().all()
    
    for item in cart_items:
        await session.delete(item)
    
    await session.commit()


# ============== ORDER ==============

async def create_order(session: AsyncSession, user_id: int, **kwargs) -> Order:
    """Создать заказ"""
    order = Order(user_id=user_id, **kwargs)
    session.add(order)
    await session.commit()
    await session.refresh(order)
    return order


async def get_order_by_id(session: AsyncSession, order_id: int) -> Optional[Order]:
    """Получить заказ по ID"""
    result = await session.execute(
        select(Order)
        .where(Order.id == order_id)
        .options(selectinload(Order.user))
    )
    return result.scalar_one_or_none()


async def get_user_orders(session: AsyncSession, user_id: int) -> List[Order]:
    """Получить все заказы пользователя"""
    result = await session.execute(
        select(Order)
        .where(Order.user_id == user_id)
        .order_by(Order.created_at.desc())
    )
    return list(result.scalars().all())


async def get_orders_by_status(session: AsyncSession, status: OrderStatus) -> List[Order]:
    """Получить заказы по статусу"""
    result = await session.execute(
        select(Order)
        .where(Order.status == status)
        .options(selectinload(Order.user))
        .order_by(Order.created_at.desc())
    )
    return list(result.scalars().all())


async def update_order_status(
    session: AsyncSession, 
    order_id: int, 
    status: OrderStatus,
    **kwargs
) -> Optional[Order]:
    """Обновить статус заказа"""
    order = await get_order_by_id(session, order_id)
    if order:
        order.status = status
        for key, value in kwargs.items():
            setattr(order, key, value)
        await session.commit()
        await session.refresh(order)
    return order


# ============== PURCHASE ==============

async def create_purchase(
    session: AsyncSession,
    user_id: int,
    project_id: int,
    price: float,
    **kwargs
) -> Purchase:
    """Создать покупку"""
    purchase = Purchase(
        user_id=user_id,
        project_id=project_id,
        price=price,
        **kwargs
    )
    session.add(purchase)
    
    # Увеличиваем счетчик покупок проекта
    project = await get_project_by_id(session, project_id)
    if project:
        project.purchases_count += 1
    
    await session.commit()
    await session.refresh(purchase)
    return purchase


async def get_user_purchases(session: AsyncSession, user_id: int) -> List[Purchase]:
    """Получить все покупки пользователя"""
    result = await session.execute(
        select(Purchase)
        .where(Purchase.user_id == user_id)
        .options(selectinload(Purchase.project))
        .order_by(Purchase.created_at.desc())
    )
    return list(result.scalars().all())


async def has_user_purchased_project(
    session: AsyncSession,
    user_id: int,
    project_id: int
) -> bool:
    """Проверить, купил ли пользователь проект"""
    result = await session.execute(
        select(Purchase).where(
            and_(Purchase.user_id == user_id, Purchase.project_id == project_id)
        )
    )
    return result.scalar_one_or_none() is not None


# ============== SUPPORT TICKET ==============

async def create_support_ticket(
    session: AsyncSession,
    user_id: int,
    subject: str,
    message: str
) -> SupportTicket:
    """Создать тикет поддержки"""
    ticket = SupportTicket(user_id=user_id, subject=subject, message=message)
    session.add(ticket)
    await session.commit()
    await session.refresh(ticket)
    return ticket


async def get_user_tickets(session: AsyncSession, user_id: int) -> List[SupportTicket]:
    """Получить тикеты пользователя"""
    result = await session.execute(
        select(SupportTicket)
        .where(SupportTicket.user_id == user_id)
        .order_by(SupportTicket.created_at.desc())
    )
    return list(result.scalars().all())


async def get_ticket_by_id(session: AsyncSession, ticket_id: int) -> Optional[SupportTicket]:
    """Получить тикет по ID"""
    result = await session.execute(
        select(SupportTicket)
        .where(SupportTicket.id == ticket_id)
        .options(selectinload(SupportTicket.user))
    )
    return result.scalar_one_or_none()


# ============== BROADCAST ==============

async def create_broadcast(
    session: AsyncSession,
    admin_id: int,
    message: str,
    target_audience: str = "all"
) -> Broadcast:
    """Создать рассылку"""
    broadcast = Broadcast(
        admin_id=admin_id,
        message=message,
        target_audience=target_audience
    )
    session.add(broadcast)
    await session.commit()
    await session.refresh(broadcast)
    return broadcast

