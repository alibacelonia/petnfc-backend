from fastapi import APIRouter, Depends, status,Security
from pydantic import ValidationError
from sqlalchemy.orm import Session
from app.service.auth_service import AuthService
from app.config.db import get_session
from app.schemas import LoginSchema, PetBase, PetUnique, PetDetails, PetPublicDisplay, PetTypeDetails, PetTypeBase, RoleBase, UserBase, UserDisplayPublic
from typing import List
from app.repositories import user_repo
from uuid import UUID
import qrcode
import os
import csv
from app.repositories.auth_repo import JWTBearer, JWTRepo
from fastapi.security import HTTPAuthorizationCredentials

from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)

# Update user 
@router.post('/signin')
async def update_user(request_body: LoginSchema, db: Session = Depends(get_session)):
    token = await AuthService.logins_service(request_body, db)
    return ({"status_code": 200, "detail": "success", "data": {"token_type": "Bearer", "access_token": token}})

@router.post('/hashpassword')
async def update_user(request_body: str):
    return (pwd_context.hash(request_body),200)