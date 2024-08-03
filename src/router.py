from fastapi import APIRouter, Query, UploadFile, Depends
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.encoders import jsonable_encoder
from typing import Annotated
from schemas import Document, Package


router = APIRouter(prefix="/api")


@router.post("/add_information")
async def get_user_info(package: Package):
    print(package)
    return JSONResponse({"status": "ok"})


@router.get("/get_info")
async def get_user_info():
    return JSONResponse({"status": "ok"})
