import datetime
from pydantic import BaseModel, ValidationError, Field, ConfigDict
from pydantic.functional_validators import (
    AfterValidator,
    BeforeValidator,
    field_validator,
)
from typing import Annotated, List, Optional
from exceptions import BadValidation
import re


def is_digit_str(v: str) -> str:
    assert v.isdigit(), "неверное числовое значение"


def is_not_empty_string(v: Optional[str]):
    if (v is not None and v) or v is None:
        return v
    else:
        raise AssertionError("пустая строка")


def check_current_length(v: Optional[int | str], size: int):
    if v is None or len(str(v)) == size:
        return v
    else:
        raise AssertionError("Неверная длина значения")


def check_snils(v: Optional[int | str]):
    return check_current_length(v, 11)


def check_inn(v: Optional[int | str]):
    return check_current_length(v, 12)


def bad_pattern_validation(v: str, pattern):
    if re.fullmatch(pattern, v):
        return v
    else:
        raise AssertionError("неверный формат данных")


def referralGUID_validation(v: str):
    return bad_pattern_validation(v, r"[A-Z0-9]{18}:[A-Z0-9]{6}")


def oid_validation(v: str):
    return bad_pattern_validation(v, r"^([0-2])((\.[1-9]{1,7})){1,7}$")


DigitString = Annotated[str, AfterValidator(is_digit_str)]
NotEmptyString = Annotated[str, AfterValidator(is_not_empty_string)]


class DocumentData(BaseModel):
    model_config = ConfigDict(extra="allow")
    documentType_name: Optional[NotEmptyString] = None  # полное наименование
    series: Optional[NotEmptyString | int] = None  # серия
    number: Optional[NotEmptyString] = None  # номер
    beginDate: Optional[datetime.date] = None  # дата начала действия
    endDate: Optional[datetime.date] = None  # дата окончания действия
    orgDep_name: Optional[NotEmptyString] = None  # кем выдан


class Document(DocumentData):
    model_config = ConfigDict(extra="allow")
    id: int  # id документа
    documentType_id: int  # тип (полис, паспорт и т д)


class AddressSchema(BaseModel):
    model_config = ConfigDict(extra="ignore")
    value: Optional[NotEmptyString] = None  # строка с полным адресом


class CredentialSchema(BaseModel):
    username: NotEmptyString
    password: NotEmptyString


class User(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: int  # уникальный идентификатор пользователя (обязательный)
    lastName: NotEmptyString  # фамилия пользователя (обязательный)
    firstName: Optional[NotEmptyString] = None  # имя пользователя
    patrName: Optional[NotEmptyString] = None  # отчество пользователя
    birthDate: Optional[datetime.date] = None  # дата рождения
    sex: Optional[int] = None  # пол
    phoneNumber: int  # номер телефона (обязательный)
    snils: Annotated[Optional[str | int], AfterValidator(check_snils)] = None
    inn: Annotated[Optional[str | int], AfterValidator(check_inn)] = None
    Credentials: CredentialSchema
    Address: Optional[AddressSchema] = None  # объект с данными адреса
    Documents: Optional[List[Document]] = None


class OrganizationSchema(BaseModel):
    oid: Annotated[str, BeforeValidator(oid_validation)] = Field(
        pattern=r"^([0-2])((\.[1-9]{1,7})){1,7}$"
    )  # уникальный идентификатор организации
    fullName: NotEmptyString  # полное наименование организации


class Organization(BaseModel):
    Organization: OrganizationSchema


class DataSchema(BaseModel):
    Sender: Organization
    Users: List[User] = []


class Package(BaseModel):
    id: int  # уникальный идентификатор посылки (обязательный)
    referralGUID: Annotated[str, AfterValidator(referralGUID_validation)] = Field(
        pattern=r"[A-Z0-9]{18}:[A-Z0-9]{6}"
    )  # уникальный ГУИД посылки (обязательный)
    referralDate: datetime.datetime  # дата отправки посылки  (обязательный)
    Data: Optional[List[DataSchema]] = None  # массив объектов с данными пользователей


class DocumentShow(BaseModel):
    model_config = ConfigDict(extra="allow")
    id: int
    type_id: int
    data: DocumentData


class UserShow(BaseModel):
    id: int
    lastName: str
    firstName: Optional[str] = None
    patrName: Optional[str] = None
    gender_id: Optional[int] = None
    type_id: Optional[int] = None
    documents: List[DocumentShow]
