@echo off
chcp 65001 >nul
cls

echo.
echo ═══════════════════════════════════════════════════════════════
echo              🔧 СОЗДАНИЕ ФАЙЛА .env ДЛЯ БОТА 🔧
echo ═══════════════════════════════════════════════════════════════
echo.

REM Проверяем существует ли .env
if exist .env (
    echo ⚠️  ВНИМАНИЕ: Файл .env уже существует!
    echo.
    set /p "overwrite=Перезаписать? (y/n): "
    if /i not "%overwrite%"=="y" (
        echo.
        echo ❌ Отменено пользователем
        pause
        exit /b
    )
)

echo.
echo 📝 Пожалуйста, введите данные:
echo.
echo ─────────────────────────────────────────────────────────────
echo.

REM Запрашиваем токен бота
:ask_token
set /p "bot_token=🤖 Токен бота (@BotFather): "
if "%bot_token%"=="" (
    echo ❌ Токен не может быть пустым!
    goto ask_token
)

echo.

REM Запрашиваем Telegram ID
:ask_id
set /p "admin_id=👤 Ваш Telegram ID (@userinfobot): "
if "%admin_id%"=="" (
    echo ❌ ID не может быть пустым!
    goto ask_id
)

echo.
echo ─────────────────────────────────────────────────────────────
echo.

REM Создаём файл .env
(
    echo # Конфигурация Telegram бота
    echo # Создан: %date% %time%
    echo.
    echo # Токен бота от @BotFather
    echo BOT_TOKEN=%bot_token%
    echo.
    echo # ID администраторов
    echo ADMIN_IDS=%admin_id%
    echo.
    echo # База данных
    echo DATABASE_URL=sqlite+aiosqlite:///bot.db
    echo.
    echo # Настройки
    echo ENVIRONMENT=development
    echo LOG_LEVEL=INFO
) > .env

if exist .env (
    echo ✅ Файл .env успешно создан!
    echo.
    echo ═══════════════════════════════════════════════════════════════
    echo.
    echo 🚀 Теперь можно запустить бота:
    echo.
    echo    .\start.bat
    echo.
    echo или
    echo.
    echo    python main.py
    echo.
    echo ═══════════════════════════════════════════════════════════════
) else (
    echo ❌ Ошибка при создании файла .env
    echo Попробуйте создать файл вручную.
)

echo.
pause

