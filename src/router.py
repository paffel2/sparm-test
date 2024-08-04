from fastapi import APIRouter, Query, UploadFile, Depends, Request, Header
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.encoders import jsonable_encoder
from fastapi.openapi.docs import get_swagger_ui_html
from typing import Annotated, List
from schemas import Document, Organization, Package
from database import session_factory
from sqlalchemy.ext.asyncio import AsyncSession
from queries import (
    create_organization,
    create_user,
    get_user_id_by_login_and_password,
    get_user_info_by_login_and_password,
    check_user_admin_rights,
    get_users_info,
)
from config import settings


router = APIRouter(prefix="/api")


async def get_session():
    try:
        session = session_factory()
        yield session
    finally:
        await session.close()


async def authorization(
    login: Annotated[str, Header()],
    password: Annotated[str, Header()],
    session: AsyncSession = Depends(get_session),
):

    user_id = await get_user_id_by_login_and_password(login, password, session)
    return user_id


async def check_admin_rights(
    login: Annotated[str, Header()],
    password: Annotated[str, Header()],
    session: AsyncSession = Depends(get_session),
):

    approve = await check_user_admin_rights(login, password, session)
    return approve


@router.post("/add_information")
async def get_user_info(
    packages: List[Package],
    session: AsyncSession = Depends(get_session),
    creator_id: int = Depends(authorization),
):
    try:
        for package in packages:
            datas = package.Data
            for data in datas:
                organization = data.Sender.Organization
                users = data.Users
                await create_organization(organization, creator_id, session)
                for user in users:
                    await create_user(
                        user,
                        creator_id,
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
):
    user_info = await get_user_info_by_login_and_password(login, password, session)
    return user_info


@router.get("/get_users_data")
async def get_user_info(
    page: int = 1,
    approve: bool = Depends(check_admin_rights),
    session: AsyncSession = Depends(get_session),
):
    if approve:
        limit = settings.PAGE_SIZE
        offset = (page - 1) * limit
        list_of_users = await get_users_info(session, limit, offset)
        return list_of_users
