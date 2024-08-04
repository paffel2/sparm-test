from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from exceptions import *

import uvicorn
from router import router as package_router


app = FastAPI()
app.include_router(router=package_router)


@app.exception_handler(RequestValidationError)
async def workspace_doesnt_exist_handler(request, exc: RequestValidationError):
    errors = exc.errors()
    loc = errors[0]["loc"][-1]
    input = errors[0]["input"]
    message = f"Неверный формат данных. {loc} : {input}"
    return JSONResponse(
        {"message": "error", "content": message},
        status_code=400,
    )


if __name__ == "__main__":

    uvicorn.run(app, host="localhost", port=8000)
