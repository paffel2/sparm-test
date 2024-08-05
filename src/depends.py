"""
Модуль depends содержит функции, которые используются в качестве зависимостей.
"""

from fastapi import Depends, Header
from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession
from exceptions import BadAuthorization, NotAdmin
from database import session_factory
from queries import (
    get_user_auth_by_login_and_password,
)


async def get_session():
    """
    Функция для получения сессий, для работы с базой данных.
    По заврешении работы с сессией, она автоматически закрывается.
    """
    try:
        session = session_factory()
        yield session
    finally:
        await session.close()


async def authorization(
    login: Annotated[str, Header()],
    password: Annotated[str, Header()],
    session: AsyncSession = Depends(get_session),
):
    """
    Функция для авторизации.
    :param login: Логин, тип str. Получен из заголовка login.
    :param password: Пароль, тип str. Получен из заголовка password.
    param password: Сессия, для работы с базой данных. Получен из функции в Depends.
    :return UserAuth: Возвращает объект пользователя
    """

    user = await get_user_auth_by_login_and_password(login, password, session)
    return user


async def admin_authorization(
    login: Annotated[str, Header()],
    password: Annotated[str, Header()],
    session: AsyncSession = Depends(get_session),
):
    """
    Функция для авторизации. В отличие от authorization, выбрасывает исключение NotAdmin,
    которое обрабатывается специальным хендлером.
    :param login: Логин, тип str. Получен из заголовка login.
    :param password: Пароль, тип str. Получен из заголовка password.
    param password: Сессия, для работы с базой данных. Получен из функции в Depends.
    :return UserAuth: Возвращает объект пользователя.
    """
    try:
        user = await get_user_auth_by_login_and_password(login, password, session)
        if user.type_id != 1:
            raise NotAdmin
        return user
    except BadAuthorization:
        raise NotAdmin
