from sqlalchemy import select, delete
from models import (
    UserORM,
    GenderORM,
    UserTypesORM,
    DocumentTypesORM,
    DocumentsORM,
    OrganizationORM,
)
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import selectinload
from schemas import (
    Document,
    User,
    OrganizationSchema,
    DocumentData,
    DocumentShow,
    UserShow,
)
from sqlalchemy.ext.asyncio import AsyncSession
from database import session_factory
from asyncpg.exceptions import UniqueViolationError
import base64
import datetime
import json
from exceptions import *


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

    document_data = document.model_dump()
    document_data.pop("documentType_id", None)
    document_data.pop("id", None)
    document_data["referralId"] = referralId
    document_data["referralDate"] = referralDate
    document_data["senderName"] = senderName

    document_data_json = (DocumentData.model_validate(document_data)).model_dump_json()
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


async def create_user(
    user: User,
    creator_id: int,
    senderName: str,
    referralId: int,
    referralDate: datetime.datetime,
    session: AsyncSession,
):
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


async def create_organization(
    organization: OrganizationSchema, creator_id: int, session: AsyncSession
):
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


async def get_user_id_by_login_and_password(
    login: str, password: str, session: AsyncSession
):
    query = select(UserORM).where(
        UserORM.login == login,
        UserORM.password == base64.b64encode(password.encode()),
        UserORM.deleted == 0,
    )
    result = await session.execute(query)
    user = result.scalar_one_or_none()
    if user:
        return user.id
    else:
        raise Exception  # TODO add exception bad autorization


async def check_user_admin_rights(login: str, password: str, session: AsyncSession):
    query = select(UserORM).where(
        UserORM.login == login,
        UserORM.password == base64.b64encode(password.encode()),
        UserORM.type_id == 1,
        UserORM.deleted == 0,
    )
    result = await session.execute(query)
    user = result.scalar_one_or_none()
    if user:
        return True
    else:
        raise Exception  # TODO add exception bad autorization


def create_user_show(user: UserORM):
    documents = user.documents
    list_of_documents = []
    for document in documents:
        if document.deleted == 0:
            document_show = DocumentShow(
                id=document.id,
                type_id=document.type_id,
                data=DocumentData.model_validate_json(document.data),
            )
            list_of_documents.append(document_show)
    user_show = UserShow(
        id=user.id,
        lastName=user.last_name,
        firstName=user.first_name,
        patrName=user.patr_name,
        gender_id=user.gender_id,
        type_id=user.type_id,
        documents=list_of_documents,
    )
    return user_show


async def get_user_info_by_login_and_password(
    login: str, password: str, session: AsyncSession
):
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
        raise Exception  # TODO add exception bad autorization


async def get_users_info(session: AsyncSession, limit: int = 10, offset: int = 0):
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
