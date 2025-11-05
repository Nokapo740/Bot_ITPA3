# 👨‍💻 Руководство разработчика

Краткая шпаргалка для работы с проектом.

## 🚀 Быстрые команды

```bash
# Активация виртуального окружения
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Запуск бота
python main.py

# Добавление тестовых данных
python add_sample_data.py

# Установка зависимостей
pip install -r requirements.txt

# Деактивация окружения
deactivate
```

## 📝 Частые задачи

### Добавить нового администратора

**Способ 1: Через .env**
```env
ADMIN_IDS=123456789,987654321,111222333
```

**Способ 2: Через код**
```python
from bot.database import crud
from bot.database.models import UserRole

async with async_session_maker() as session:
    await crud.create_admin(session, telegram_id=123456789, role=UserRole.ADMIN)
```

### Добавить категорию

```python
from bot.database import crud

async with async_session_maker() as session:
    category = await crud.create_category(
        session,
        name="PHP",
        description="Проекты на PHP",
        icon="🐘"
    )
```

### Добавить проект

```python
from bot.database import crud
from bot.database.models import ProjectType, ProjectLevel

async with async_session_maker() as session:
    project = await crud.create_project(
        session,
        title="Название проекта",
        description="Подробное описание",
        category_id=1,  # ID категории
        project_type=ProjectType.PROJECT,
        level=ProjectLevel.INTERMEDIATE,
        technologies="Django, PostgreSQL, Redis",
        programming_languages="Python",
        price=5000.0,
        is_active=True
    )
```

### Получить всех пользователей

```python
from bot.database import crud

async with async_session_maker() as session:
    users = await crud.get_all_users(session)
    for user in users:
        print(f"{user.first_name} - @{user.username}")
```

### Изменить цену проекта

```python
from bot.database import crud

async with async_session_maker() as session:
    project = await crud.get_project_by_id(session, project_id=1)
    await crud.update_project(session, project, price=6000.0)
```

## 🔧 Создание нового handler'а

### 1. Создайте файл handler'а

`bot/handlers/my_feature.py`:

```python
from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

router = Router()

@router.callback_query(F.data == "my_feature")
async def my_feature_handler(callback: CallbackQuery, session: AsyncSession):
    await callback.message.edit_text(
        "Моя новая функция!",
        reply_markup=...
    )
    await callback.answer()
```

### 2. Зарегистрируйте router в main.py

```python
from bot.handlers import my_feature

# В функции main():
dp.include_router(my_feature.router)
```

### 3. Создайте клавиатуру (если нужно)

`bot/keyboards/user.py`:

```python
def get_my_feature_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="Кнопка", callback_data="my_callback")
    )
    return builder.as_markup()
```

## 🎨 FSM (Finite State Machine)

### Создание диалога с состояниями

#### 1. Определите состояния

`bot/states/my_states.py`:

```python
from aiogram.fsm.state import State, StatesGroup

class MyStates(StatesGroup):
    waiting_for_name = State()
    waiting_for_age = State()
    confirm = State()
```

#### 2. Используйте в handler'е

```python
from aiogram.fsm.context import FSMContext
from bot.states.my_states import MyStates

@router.callback_query(F.data == "start_dialog")
async def start_dialog(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("Введите имя:")
    await state.set_state(MyStates.waiting_for_name)

@router.message(MyStates.waiting_for_name)
async def process_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("Введите возраст:")
    await state.set_state(MyStates.waiting_for_age)

@router.message(MyStates.waiting_for_age)
async def process_age(message: Message, state: FSMContext):
    data = await state.get_data()
    await message.answer(f"Имя: {data['name']}, Возраст: {message.text}")
    await state.clear()
```

## 🗄️ Работа с базой данных

### Асинхронный контекст

```python
from bot.database.engine import async_session_maker

async with async_session_maker() as session:
    # Ваш код с БД
    user = await crud.get_user_by_telegram_id(session, 123456789)
```

### Commit и Refresh

```python
# Создание
project = Project(title="Test", ...)
session.add(project)
await session.commit()
await session.refresh(project)  # Обновляем объект из БД

# Обновление
project.price = 1000
await session.commit()
```

### Связи (Relationships)

```python
# Загрузка с связями
from sqlalchemy.orm import selectinload

result = await session.execute(
    select(Project)
    .where(Project.id == 1)
    .options(selectinload(Project.category))
)
project = result.scalar_one_or_none()

# Теперь можно использовать project.category без дополнительных запросов
```

## 🎯 Callback Data паттерны

### Простые callback'и
```python
callback_data="action"
# Обработка:
@router.callback_query(F.data == "action")
```

### Callback'и с параметрами
```python
callback_data="action_123"
# Обработка:
@router.callback_query(F.data.startswith("action_"))
async def handler(callback: CallbackQuery):
    item_id = int(callback.data.split("_")[1])
```

### Сложные callback'и (использование фабрик)
```python
from aiogram.filters.callback_data import CallbackData

class ProjectCallback(CallbackData, prefix="project"):
    action: str
    project_id: int
    page: int = 0

# Создание:
callback_data=ProjectCallback(action="view", project_id=123, page=2).pack()

# Обработка:
@router.callback_query(ProjectCallback.filter())
async def handler(callback: CallbackQuery, callback_data: ProjectCallback):
    project_id = callback_data.project_id
    action = callback_data.action
```

## 📊 Логирование

```python
import logging

logger = logging.getLogger(__name__)

logger.info("Информация")
logger.warning("Предупреждение")
logger.error("Ошибка")
logger.debug("Отладка")

# С дополнительными данными
logger.info(f"Пользователь {user_id} создал заказ {order_id}")
```

## ⚠️ Обработка ошибок

```python
@router.callback_query(F.data == "action")
async def handler(callback: CallbackQuery, session: AsyncSession):
    try:
        # Основная логика
        project = await crud.get_project_by_id(session, 999)
        if not project:
            await callback.answer("❌ Проект не найден", show_alert=True)
            return
        
        # ...
        
    except Exception as e:
        logger.error(f"Ошибка в handler: {e}")
        await callback.answer("❌ Произошла ошибка", show_alert=True)
```

## 🔒 Проверка прав администратора

```python
from bot.database import crud

@router.callback_query(F.data == "admin_action")
async def admin_handler(callback: CallbackQuery, session: AsyncSession):
    is_admin = await crud.is_admin(session, callback.from_user.id)
    
    if not is_admin:
        await callback.answer("❌ Недостаточно прав", show_alert=True)
        return
    
    # Код для админа
```

## 📤 Отправка файлов

```python
from aiogram.types import FSInputFile

# Отправка файла
file = FSInputFile("path/to/file.zip")
await message.answer_document(
    document=file,
    caption="Ваш проект"
)

# Отправка фото
photo = FSInputFile("path/to/image.jpg")
await message.answer_photo(
    photo=photo,
    caption="Описание"
)
```

## 🧪 Тестирование

### Тестовый пользователь

```python
# Создание тестового пользователя
async with async_session_maker() as session:
    user = await crud.create_user(
        session,
        telegram_id=999999999,
        username="testuser",
        first_name="Test"
    )
```

### Очистка БД для тестов

```python
from bot.database.engine import Base, engine

async def reset_database():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
```

## 💡 Полезные трюки

### Красивое форматирование сообщений

```python
text = (
    f"<b>Жирный текст</b>\n"
    f"<i>Курсив</i>\n"
    f"<code>Код</code>\n"
    f"<pre>Блок кода</pre>\n"
    f"<a href='https://example.com'>Ссылка</a>\n"
)

await message.answer(text, parse_mode="HTML")
```

### Прогресс-бар

```python
async def long_operation(message: Message):
    progress_msg = await message.answer("⏳ Обработка...")
    
    # Долгая операция
    await asyncio.sleep(2)
    
    await progress_msg.edit_text("✅ Готово!")
```

### Пагинация с сохранением фильтров

```python
def get_pagination_kb(page: int, total: int, filters: str = ""):
    builder = InlineKeyboardBuilder()
    
    if page > 0:
        builder.button(text="⬅️", callback_data=f"page_{page-1}_{filters}")
    
    builder.button(text=f"{page+1}/{total}", callback_data="current")
    
    if page < total - 1:
        builder.button(text="➡️", callback_data=f"page_{page+1}_{filters}")
    
    return builder.as_markup()
```

## 📚 Полезные ссылки

- [Документация aiogram 3.x](https://docs.aiogram.dev/en/latest/)
- [SQLAlchemy 2.0 docs](https://docs.sqlalchemy.org/en/20/)
- [Python Async/Await](https://docs.python.org/3/library/asyncio.html)
- [Telegram Bot API](https://core.telegram.org/bots/api)

## 🐛 Частые ошибки

### "Event loop is closed"
```python
# Неправильно:
loop = asyncio.get_event_loop()
loop.run_until_complete(main())

# Правильно:
asyncio.run(main())
```

### "Session is closed"
```python
# Всегда используйте async with:
async with async_session_maker() as session:
    # Работа с БД
    pass
```

### "Cannot use markup without message"
```python
# При использовании callback.message.edit_text()
# всегда передавайте reply_markup
await callback.message.edit_text(
    "Текст",
    reply_markup=some_keyboard  # Обязательно!
)
```

---

**Успешной разработки! 💪**

