@echo off
chcp 65001 >nul
cls

echo.
echo ═══════════════════════════════════════════════════════════════
echo         📦 ПОДГОТОВКА БОТА ДЛЯ GITHUB/RAILWAY 📦
echo ═══════════════════════════════════════════════════════════════
echo.

echo [1/3] Проверяю необходимые файлы...
echo.

if exist Procfile (
    echo      ✅ Procfile найден
) else (
    echo      ❌ Procfile не найден
)

if exist railway.json (
    echo      ✅ railway.json найден
) else (
    echo      ❌ railway.json не найден
)

if exist runtime.txt (
    echo      ✅ runtime.txt найден
) else (
    echo      ❌ runtime.txt не найден
)

if exist .gitignore (
    echo      ✅ .gitignore найден
) else (
    echo      ❌ .gitignore не найден
)

if exist requirements.txt (
    echo      ✅ requirements.txt найден
) else (
    echo      ❌ requirements.txt не найден
)

echo.
echo [2/3] Проверяю .env файл...
if exist .env (
    echo      ⚠️  ВНИМАНИЕ! Файл .env существует
    echo      ⚠️  НЕ загружайте его на GitHub!
    echo      ⚠️  Убедитесь что .env есть в .gitignore
) else (
    echo      ℹ️  Файл .env не найден ^(это нормально для GitHub^)
)

echo.
echo [3/3] Создаю пример .env для справки...
if not exist .env.example (
    (
    echo # Пример переменных окружения для Railway
    echo # НЕ загружайте реальные данные на GitHub!
    echo BOT_TOKEN=ваш_токен_от_BotFather
    echo ADMIN_IDS=ваш_telegram_id
    echo DATABASE_URL=sqlite+aiosqlite:///bot.db
    echo ENVIRONMENT=production
    echo LOG_LEVEL=INFO
    ) > .env.example
    echo      ✅ Создан .env.example
) else (
    echo      ℹ️  .env.example уже существует
)

echo.
echo ═══════════════════════════════════════════════════════════════
echo                    ✅ ПРОВЕРКА ЗАВЕРШЕНА
echo ═══════════════════════════════════════════════════════════════
echo.
echo 📋 ЧТО ДАЛЬШЕ:
echo.
echo    1. Создайте репозиторий на GitHub.com
echo       └─ New repository → Private
echo.
echo    2. Загрузите ВСЕ файлы проекта
echo       └─ ⚠️ НЕ загружайте .env файл!
echo       └─ ✅ Загрузите .env.example для справки
echo.
echo    3. Перейдите на Railway.app
echo       └─ Login with GitHub
echo       └─ New Project → Deploy from GitHub
echo.
echo    4. Добавьте переменные окружения в Railway:
echo       └─ BOT_TOKEN
echo       └─ ADMIN_IDS
echo       └─ DATABASE_URL
echo       └─ ENVIRONMENT
echo       └─ LOG_LEVEL
echo.
echo    5. Railway автоматически запустит бота!
echo.
echo ═══════════════════════════════════════════════════════════════
echo.
echo 📚 Подробная инструкция: 🚂_ЗАПУСК_НА_RAILWAY.txt
echo.
pause

