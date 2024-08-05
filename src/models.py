"""
Модуль models содержит модели для работы с базой данных
"""

from sqlalchemy import Column, String, ForeignKey, Text, DateTime
from sqlalchemy.orm import Mapped, relationship
from sqlalchemy.dialects import mysql
from database import Base

# Аналог типа int(11) в базе MySql
Integer = mysql.INTEGER(11)


class DefaultTable:
    """
    Класс DefaultTable. Представляет собой поля таблицы, которые присутствуют во всех таблица.

    id - id объекта.

    create_datetime - Дата и время создания записи.

    create_user_id - Автор создания записи.

    modify_datetime - Дата и время последнего изменения записи.

    modify_user_id - Автор последнего изменения записи.

    deleted - Отметка об удалении записи.
    """

    id = Column(
        Integer,
        primary_key=True,
        nullable=False,
        autoincrement=True,
    )
    create_datetime = Column(
        DateTime, nullable=True, comment="Дата и время создания записи"
    )
    create_user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        comment="Автор создания записи",
    )
    modify_datetime = Column(
        DateTime, nullable=True, comment="Дата и время последнего изменения записи"
    )
    modify_user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        comment="Автор последнего изменения записи",
    )
    deleted = Column(
        Integer,
        nullable=False,
        default=0,
        comment="Отметка об удалении записи",
        server_default="0",
    )


class UserORM(Base, DefaultTable):
    """
    Класс UserORM. Представляет собой таблицу users.
    наследуется от Base и DefaultTable

    last_name - Фамилия.

    first_name - Имя.

    patr_name - Отчество.

    gender_id - id пола.

    type_id - id типа пользователя.

    login - Логин.

    password  - Пароль.
    """

    __tablename__ = "users"
    __table_args__ = {
        "mysql_engine": "InnoDB",
        "comment": "Пользователи",
        "mysql_auto_increment": "2",
    }
    last_name = Column(String(255), nullable=False, comment="Фамилия")
    first_name = Column(String(255), nullable=True, comment="Имя")
    patr_name = Column(String(255), nullable=True, comment="Отчество")
    gender_id = Column(
        Integer,
        ForeignKey("gender_types.id", ondelete="SET NULL"),
        nullable=True,
        comment="id пола",
    )
    type_id = Column(
        Integer,
        ForeignKey("user_types.id", ondelete="SET NULL"),
        nullable=True,
        comment="id типа пользователя",
    )
    login = Column(String(255), nullable=True, comment="Логин", unique=True)
    password = Column(Text, nullable=True, comment="Пароль")
    documents: Mapped[list["DocumentsORM"]] = relationship(
        primaryjoin="UserORM.id==DocumentsORM.user_id"
    )


class GenderORM(Base, DefaultTable):
    """
    Класс GenderORM. Представляет собой таблицу типов полов.
    наследуется от Base и DefaultTable

    name - Наименование.
    """

    __tablename__ = "gender_types"
    __table_args__ = {
        "mysql_engine": "InnoDB",
        "comment": "Тип пола человека",
        "mysql_auto_increment": "3",
    }
    name = Column(String(255), nullable=True, comment="Наименование", unique=True)


class UserTypesORM(Base, DefaultTable):
    """
    Класс UserTypesORM. Представляет собой таблицу типов пользователей.
    наследуется от Base и DefaultTable

    name - Наименование типа.
    """

    __tablename__ = "user_types"
    __table_args__ = {
        "mysql_engine": "InnoDB",
        "comment": "Типы пользователей",
        "mysql_auto_increment": "3",
    }
    name = Column(String(255), nullable=True, comment="Наименование типа", unique=True)


class DocumentTypesORM(Base, DefaultTable):
    """
    Класс DocumentTypesORM. Представляет собой таблицу типов документов.
    наследуется от Base и DefaultTable

    name - Наименование типа документа.
    """

    __tablename__ = "document_types"
    __table_args__ = {
        "mysql_engine": "InnoDB",
        "comment": "Типы документов",
        "mysql_auto_increment": "5",
    }
    name = Column(
        String(255), nullable=True, comment="Наименование типа документа", unique=True
    )


class DocumentsORM(Base, DefaultTable):
    """
    Класс DocumentsORM. Представляет собой таблицу документов.
    наследуется от Base и DefaultTable

    user_id  - id пользователя.

    type_id - id типа документа.

    data - Данные документов в формате JSON.
    """

    __tablename__ = "documents"
    __table_args__ = {
        "mysql_engine": "InnoDB",
        "comment": "Документы пользователей",
    }
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=True,
        comment="id пользователя",
    )
    type_id = Column(
        Integer,
        ForeignKey("document_types.id", ondelete="SET NULL"),
        nullable=True,
        comment="id типа документа",
    )
    data = Column(Text, nullable=True, comment="Данные документов в формате JSON")


class OrganizationORM(Base, DefaultTable):
    """
    Класс OrganizationORM. Представляет собой таблицу организаций.
    наследуется от Base и DefaultTable

    oid  - oid организации.

    name - Наименование организации.
    """

    __tablename__ = "organizations"
    __table_args__ = {
        "mysql_engine": "InnoDB",
        "comment": "Организации",
    }
    oid = Column(String(255), nullable=False, comment="OID организации", unique=True)
    name = Column(
        String(255), nullable=False, comment="Наименование организации", unique=True
    )
