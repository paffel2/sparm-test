from fastapi import FastAPI
from fastapi.responses import JSONResponse
from exceptions import *


import uvicorn
from router import router as package_router


app = FastAPI()
app.include_router(router=package_router)


if __name__ == "__main__":

    uvicorn.run(app, host="localhost", port=8000)
