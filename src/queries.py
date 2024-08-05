"""
Модуль queries содержит запросы к базе данных.
"""

from sqlalchemy import select, update
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
import base64
import datetime
import json
from exceptions import *
from common import create_user_show, validate_document, DocumentsID
from models import (
    UserORM,
    DocumentsORM,
    OrganizationORM,
)
from schemas import (
    Document,
    User,
    OrganizationSchema,
    DocumentData,
    UserAuth,
    UserUpdate,
)


async def create_documents(
    document: Document,
    user_id: int,
    creator_id: int,
    senderName: str,
    referralId: int,
    referralDate: datetime.datetime,
    create_datetime: datetime.datetime,
    session: AsyncSession,
):
    """
    Функция создания документа в базе данных.
    :param user_id: id пользователя.
    :param creator_id: id пользователя создателя записи.
    :param senderName: имя организации, от которой пришел запрос.
    :param referralId: id посылки.
    :param referralDate: дата и время отправления посылки.
    :param create_datetime: дата и время создания записи.
    :param creator_id: id пользователя создателя записи.
    :param session: сессия работы с базой данных.

    """
    validate_document(document, document.documentType_id)
    document_data = document.model_dump()
    document_data.pop("documentType_id", None)
    document_data.pop("id", None)
    document_data["referralId"] = referralId
    document_data["referralDate"] = referralDate
    document_data["senderName"] = senderName
    document_data_json = DocumentData.model_validate(document_data).model_dump_json()
    document_orm = DocumentsORM(
        id=document.id,
        create_datetime=create_datetime,
        create_user_id=creator_id,
        user_id=user_id,
        type_id=document.documentType_id,
        data=document_data_json,
    )
    session.add(document_orm)
    await session.flush()


async def create_documents_with_number_only(
    user_id: int,
    creator_id: int,
    type_id: int,
    number: int,
    senderName: str,
    referralId: int,
    referralDate: datetime.datetime,
    create_datetime: datetime.datetime,
    session: AsyncSession,
):
    """
    Функция создания документа типа СНИЛС и ИНН.
    :param user_id: id пользователя.
    :param creator_id: id пользователя создателя записи.
    :param type_id: id типа документа.
    :param number: номер документа.
    :param senderName: имя организации, от которой пришел запрос.
    :param referralId: id посылки.
    :param referralDate: дата и время отправления посылки.
    :param create_datetime: дата и время создания записи.
    :param session: сессия работы с базой данных.

    """
    document = DocumentsORM(
        type_id=type_id,
        create_user_id=creator_id,
        user_id=user_id,
        create_datetime=create_datetime,
        data=json.dumps(
            {
                "number": number,
                "senderName": senderName,
                "referralId": referralId,
                "referralDate": str(referralDate),
            }
        ),
    )
    session.add(document)
    await session.flush()


async def create_user(
    user: User,
    creator_id: int,
    senderName: str,
    referralId: int,
    referralDate: datetime.datetime,
    session: AsyncSession,
):
    """
    Функция создания пользователя.
    :param user: объект класса User.
    :param creator_id: id пользователя создателя записи.
    :param senderName: имя организации, от которой пришел запрос.
    :param referralId: id посылки.
    :param referralDate: дата и время отправления посылки.
    :param session: сессия работы с базой данных.

    """
    create_datetime = datetime.datetime.now()
    user_orm = UserORM(
        id=user.id,
        last_name=user.lastName,
        first_name=user.firstName,
        patr_name=user.patrName,
        gender_id=user.sex,
        type_id=2,
        login=user.Credentials.username,
        password=base64.b64encode(user.Credentials.password.encode()),
        create_datetime=create_datetime,
        create_user_id=creator_id,
    )
    session.add(user_orm)
    await session.flush()
    await session.refresh(user_orm)

    for document in user.Documents:
        await create_documents(
            document,
            user_orm.id,
            creator_id,
            senderName,
            referralId,
            referralDate,
            create_datetime,
            session,
        )
    if user.snils is not None:
        await create_documents_with_number_only(
            user_orm.id,
            creator_id,
            DocumentsID.SNILS_ID,
            user.snils,
            senderName,
            referralId,
            referralDate,
            create_datetime,
            session,
        )
    if user.inn is not None:
        await create_documents_with_number_only(
            user_orm.id,
            creator_id,
            DocumentsID.INN_ID,
            user.inn,
            senderName,
            referralId,
            referralDate,
            create_datetime,
            session,
        )


async def create_organization(
    organization: OrganizationSchema, creator_id: int, session: AsyncSession
):
    """
    Функция создания организации.
    :param organization: объект класса OrganizationSchema.
    :param creator_id: id пользователя создателя записи.
    :param session: сессия работы с базой данных.

    """
    query = select(OrganizationORM).where(OrganizationORM.oid == organization.oid)
    result = await session.execute(query)
    organization_in_db = result.scalar_one_or_none()
    if organization_in_db:
        return None
    else:
        create_datetime = datetime.datetime.now()
        organization_orm = OrganizationORM(
            name=organization.fullName,
            oid=organization.oid,
            create_user_id=creator_id,
            create_datetime=create_datetime,
        )
        session.add(organization_orm)
        await session.flush()


async def get_user_auth_by_login_and_password(
    login: str, password: str, session: AsyncSession
):
    """
    Функция для получения данных в виде UserAuth(id пользователя и id типа пользователя).
    :param login: логин.
    :param password: пароль.
    :param session: сессия работы с базой данных.
    :return UserAuth

    """
    query = select(UserORM).where(
        UserORM.login == login,
        UserORM.password == base64.b64encode(password.encode()),
        UserORM.deleted == 0,
    )
    result = await session.execute(query)
    user = result.scalar_one_or_none()
    if user:
        return UserAuth(id=user.id, type_id=user.type_id)
    else:
        raise BadAuthorization


async def get_user_info_by_login_and_password(
    login: str, password: str, session: AsyncSession
):
    """
    Функция для получения полных данных пользователя, включая документы.
    :param login: логин.
    :param password: пароль.
    :param session: сессия работы с базой данных.
    :return UserShow
    """
    query = (
        select(UserORM)
        .where(
            UserORM.login == login,
            UserORM.password == base64.b64encode(password.encode()),
            UserORM.deleted == 0,
        )
        .options(selectinload(UserORM.documents))
    )

    result = await session.execute(query)
    user = result.scalar_one_or_none()

    if user:
        return create_user_show(user)
    else:
        raise BadAuthorization


async def get_users_info(session: AsyncSession, limit: int = 10, offset: int = 0):
    """
    Функция для получения списка всех пользователей включая документы.
    :param session: сессия работы с базой данных.
    :param limit: ограничение размера списка.
    :param offset: число пропущенных записей.
    :return List[UserShow]
    """
    query = (
        select(UserORM)
        .where(UserORM.deleted == 0)
        .limit(limit)
        .offset(offset)
        .options(selectinload(UserORM.documents))
    )

    result = await session.execute(query)
    users = result.scalars().all()
    list_of_users = []
    for user in users:
        user_show = create_user_show(user)
        list_of_users.append(user_show)
    return list_of_users


async def delete_user_info_from_db(user_id: int, session: AsyncSession):
    """
    Функция для удаления пользователя.
    :param user_id: id удаляемого пользователя.
    :param session: сессия работы с базой данных.
    """
    select_user_query = select(UserORM).where(
        UserORM.id == user_id, UserORM.deleted == 0
    )
    select_user_result = await session.execute(select_user_query)
    user = select_user_result.scalar_one_or_none()
    if user:
        delete_user_query = (
            update(UserORM).where(UserORM.id == user_id).values(deleted=1)
        )
        delete_user_documents_query = (
            update(DocumentsORM)
            .where(DocumentsORM.user_id == user_id, DocumentsORM.deleted == 0)
            .values(deleted=1)
        )
        await session.execute(delete_user_query)
        await session.execute(delete_user_documents_query)
        await session.commit()
    else:
        raise UserNotFound


async def delete_document(document_id: int, session: AsyncSession, user_id: int = None):
    """
    Функция для удаления документа.
    :param document_id: id документа
    :param session: сессия работы с базой данных.
    :param user_id: id удаляемого пользователя.
    """
    delete_query = (
        update(DocumentsORM).where(DocumentsORM.id == document_id).values(deleted=1)
    )
    if user_id:
        delete_query = (
            update(DocumentsORM)
            .where(DocumentsORM.id == document_id, DocumentsORM.user_id == user_id)
            .values(deleted=1)
        )
    result = await session.execute(delete_query)
    await session.commit()
    if result.rowcount != 1:
        raise DocumentNotExist


async def update_user(
    modifier_id: int, user_id: int, user_update: UserUpdate, session: AsyncSession
):
    """
    Функция обновления пользователя.
    :param modifier_id: id пользователя, который вности изменения.
    :param user_id: id изменяемого пользователя.
    :param user_update: вносимое обновление.
    :param session: сессия работы с базой данных.
    """
    select_user_query = select(UserORM).where(
        UserORM.id == user_id, UserORM.deleted == 0
    )
    result = await session.execute(select_user_query)
    user = result.scalar_one_or_none()
    if user:
        user.last_name = user_update.lastName or user.last_name
        user.first_name = user_update.firstName or user.first_name
        user.patr_name = user_update.patrName or user.patr_name
        user.gender_id = user_update.sex or user.gender_id
        user.login = user_update.login or user.login
        user.password = base64.b64encode(user_update.password.encode()) or user.password
        user.modify_user_id = modifier_id
        user.modify_datetime = datetime.datetime.now()

        session.add(user)
        await session.commit()
    else:
        raise UserNotFound


async def update_document(
    modifier_id: int,
    document_update: Document,
    session: AsyncSession,
    user_id: int = None,
):
    """
    Функция обновления документа.
    :param modifier_id: id пользователя, который вности изменения.
    :param document_update: вносимое обновление.
    :param session: сессия работы с базой данных.
    :param user_id: id владельца документа.
    """
    if user_id:
        select_document_query = select(DocumentsORM).where(
            DocumentsORM.id == document_update.id,
            DocumentsORM.user_id == user_id,
            DocumentsORM.deleted == 0,
        )
    else:
        select_document_query = select(DocumentsORM).where(
            DocumentsORM.id == document_update.id, DocumentsORM.deleted == 0
        )
    result = await session.execute(select_document_query)
    document = result.scalar_one_or_none()
    if document:
        document.type_id = document_update.documentType_id or document.type_id
        current_data = DocumentData.model_validate_json(document.data).model_dump()
        update_data = document_update.model_dump()
        update_data.pop("documentType_id", None)
        update_data.pop("id", None)
        for key, value in update_data.items():
            if value:
                current_data[key] = value
        document_data_obj = DocumentData.model_validate(current_data)
        validate_document(document_data_obj, document.type_id)
        document.data = document_data_obj.model_dump_json()
        document.modify_user_id = modifier_id
        document.modify_datetime = datetime.datetime.now()
        session.add(document)
        await session.commit()
    else:
        raise DocumentNotExist
