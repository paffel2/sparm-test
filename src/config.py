"""
Модуль config, содержит параметры сервера.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Класс содержащий настройки сервера

    DB_HOST: str  - хост базы данных

    DB_PORT: int  - порт базы данных

    DB_USER: str  - имя пользователя базы данных

    DB_PASSWORD: str  - пароль базы данных

    DB_NAME: str  - имя базы данных

    PAGE_SIZE: int  - размер страниц для пагинации

    DATABASE_URL: str - url для подключения к базе данных
    """

    DB_HOST: str
    DB_PORT: int
    DB_USER: str
    DB_PASSWORD: str
    DB_NAME: str
    PAGE_SIZE: int

    @property
    def DATABASE_URL(self):
        return f"mysql+aiomysql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
