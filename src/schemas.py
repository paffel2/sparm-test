"""
Модуль schemas содержит pydantic модели, используемые при валидации запросов и отправке ответов. 
"""

import datetime
from pydantic import BaseModel, Field, ConfigDict
from pydantic.functional_validators import (
    AfterValidator,
    BeforeValidator,
)
from typing import Annotated, List, Optional
import re


def is_digit_str(v: str):
    """
    Функция проверки, что строка, содержит число.
    """
    assert v.isdigit(), "Неверное числовое значение"


def is_not_empty_string(v: Optional[str]):
    """
    Функция проверки, что строка, либо непустая, либо None.
    """
    if (v is not None and v) or v is None:
        return v
    else:
        raise AssertionError("Пустая строка")


def check_current_length(v: Optional[int | str], size: int):
    """
    Функция проверки, что строка определенной длины , либо None.
    """
    if v is None or len(str(v)) == size:
        return v
    else:
        raise AssertionError("Неверная длина значения")


def check_snils(v: Optional[int | str]):
    """
    Функция проверки, что строка равна длине снилс.
    """
    return check_current_length(v, 11)


def check_inn(v: Optional[int | str]):
    """
    Функция проверки, что строка равна длине инн.
    """
    return check_current_length(v, 12)


def bad_pattern_validation(v: str, pattern):
    """
    Функция проверки, что строка подходит под переданный паттерн.
    """
    if re.fullmatch(pattern, v):
        return v
    else:
        raise AssertionError("Неверный формат данных")


def referralGUID_validation(v: str):
    """
    Функция проверки referralGUID.
    """
    return bad_pattern_validation(v, r"[A-Z0-9]{18}:[A-Z0-9]{6}")


def oid_validation(v: str):
    """
    Функция проверки oid.
    """
    return bad_pattern_validation(v, r"^([0-2])((\.[1-9]{1,7})){1,7}$")


def check_gender(v: Optional[int]):
    """
    Функция проверки типа пола.
    """
    if v is None or v == 1 or v == 2:
        return v
    else:
        raise AssertionError("Неверный тип пола")


def check_document_type(v: int):
    """
    Функция проверки типа документа.
    """
    if v > 0 and v < 5:
        return v
    else:
        raise AssertionError("Неверный тип документа")


# Тип непустой строки.
NotEmptyString = Annotated[str, AfterValidator(is_not_empty_string)]


class DocumentData(BaseModel):
    """
    Класс DocumentData. Представляет собой сущность дополнительных данных документа.
    Может принимать дополнительные поляЭ, непрописанные в классе.

    documentType_name - полное наименование

    series - серия

    number - номер

    beginDate - дата начала действия

    endDate - дата окончания действия

    orgDep_Name - кем выдан
    """

    model_config = ConfigDict(extra="allow")
    documentType_name: Optional[NotEmptyString] = None
    series: Optional[NotEmptyString | int] = None
    number: NotEmptyString
    beginDate: Optional[datetime.date] = None
    endDate: Optional[datetime.date] = None
    orgDep_Name: Optional[NotEmptyString] = None


class Document(DocumentData):
    """
    Класс Document. Представляет собой сущность документа.
    Может принимать дополнительные поляЭ, непрописанные в классе.
    Наследуется от DocumentData.

    id - id документа

    documentType_id - тип (полис, паспорт и т д)
    """

    model_config = ConfigDict(extra="allow")
    id: int
    documentType_id: Annotated[int, AfterValidator(check_document_type)]


class AddressSchema(BaseModel):
    """
    Класс AddressSchema. Представляет собой сущность адреса.
    Может принимать дополнительные поля, которые будут игнорироваться.

    value - строка с полным адресом
    """

    model_config = ConfigDict(extra="ignore")
    value: Optional[NotEmptyString] = None


class CredentialSchema(BaseModel):
    """
    Класс CredentialSchema. Представляет собой сущность регистрационных данных.

    username - имя пользователя

    password - пароль

    """

    username: NotEmptyString
    password: NotEmptyString


class UserUpdate(BaseModel):
    """
    Класс UserUpdate. Представляет собой данные для обновления пользователя.

    lastName - фамилия

    firstName - имя

    patrName - отчество

    sex - id пола

    login - имя пользователя

    password - пароль

    """

    lastName: Optional[NotEmptyString] = None
    firstName: Optional[NotEmptyString] = None
    patrName: Optional[NotEmptyString] = None
    sex: Annotated[Optional[int], AfterValidator(check_gender)] = None
    login: Optional[NotEmptyString] = None
    password: Optional[NotEmptyString] = None


class User(BaseModel):
    """
    Класс User Представляет собой данные при регистрации.

    id - уникальный идентификатор пользователя (обязательный)

    lastName - фамилия пользователя (обязательный)

    firstName - имя пользователя

    patrName - отчество пользователя

    birthDate -  дата рождения

    sex - пол

    phoneNumber - номер телефона (обязательный)

    snils - снилс

    inn - инн

    Credentials - логин и пароль (CredentialSchema)

    Address - объект с данными адреса (AddressSchema)

    Documents - список документов

    """

    model_config = ConfigDict(extra="ignore")
    id: int  # уникальный идентификатор пользователя (обязательный)
    lastName: NotEmptyString  # фамилия пользователя (обязательный)
    firstName: Optional[NotEmptyString] = None  # имя пользователя
    patrName: Optional[NotEmptyString] = None  # отчество пользователя
    birthDate: Optional[datetime.date] = None  # дата рождения
    sex: Annotated[Optional[int], AfterValidator(check_gender)] = None  # пол
    phoneNumber: int  # номер телефона (обязательный)
    snils: Annotated[Optional[str | int], AfterValidator(check_snils)] = None
    inn: Annotated[Optional[str | int], AfterValidator(check_inn)] = None
    Credentials: CredentialSchema
    Address: Optional[AddressSchema] = None  # объект с данными адреса
    Documents: Optional[List[Document]] = None


class OrganizationSchema(BaseModel):
    """
    Класс OrganizationSchema. Представляет собой данные при регистрации ораганизации.

    oid - уникальный идентификатор организации
    fullName - полное наименование организации

    """

    oid: Annotated[str, BeforeValidator(oid_validation)] = Field(
        pattern=r"^([0-2])((\.[1-9]{1,7})){1,7}$"
    )  # уникальный идентификатор организации
    fullName: NotEmptyString  # полное наименование организации


class Organization(BaseModel):
    Organization: OrganizationSchema


class DataSchema(BaseModel):
    """
    Класс DataSchema. Представляет собой данные в посылке.

    Sender - данные организации

    Users - данные пользователей

    """

    Sender: Organization
    Users: List[User] = []


class Package(BaseModel):
    """
    Класс Package. Представляет собой посылку.

    id - уникальный идентификатор посылки (обязательный)

    referralGUID - уникальный ГУИД посылки (обязательный)

    referralDate - дата отправки посылки  (обязательный)

    Data - массив объектов с данными пользователей

    """

    id: int  # уникальный идентификатор посылки (обязательный)
    referralGUID: Annotated[str, AfterValidator(referralGUID_validation)] = Field(
        pattern=r"[A-Z0-9]{18}:[A-Z0-9]{6}"
    )  # уникальный ГУИД посылки (обязательный)
    referralDate: datetime.datetime  # дата отправки посылки  (обязательный)
    Data: Optional[List[DataSchema]] = None  # массив объектов с данными пользователей


class DocumentShow(BaseModel):
    """
    Класс DocumentShow. Представляет ответ на запрос документа.

    id - id документа

    type_id - id типа документа

    data - массив дополнительных данных документа

    """

    model_config = ConfigDict(extra="allow")
    id: int
    type_id: int
    data: DocumentData


class UserAuth(BaseModel):
    """
    Класс UserAuth. Представляет id и тип пользователя.

    id - id пользователя

    type_id - id типа пользователя
    """

    id: int
    type_id: Optional[int] = None


class UserShow(UserAuth):
    """
    Класс UserShow. Представляет ответ на запрос данных пользователя.

    lastName - фамилия

    firstName - имя

    patrName - отчество

    gender_id - тип пола

    documents - список документов

    """

    lastName: str
    firstName: Optional[str] = None
    patrName: Optional[str] = None
    gender_id: Optional[int] = None
    documents: List[DocumentShow]
