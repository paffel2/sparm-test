"""
Модуль config, содержит параметры сервера.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Класс содержащий настройки сервера

    MYSQL_HOST: str  - хост базы данных

    MYSQL_PORT: int  - порт базы данных

    MYSQL_USER: str  - имя пользователя базы данных

    MYSQL_PASSWORD: str  - пароль базы данных

    MYSQL_DATABASE: str  - имя базы данных

    PAGE_SIZE: int  - размер страниц для пагинации

    DATABASE_URL: str - url для подключения к базе данных
    """

    MYSQL_HOST: str
    MYSQL_PORT: int
    MYSQL_USER: str
    MYSQL_PASSWORD: str
    MYSQL_DATABASE: str
    PAGE_SIZE: int

    @property
    def DATABASE_URL(self):
        return f"mysql+aiomysql://{self.MYSQL_USER}:{self.MYSQL_PASSWORD}@{self.MYSQL_HOST}:{self.MYSQL_PORT}/{self.MYSQL_DATABASE}"

    model_config = SettingsConfigDict(env_file="env_template", extra="ignore")


settings = Settings()
