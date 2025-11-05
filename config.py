"""
Конфигурация приложения
"""
import os
from typing import List
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Настройки приложения"""
    
    # Telegram Bot
    bot_token: str = Field(..., env='BOT_TOKEN')
    
    # Database
    database_url: str = Field(
        default='sqlite+aiosqlite:///./student_bot.db',
        env='DATABASE_URL'
    )
    
    # Admins
    admin_ids: str = Field(default='', env='ADMIN_IDS')
    
    # Application
    debug: bool = Field(default=True, env='DEBUG')
    timezone: str = Field(default='Europe/Moscow', env='TIMEZONE')
    
    # Paths
    uploads_dir: str = 'uploads'
    projects_dir: str = 'uploads/projects'
    orders_dir: str = 'uploads/orders'
    
    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'
    
    @property
    def admin_list(self) -> List[int]:
        """Получить список ID администраторов"""
        if not self.admin_ids:
            return []
        return [int(admin_id.strip()) for admin_id in self.admin_ids.split(',') if admin_id.strip()]


# Создаем экземпляр настроек
settings = Settings()

# Создаем необходимые директории
os.makedirs(settings.uploads_dir, exist_ok=True)
os.makedirs(settings.projects_dir, exist_ok=True)
os.makedirs(settings.orders_dir, exist_ok=True)

