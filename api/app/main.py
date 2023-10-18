from fastapi import FastAPI, Request
from pydantic import BaseModel
from app.config.db import init_db
from app.models import models
from app.routers import pet_router, user_router, country_router, state_router, city_router, auth_router
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel

from fastapi.staticfiles import StaticFiles
from aiofiles import open as async_open
import os, json

app = FastAPI()


# app.mount("/files", StaticFiles(directory="app/files"), name="files")
app.mount("/userdata", StaticFiles(directory="app/userdata"), name="userdata")

async def load_json_file(file_path):
    async with async_open(file_path, mode="r") as file:
        data = await file.read()
        return json.loads(data)

class BaseResponseModel(BaseModel):
    status_code: int
    detail: str
    
    
# @app.exception_handler(StarletteHTTPException)
# async def http_exception_handler(request: Request, exc):

#     error_response = BaseResponseModel(
#         status_code=404,
#         detail="Not Found"
#     )
#     return JSONResponse(status_code=404, content=error_response.dict())

@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc):
    error_response = BaseResponseModel(
        status_code=exc.status_code,
        detail=exc.detail
    )
    return JSONResponse(status_code=exc.status_code, content=error_response.dict())

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    response_data = BaseResponseModel(
        status_code=400,
        detail="Invalid request"
    )
    return JSONResponse(status_code=400, content=response_data.dict())

@app.on_event("startup")
async def on_startup():
    await init_db()

@app.get("/api/v1")
async def pong():
    return {"message": "Hello World!"}

app.include_router(auth_router.router, prefix="/api/v1")
app.include_router(user_router.router, prefix="/api/v1")
app.include_router(pet_router.router, prefix="/api/v1")
app.include_router(country_router.router, prefix="/api/v1")
app.include_router(state_router.router, prefix="/api/v1")
app.include_router(city_router.router, prefix="/api/v1")

origins = [
    "http://localhost",
    "http://localhost:8000",
    "http://localhost:3000",
    "http://localhost:3001",
    "http://localhost:3002",
    "http://localhost:3003",
    "http://localhost:3004",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)