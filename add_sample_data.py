"""
Скрипт для добавления тестовых данных в базу
"""
import asyncio
from bot.database import crud, init_db
from bot.database.engine import async_session_maker
from bot.database.models import ProjectType, ProjectLevel


async def add_sample_data():
    """Добавить тестовые данные"""
    print("🔄 Инициализация базы данных...")
    await init_db()
    
    async with async_session_maker() as session:
        print("\n📁 Создание категорий...")
        
        # Создаем категории
        categories_data = [
            {"name": "Python", "description": "Проекты на Python", "icon": "🐍"},
            {"name": "JavaScript", "description": "Проекты на JavaScript", "icon": "📜"},
            {"name": "Java", "description": "Проекты на Java", "icon": "☕"},
            {"name": "C++", "description": "Проекты на C++", "icon": "🔧"},
            {"name": "Web", "description": "Web-разработка", "icon": "🌐"},
        ]
        
        categories = {}
        for cat_data in categories_data:
            try:
                category = await crud.create_category(session, **cat_data)
                categories[cat_data["name"]] = category
                print(f"  ✅ Создана категория: {category.name}")
            except Exception as e:
                print(f"  ⚠️  Категория {cat_data['name']} уже существует или ошибка: {e}")
        
        print("\n📚 Создание проектов...")
        
        # Создаем проекты
        projects_data = [
            {
                "title": "Телеграм-бот для интернет-магазина",
                "description": "Полнофункциональный бот с корзиной, оплатой и админ-панелью. Включает каталог товаров, систему заказов, интеграцию с платежными системами.",
                "category": "Python",
                "project_type": ProjectType.PROJECT,
                "level": ProjectLevel.ADVANCED,
                "technologies": "aiogram 3.x, SQLAlchemy, PostgreSQL, ЮKassa API",
                "programming_languages": "Python",
                "price": 8000.0,
            },
            {
                "title": "Система управления складом",
                "description": "Desktop приложение для учета товаров на складе с базой данных. Включает добавление/удаление товаров, отчеты, поиск.",
                "category": "Python",
                "project_type": ProjectType.DIPLOMA,
                "level": ProjectLevel.INTERMEDIATE,
                "technologies": "PyQt5, SQLite, pandas, matplotlib",
                "programming_languages": "Python",
                "price": 12000.0,
            },
            {
                "title": "Веб-сайт портфолио",
                "description": "Современный адаптивный сайт-портфолио с анимациями. Полностью responsive дизайн, оптимизация для SEO.",
                "category": "Web",
                "project_type": ProjectType.PROJECT,
                "level": ProjectLevel.BASIC,
                "technologies": "HTML5, CSS3, JavaScript, Bootstrap 5",
                "programming_languages": "JavaScript, HTML, CSS",
                "price": 3000.0,
            },
            {
                "title": "Интернет-магазин на React",
                "description": "SPA интернет-магазин с корзиной, фильтрами, поиском. Backend на Node.js + Express, Frontend на React.",
                "category": "JavaScript",
                "project_type": ProjectType.DIPLOMA,
                "level": ProjectLevel.ADVANCED,
                "technologies": "React, Redux, Node.js, Express, MongoDB",
                "programming_languages": "JavaScript",
                "price": 15000.0,
            },
            {
                "title": "REST API для социальной сети",
                "description": "Backend API с аутентификацией, постами, комментариями, лайками. Документация Swagger.",
                "category": "Python",
                "project_type": ProjectType.COURSEWORK,
                "level": ProjectLevel.ADVANCED,
                "technologies": "FastAPI, PostgreSQL, JWT, Redis",
                "programming_languages": "Python",
                "price": 7000.0,
            },
            {
                "title": "Игра 'Змейка' на C++",
                "description": "Классическая игра змейка с графическим интерфейсом, счетом и уровнями сложности.",
                "category": "C++",
                "project_type": ProjectType.PROJECT,
                "level": ProjectLevel.INTERMEDIATE,
                "technologies": "C++, SFML, STL",
                "programming_languages": "C++",
                "price": 4000.0,
            },
            {
                "title": "Калькулятор на Java",
                "description": "GUI калькулятор с основными математическими операциями и историей вычислений.",
                "category": "Java",
                "project_type": ProjectType.PROJECT,
                "level": ProjectLevel.BASIC,
                "technologies": "Java Swing, JUnit",
                "programming_languages": "Java",
                "price": 2500.0,
            },
            {
                "title": "Презентация 'Основы Python'",
                "description": "Профессиональная презентация на 30+ слайдов с примерами кода, диаграммами и иллюстрациями.",
                "category": "Python",
                "project_type": ProjectType.PRESENTATION,
                "level": ProjectLevel.BASIC,
                "technologies": "PowerPoint, Canva",
                "programming_languages": "Python (примеры)",
                "price": 1500.0,
            },
            {
                "title": "Чат-бот с машинным обучением",
                "description": "Интеллектуальный чат-бот с использованием NLP и нейронных сетей. Обучение на пользовательских данных.",
                "category": "Python",
                "project_type": ProjectType.DIPLOMA,
                "level": ProjectLevel.ADVANCED,
                "technologies": "Python, TensorFlow, NLTK, scikit-learn",
                "programming_languages": "Python",
                "price": 18000.0,
            },
            {
                "title": "CRM система для малого бизнеса",
                "description": "Система управления клиентами с базой данных, отчетами, напоминаниями.",
                "category": "Web",
                "project_type": ProjectType.DIPLOMA,
                "level": ProjectLevel.ADVANCED,
                "technologies": "Django, PostgreSQL, Bootstrap, jQuery",
                "programming_languages": "Python, JavaScript",
                "price": 16000.0,
            },
        ]
        
        for project_data in projects_data:
            category_name = project_data.pop("category")
            
            if category_name in categories:
                project_data["category_id"] = categories[category_name].id
                project_data["is_active"] = True
                
                try:
                    project = await crud.create_project(session, **project_data)
                    print(f"  ✅ Создан проект: {project.title}")
                except Exception as e:
                    print(f"  ⚠️  Ошибка создания проекта '{project_data['title']}': {e}")
        
        print("\n✅ Тестовые данные успешно добавлены!")
        print("\n📊 Статистика:")
        print(f"  • Категорий: {len(categories)}")
        print(f"  • Проектов: {len(projects_data)}")


if __name__ == "__main__":
    print("🎓 Добавление тестовых данных в базу\n")
    asyncio.run(add_sample_data())
    print("\n🎉 Готово! Можете запустить бота: python main.py")

