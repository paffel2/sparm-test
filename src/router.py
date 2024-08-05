"""
Модуль router содержит все эндпоинты приложения.
"""

from fastapi import APIRouter, Depends, Header
from fastapi.responses import JSONResponse
from typing import Annotated, List
from exceptions import NotAdmin
from schemas import Package, UserAuth, UserShow, UserUpdate, Document
from sqlalchemy.ext.asyncio import AsyncSession
from queries import (
    create_organization,
    create_user,
    get_user_info_by_login_and_password,
    get_users_info,
    delete_user_info_from_db,
    delete_document,
    update_user,
    update_document,
)
from config import settings
from depends import get_session, authorization, admin_authorization


router = APIRouter(prefix="/api")


@router.post("/add_information")
async def get_user_info(
    packages: List[Package],
    session: AsyncSession = Depends(get_session),
    creator: UserAuth = Depends(authorization),
):
    try:
        for package in packages:
            datas = package.Data
            for data in datas:
                organization = data.Sender.Organization
                users = data.Users
                await create_organization(organization, creator.id, session)
                for user in users:
                    await create_user(
                        user,
                        creator.id,
                        organization.fullName,
                        package.id,
                        package.referralDate,
                        session,
                    )
                await session.commit()
        return JSONResponse({"status": "ok"})
    except:
        await session.rollback()
        raise


@router.get("/get_personal_info")
async def get_user_info(
    login: Annotated[str, Header()],
    password: Annotated[str, Header()],
    session: AsyncSession = Depends(get_session),
) -> UserShow:
    user_info = await get_user_info_by_login_and_password(login, password, session)
    return user_info


@router.get("/get_users_data")
async def get_user_info(
    page: int = 1,
    admin: UserAuth = Depends(admin_authorization),
    session: AsyncSession = Depends(get_session),
) -> List[UserShow]:
    if admin.type_id == 1:
        limit = settings.PAGE_SIZE
        offset = (page - 1) * limit
        list_of_users = await get_users_info(session, limit, offset)
        return list_of_users
    else:
        raise NotAdmin


@router.delete("/delete_user_info")
async def delete_user_info(
    user_id: int = None,
    user: UserAuth = Depends(authorization),
    session: AsyncSession = Depends(get_session),
):
    try:
        if user_id and user.type_id == 1:
            await delete_user_info_from_db(user_id, session)

        else:
            await delete_user_info_from_db(user.id, session)
        return JSONResponse({"status": "user deleted"})
    except:
        await session.rollback()


@router.delete("/delete_user_document")
async def delete_user_document(
    document_id: int,
    user: UserAuth = Depends(authorization),
    session: AsyncSession = Depends(get_session),
):
    try:
        if user.type_id == 1:
            await delete_document(document_id, session)
        else:
            await delete_document(document_id, session, user.id)
        return JSONResponse({"status": "document deleted"})
    except:
        await session.rollback()


@router.put("/update_user")
async def update_user_info(
    update: UserUpdate,
    user_id: int = None,
    user: UserAuth = Depends(authorization),
    session: AsyncSession = Depends(get_session),
):
    try:
        if user.type_id == 1 and user_id:
            await update_user(user.id, user_id, update, session)
        else:
            await update_user(user.id, user.id, update, session)
        return JSONResponse({"status": "user updated"})
    except:
        await session.rollback()


@router.put("/update_document")
async def update_document_info(
    update: Document,
    user: UserAuth = Depends(authorization),
    session: AsyncSession = Depends(get_session),
):
    try:
        if user.type_id == 1:
            await update_document(user.id, update, session)
        else:
            await update_document(user.id, update, session, user.id)
        return JSONResponse({"status": "document updated"})
    except:
        await session.rollback()
