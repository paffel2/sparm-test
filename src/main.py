"""
Модуль main. Главный модуль для запуска сервера.
"""

from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import IntegrityError
from exceptions import *

import uvicorn
from router import router as package_router
import logging

logger = logging.getLogger()

# приложение FastApi
app = FastAPI()
# добавление роутера в приложение
app.include_router(router=package_router)


@app.exception_handler(RequestValidationError)
async def request_validation_handler(request, exc: RequestValidationError):
    """
    Функция, добавляющая обработку исключения RequestValidationError.
    """
    errors = exc.errors()
    logger.error(f"RequestValidationError. {errors}")
    loc = errors[0]["loc"][-1]
    input = errors[0]["input"]
    message = f"Неверный формат данных. {loc} : {input}"
    raise HTTPException(
        detail=message,
        status_code=400,
    )


@app.exception_handler(BadAuthorization)
async def bad_authorization_handler(request, exc: BadAuthorization):
    """
    Функция, добавляющая обработку исключения BadAuthorization.
    """
    raise HTTPException(
        detail="Неверный логин или пароль",
        status_code=400,
    )


@app.exception_handler(UserNotFound)
async def user_not_found_handler(request, exc: UserNotFound):
    """
    Функция, добавляющая обработку исключения UserNotFound.
    """
    raise HTTPException(
        detail="Пользователь не существует",
        status_code=400,
    )


@app.exception_handler(DocumentNotExist)
async def document_not_exist_handler(request, exc: DocumentNotExist):
    """
    Функция, добавляющая обработку исключения DocumentNotExist.
    """
    raise HTTPException(
        detail="Документ не существует",
        status_code=400,
    )


@app.exception_handler(NotAdmin)
async def document_not_exist_handler(request, exc: NotAdmin):
    """
    Функция, добавляющая обработку исключения NotAdmin.
    """
    raise HTTPException(
        status_code=404,
    )


@app.exception_handler(BadValidation)
async def bad_validation_handler(request, exc: BadValidation):
    """
    Функция, добавляющая обработку исключения BadValidation.
    """
    raise HTTPException(
        detail=exc.message,
        status_code=400,
    )


@app.exception_handler(IntegrityError)
async def integrity_error_handler(request, exc: IntegrityError):
    """
    Функция, добавляющая обработку исключения IntegrityError.
    """
    logger.error(f"IntegrityError. {exc}")
    raise HTTPException(
        status_code=500,
    )


@app.exception_handler(Exception)
async def exception_handler(request, exc: Exception):
    """
    Функция, добавляющая обработку исключения Exception.
    """
    logger.error(f"Exception. {exc}")
    raise HTTPException(
        status_code=500,
    )


if __name__ == "__main__":
    # запуск сервера
    uvicorn.run(app, host="0.0.0.0", port=8000)
