"""
Модуль exceptions содержит классы исключений.
"""


class BadValidation(Exception):
    """
    Класс исключение для обработки валидации данных.
    """

    def __init__(self, message: str, *args: object) -> None:
        self.message = message
        super().__init__(*args)


class UserNotFound(Exception):
    """
    Класс исключение для обработки ошибки не найденного пользователя.
    """

    pass


class DocumentNotExist(Exception):
    """
    Класс исключение для обработки ошибки не найденного документа.
    """

    pass


class BadAuthorization(Exception):
    """
    Класс исключение для обработки ошибки авторизации.
    """

    pass


class NotAdmin(Exception):
    """
    Класс исключение для обработки ошибки авторизации администратора.
    """

    pass
