from fastapi import APIRouter, Depends, Form, status, File, UploadFile
from fastapi.datastructures import FormData
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ValidationError
from sqlalchemy.orm import Session
from app.config.db import get_session
from app.schemas import Timezone, Translations, Country, State, City
from typing import Any, List, Optional
from app.repositories import state_repo
from fastapi.staticfiles import StaticFiles
import json
import httpx
import os

# from cachetools import TTLCache

# cache = TTLCache(maxsize=100, ttl=3600)

router = APIRouter(
    prefix="",
    tags=["state"]
)

# Get a list of pet types e.g. Dog, Cat, etc...
@router.get('/state')
async def get_all_states():
    return state_repo.get_all_states()

# Get a list of pet types e.g. Dog, Cat, etc...
@router.get('/state/{id}')
async def get_state_by_id(id: int):
    return state_repo.get_state_by_id(id)

@router.get('/country/{code}/state')
async def get_state_by_id(code: str):
    return state_repo.get_state_by_country_code(str(code).upper())

# Get a list of pet types e.g. Dog, Cat, etc...
@router.get('/state/search/{name}')
async def get_state_by_name(name: str):
    return state_repo.search_state(name)