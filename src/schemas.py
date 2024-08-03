from ast import Str
import datetime
from pydantic import BaseModel, ValidationError, Field
from pydantic.functional_validators import AfterValidator, BeforeValidator
from typing import Annotated, List
from exceptions import BadValidation


def is_digit_str(v: str) -> str:
    assert v.isdigit(), "неверное числовое значение"


DigitString = Annotated[str, AfterValidator(is_digit_str)]
NotEmptyString = Annotated[str, Field(min_length=1)]


class Document(BaseModel):
    id: int  # id документа
    documentType_id: int  # тип (полис, паспорт и т д)
    documentType_name: NotEmptyString = None  # полное наименование
    series: NotEmptyString = None  # серия
    number: NotEmptyString = None  # номер
    beginDate: datetime.date  # дата начала действия
    endDate: datetime.date = None  # дата окончания действия
    orgDep_name: NotEmptyString = None  # кем выдан


class AddressSchema(BaseModel):
    value: NotEmptyString = None  # строка с полным адресом


class User(BaseModel):
    id: int  # уникальный идентификатор пользователя (обязательный)
    lastName: NotEmptyString  # фамилия пользователя (обязательный)
    firstName: NotEmptyString = None  # имя пользователя
    patrName: NotEmptyString = None  # отчество пользователя
    birthDate: datetime.date = None  # дата рождения
    sex: int = None  # пол
    phoneNumber: int  # номер телефона (обязательный)
    snils: DigitString = Field(max_length=11, min_length=11)  # снилс
    inn: DigitString = Field(max_length=12, min_length=12)  # ИНН
    Address: AddressSchema = None  # объект с данными адреса
    Documents: List[Document] = None


class Organization(BaseModel):
    oid: str = Field(
        pattern=r"^([0-2])((\.[1-9]*))*$"
    )  # уникальный идентификатор организации
    fullName: NotEmptyString  # полное наименование организации


class DataSchema(BaseModel):
    Sender: Organization
    Users: List[User] = None


class Package(BaseModel):
    id: int  # уникальный идентификатор посылки (обязательный)
    referralGUID: str = Field(
        pattern=r"[A-Z0-9]{18}:[A-Z0-9]{6}"
    )  # уникальный ГУИД посылки (обязательный)
    referralDate: datetime.datetime  # дата отправки посылки  (обязательный)
    Data: DataSchema  # массив объектов с данными пользователей
