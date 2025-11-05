"""
Модели базы данных
"""
from datetime import datetime
from typing import Optional
from sqlalchemy import String, Integer, Float, DateTime, Text, Boolean, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from enum import Enum
from .engine import Base


class UserRole(str, Enum):
    """Роли пользователей"""
    USER = "user"
    ADMIN = "admin"
    MANAGER = "manager"
    CONTENT_MANAGER = "content_manager"


class OrderStatus(str, Enum):
    """Статусы заказов"""
    NEW = "new"
    UNDER_REVIEW = "under_review"
    ACCEPTED = "accepted"
    IN_PROGRESS = "in_progress"
    READY_FOR_CHECK = "ready_for_check"
    COMPLETED = "completed"
    REJECTED = "rejected"


class ProjectType(str, Enum):
    """Типы проектов"""
    DIPLOMA = "diploma"
    COURSEWORK = "coursework"
    PRESENTATION = "presentation"
    PROJECT = "project"


class ProjectLevel(str, Enum):
    """Уровень сложности проекта"""
    BASIC = "basic"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


class TicketStatus(str, Enum):
    """Статусы тикетов поддержки"""
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    CLOSED = "closed"


# ============== МОДЕЛИ ===============

class User(Base):
    """Пользователь бота"""
    __tablename__ = 'users'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    telegram_id: Mapped[int] = mapped_column(Integer, unique=True, nullable=False, index=True)
    username: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    first_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    last_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    phone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    # Дополнительные поля
    is_blocked: Mapped[bool] = mapped_column(Boolean, default=False)
    referral_code: Mapped[Optional[str]] = mapped_column(String(50), unique=True, nullable=True)
    referred_by: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey('users.id'), nullable=True)
    
    # Временные метки
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Связи
    purchases: Mapped[list["Purchase"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    orders: Mapped[list["Order"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    cart_items: Mapped[list["Cart"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    support_tickets: Mapped[list["SupportTicket"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    reviews: Mapped[list["Review"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User {self.telegram_id} - {self.first_name}>"


class Admin(Base):
    """Администраторы с уровнями доступа"""
    __tablename__ = 'admins'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    telegram_id: Mapped[int] = mapped_column(Integer, unique=True, nullable=False, index=True)
    role: Mapped[UserRole] = mapped_column(SQLEnum(UserRole), default=UserRole.ADMIN)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<Admin {self.telegram_id} - {self.role}>"


class Category(Base):
    """Категории проектов"""
    __tablename__ = 'categories'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    icon: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)  # Эмодзи
    
    # Связи
    projects: Mapped[list["Project"]] = relationship(back_populates="category")
    
    def __repr__(self):
        return f"<Category {self.name}>"


class Project(Base):
    """Готовые проекты в каталоге"""
    __tablename__ = 'projects'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    
    # Классификация
    category_id: Mapped[int] = mapped_column(Integer, ForeignKey('categories.id'), nullable=False)
    project_type: Mapped[ProjectType] = mapped_column(SQLEnum(ProjectType), nullable=False)
    level: Mapped[ProjectLevel] = mapped_column(SQLEnum(ProjectLevel), default=ProjectLevel.BASIC)
    
    # Технологии
    technologies: Mapped[str] = mapped_column(Text, nullable=False)  # Через запятую
    programming_languages: Mapped[str] = mapped_column(String(255), nullable=False)  # Через запятую
    
    # Цена
    price: Mapped[float] = mapped_column(Float, nullable=False)
    discount_price: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # Файлы
    file_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    image_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    demo_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    
    # Статистика
    views_count: Mapped[int] = mapped_column(Integer, default=0)
    purchases_count: Mapped[int] = mapped_column(Integer, default=0)
    
    # Статус
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Связи
    category: Mapped["Category"] = relationship(back_populates="projects")
    purchases: Mapped[list["Purchase"]] = relationship(back_populates="project")
    cart_items: Mapped[list["Cart"]] = relationship(back_populates="project")
    reviews: Mapped[list["Review"]] = relationship(back_populates="project")
    
    def __repr__(self):
        return f"<Project {self.title} - {self.price}₸>"


class Order(Base):
    """Индивидуальные заказы"""
    __tablename__ = 'orders'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'), nullable=False)
    
    # Детали заказа
    project_type: Mapped[ProjectType] = mapped_column(SQLEnum(ProjectType), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    technologies: Mapped[str] = mapped_column(Text, nullable=False)
    deadline: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    budget: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    # Контактные данные
    contact_info: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    # Файлы
    files_path: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON массив путей
    result_files_path: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON массив путей
    
    # Статус и цена
    status: Mapped[OrderStatus] = mapped_column(SQLEnum(OrderStatus), default=OrderStatus.NEW)
    price: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    is_paid: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Комментарии администратора
    admin_comment: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    rejection_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Связи
    user: Mapped["User"] = relationship(back_populates="orders")
    
    def __repr__(self):
        return f"<Order #{self.id} - {self.status}>"


class Purchase(Base):
    """Покупки готовых проектов"""
    __tablename__ = 'purchases'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'), nullable=False)
    project_id: Mapped[int] = mapped_column(Integer, ForeignKey('projects.id'), nullable=False)
    
    price: Mapped[float] = mapped_column(Float, nullable=False)
    payment_method: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    transaction_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Связи
    user: Mapped["User"] = relationship(back_populates="purchases")
    project: Mapped["Project"] = relationship(back_populates="purchases")
    
    def __repr__(self):
        return f"<Purchase #{self.id} - User:{self.user_id} Project:{self.project_id}>"


class Cart(Base):
    """Корзина покупок"""
    __tablename__ = 'cart'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'), nullable=False)
    project_id: Mapped[int] = mapped_column(Integer, ForeignKey('projects.id'), nullable=False)
    
    added_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Связи
    user: Mapped["User"] = relationship(back_populates="cart_items")
    project: Mapped["Project"] = relationship(back_populates="cart_items")
    
    def __repr__(self):
        return f"<Cart User:{self.user_id} Project:{self.project_id}>"


class SupportTicket(Base):
    """Тикеты поддержки"""
    __tablename__ = 'support_tickets'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'), nullable=False)
    
    subject: Mapped[str] = mapped_column(String(255), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[TicketStatus] = mapped_column(SQLEnum(TicketStatus), default=TicketStatus.OPEN)
    
    admin_response: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    closed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Связи
    user: Mapped["User"] = relationship(back_populates="support_tickets")
    
    def __repr__(self):
        return f"<SupportTicket #{self.id} - {self.status}>"


class Broadcast(Base):
    """История рассылок"""
    __tablename__ = 'broadcasts'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    admin_id: Mapped[int] = mapped_column(Integer, nullable=False)
    
    message: Mapped[str] = mapped_column(Text, nullable=False)
    target_audience: Mapped[str] = mapped_column(String(100), default="all")  # all, active, buyers, non_buyers
    
    # Статистика
    total_sent: Mapped[int] = mapped_column(Integer, default=0)
    successful: Mapped[int] = mapped_column(Integer, default=0)
    failed: Mapped[int] = mapped_column(Integer, default=0)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    sent_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    def __repr__(self):
        return f"<Broadcast #{self.id} - {self.total_sent} users>"


class Review(Base):
    """Отзывы и оценки"""
    __tablename__ = 'reviews'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'), nullable=False)
    project_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey('projects.id'), nullable=True)
    
    rating: Mapped[int] = mapped_column(Integer, nullable=False)  # 1-5 звезд
    comment: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Связи
    user: Mapped["User"] = relationship(back_populates="reviews")
    project: Mapped[Optional["Project"]] = relationship(back_populates="reviews")
    
    def __repr__(self):
        return f"<Review #{self.id} - {self.rating}⭐>"

