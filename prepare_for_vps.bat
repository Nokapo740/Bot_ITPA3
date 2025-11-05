@echo off
chcp 65001 >nul
cls

echo.
echo ═══════════════════════════════════════════════════════════════
echo         📦 ПОДГОТОВКА БОТА ДЛЯ ЗАГРУЗКИ НА VPS 📦
echo ═══════════════════════════════════════════════════════════════
echo.

echo [1/4] Создаю папку для деплоя...
if exist deploy_package rmdir /s /q deploy_package
mkdir deploy_package
echo      ✅ Папка создана

echo.
echo [2/4] Копирую необходимые файлы...

:: Копируем код бота
xcopy bot deploy_package\bot /E /I /Y >nul
echo      ✅ Код бота скопирован

:: Копируем файлы конфигурации
copy requirements.txt deploy_package\ >nul
copy main.py deploy_package\ >nul
copy config.py deploy_package\ >nul
echo      ✅ Файлы конфигурации скопированы

:: Создаем пример .env файла
echo [3/4] Создаю пример .env файла...
(
echo # Настройки для VPS
echo BOT_TOKEN=ВАШ_ТОКЕН_ОТ_BOTFATHER
echo ADMIN_IDS=ВАШ_TELEGRAM_ID
echo DATABASE_URL=sqlite+aiosqlite:///bot.db
echo ENVIRONMENT=production
echo LOG_LEVEL=INFO
) > deploy_package\.env.example
echo      ✅ Пример .env создан

echo.
echo [4/4] Создаю инструкцию для VPS...
(
echo ═══════════════════════════════════════════════════════════
echo   ИНСТРУКЦИЯ ПО УСТАНОВКЕ НА VPS
echo ═══════════════════════════════════════════════════════════
echo.
echo 1. Загрузите все файлы на сервер в папку /root/bot
echo.
echo 2. Подключитесь к серверу: ssh root@ваш_ip
echo.
echo 3. Выполните команды:
echo.
echo    cd /root/bot
echo    python3.11 -m venv venv
echo    source venv/bin/activate
echo    pip install -r requirements.txt
echo.
echo 4. Создайте .env файл:
echo.
echo    cp .env.example .env
echo    nano .env
echo.
echo    Укажите свои данные и сохраните ^(Ctrl+O, Enter, Ctrl+X^)
echo.
echo 5. Создайте systemd сервис:
echo.
echo    sudo nano /etc/systemd/system/telegram-bot.service
echo.
echo    Вставьте содержимое из файла telegram-bot.service
echo.
echo 6. Запустите бота:
echo.
echo    sudo systemctl daemon-reload
echo    sudo systemctl start telegram-bot
echo    sudo systemctl enable telegram-bot
echo    sudo systemctl status telegram-bot
echo.
echo ═══════════════════════════════════════════════════════════
echo   ГОТОВО! Бот работает 24/7!
echo ═══════════════════════════════════════════════════════════
) > deploy_package\INSTALL.txt
echo      ✅ Инструкция создана

echo.
echo [БОНУС] Создаю файл systemd сервиса...
(
echo [Unit]
echo Description=Telegram Bot
echo After=network.target
echo.
echo [Service]
echo Type=simple
echo User=root
echo WorkingDirectory=/root/bot
echo Environment="PATH=/root/bot/venv/bin"
echo ExecStart=/root/bot/venv/bin/python /root/bot/main.py
echo Restart=always
echo RestartSec=10
echo.
echo [Install]
echo WantedBy=multi-user.target
) > deploy_package\telegram-bot.service
echo      ✅ Сервис создан

echo.
echo ═══════════════════════════════════════════════════════════
echo                    ✅ ВСЁ ГОТОВО! ✅
echo ═══════════════════════════════════════════════════════════
echo.
echo 📦 Все файлы находятся в папке: deploy_package\
echo.
echo 📋 ЧТО ДЕЛАТЬ ДАЛЬШЕ:
echo.
echo    1. Загрузите папку deploy_package на VPS
echo.
echo    2. Используйте FileZilla, WinSCP или SCP:
echo       scp -r deploy_package/* root@ВАШ_IP:/root/bot/
echo.
echo    3. Следуйте инструкции из файла INSTALL.txt
echo.
echo ═══════════════════════════════════════════════════════════
echo.
pause

