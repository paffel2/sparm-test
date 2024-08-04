from sqlalchemy import Column, Identity, String, ForeignKey, Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects import mysql
from typing import Annotated, Optional
import enum
import uuid
from datetime import datetime

from database import Base

Integer = mysql.INTEGER(11)


class DefaultTable:
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
    __tablename__ = "gender_types"
    __table_args__ = {
        "mysql_engine": "InnoDB",
        "comment": "Тип пола человека",
        "mysql_auto_increment": "3",
    }
    name = Column(String(255), nullable=True, comment="Наименование", unique=True)


class UserTypesORM(Base, DefaultTable):
    __tablename__ = "user_types"
    __table_args__ = {
        "mysql_engine": "InnoDB",
        "comment": "Типы пользователей",
        "mysql_auto_increment": "3",
    }
    name = Column(String(255), nullable=True, comment="Наименование типа", unique=True)


class DocumentTypesORM(Base, DefaultTable):
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
    __tablename__ = "organizations"
    __table_args__ = {
        "mysql_engine": "InnoDB",
        "comment": "Организации",
    }
    oid = Column(String(255), nullable=False, comment="OID организации", unique=True)
    name = Column(
        String(255), nullable=False, comment="Наименование организации", unique=True
    )
