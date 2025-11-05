@echo off
chcp 65001 > nul
echo ========================================
echo    Запуск Студенческого Аутсорс Бота
echo ========================================
echo.

REM Проверка наличия виртуального окружения
if not exist "venv\" (
    echo Виртуальное окружение не найдено!
    echo Создаем виртуальное окружение...
    python -m venv venv
    echo.
    echo Установка зависимостей...
    call venv\Scripts\activate.bat
    pip install -r requirements.txt
    echo.
) else (
    call venv\Scripts\activate.bat
)

REM Проверка наличия .env файла
if not exist ".env" (
    echo ⚠️  ВНИМАНИЕ: Файл .env не найден!
    echo.
    echo Пожалуйста:
    echo 1. Скопируйте .env.example в .env
    echo 2. Заполните BOT_TOKEN и ADMIN_IDS
    echo 3. Запустите скрипт снова
    echo.
    pause
    exit /b 1
)

echo.
echo ✅ Запуск бота...
echo.
python main.py

pause

