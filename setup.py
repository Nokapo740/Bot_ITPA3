"""
Скрипт первоначальной настройки проекта
"""
import os
import sys
import subprocess


def print_header(text):
    """Красивый заголовок"""
    print("\n" + "=" * 50)
    print(f"  {text}")
    print("=" * 50 + "\n")


def check_python_version():
    """Проверка версии Python"""
    if sys.version_info < (3, 10):
        print("❌ Требуется Python 3.10 или выше!")
        print(f"   Текущая версия: {sys.version}")
        sys.exit(1)
    print(f"✅ Python версия: {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")


def create_env_file():
    """Создание .env файла"""
    if os.path.exists(".env"):
        print("⚠️  Файл .env уже существует")
        response = input("   Перезаписать? (y/n): ")
        if response.lower() != 'y':
            print("   Пропускаем создание .env")
            return
    
    print("📝 Создание файла .env...")
    
    # Запрашиваем данные
    bot_token = input("   Введите BOT_TOKEN от @BotFather: ").strip()
    admin_ids = input("   Введите ADMIN_IDS (через запятую): ").strip()
    
    # Создаем .env
    with open(".env", "w", encoding="utf-8") as f:
        f.write(f"# Telegram Bot Configuration\n")
        f.write(f"BOT_TOKEN={bot_token}\n\n")
        f.write(f"# Database Configuration\n")
        f.write(f"DATABASE_URL=sqlite+aiosqlite:///./student_bot.db\n\n")
        f.write(f"# Admin Configuration\n")
        f.write(f"ADMIN_IDS={admin_ids}\n\n")
        f.write(f"# Application Settings\n")
        f.write(f"DEBUG=True\n")
        f.write(f"TIMEZONE=Europe/Moscow\n")
    
    print("✅ Файл .env создан")


def install_requirements():
    """Установка зависимостей"""
    print("📦 Установка зависимостей...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Зависимости установлены")
    except subprocess.CalledProcessError:
        print("❌ Ошибка установки зависимостей")
        sys.exit(1)


def create_directories():
    """Создание необходимых директорий"""
    print("📁 Создание директорий...")
    directories = [
        "uploads",
        "uploads/projects",
        "uploads/orders",
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"   ✅ {directory}")


def main():
    """Главная функция"""
    print_header("🎓 Настройка Студенческого Аутсорс Бота")
    
    print("Шаг 1: Проверка Python")
    check_python_version()
    
    print("\nШаг 2: Создание .env файла")
    create_env_file()
    
    print("\nШаг 3: Установка зависимостей")
    install_requirements()
    
    print("\nШаг 4: Создание директорий")
    create_directories()
    
    print_header("✅ Настройка завершена!")
    
    print("📝 Следующие шаги:\n")
    print("1. Добавьте тестовые данные:")
    print("   python add_sample_data.py\n")
    print("2. Запустите бота:")
    print("   python main.py\n")
    print("   или используйте start.bat (Windows)\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Настройка прервана пользователем")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        sys.exit(1)

