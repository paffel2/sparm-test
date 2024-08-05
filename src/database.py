"""
Модуль database содержит вспомогательные функции и классы для работы с базой данных.
"""

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from config import settings
from sqlalchemy.orm import DeclarativeBase

# Движок для работы с базой данных
engine = create_async_engine(
    url=settings.DATABASE_URL, echo=False, pool_size=5, max_overflow=10
)

# Фабричный метод для получения сессий для работы с базой данных
session_factory = async_sessionmaker(engine)


# Класс содержащий различные методанные для работы с моделями в базе
# Метод repr переопределен для удобного отображения моделей в логах
class Base(DeclarativeBase):
    """
    Класс содержащий различные методанные для работы с моделями в базе.

    Метод repr переопределен для удобного отображения моделей в логах.
    """

    def __repr__(self) -> str:
        cols = []
        for ids, col in enumerate(self.__table__.columns.keys()):
            cols.append(f"{col}={getattr(self, col)}")

        return f"<{self.__class__.__name__} {', '.join(cols)}>"
