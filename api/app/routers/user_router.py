from fastapi import APIRouter, Depends, status
from pydantic import ValidationError
from sqlalchemy.orm import Session
from app.config.db import get_session
from app.schemas import PetBase, PetUnique, PetDetails, PetPublicDisplay, PetTypeDetails, PetTypeBase, RoleBase, UserBase, UserDisplayPublic
from typing import List
from app.repositories import user_repo
from uuid import UUID
import qrcode
import os
import csv


router = APIRouter(
    prefix="/user",
    tags=["user"]
)

# Get a list of pet types e.g. Dog, Cat, etc...
@router.get('/user-roles')
async def get_all_user_roles(db: Session = Depends(get_session)):
    return await user_repo.get_all_user_roles(db)

# Get a user role by id
@router.get('/user-role/{id}')
async def get_user_role_by_id(id: int, db: Session = Depends(get_session)):
    return await user_repo.get_user_role_by_id(id, db)

# Add user role
@router.post('/user-role/add')
async def add_user_role(request: RoleBase, db: Session = Depends(get_session)):
    return await user_repo.add_user_role(db, request)

# Update user role by id
@router.post('/user-role/update/{id}')
async def update_user_role(id: int, request: RoleBase, db: Session = Depends(get_session)):
    return await user_repo.update_user_role(db, id, request)

# Get all users
@router.get('/')
async def get_all_users(db: Session = Depends(get_session)):
    return await user_repo.get_all_users(db)

# Get user by id
@router.get('/{id}/details')
async def get_user_by_id(id: int, db: Session = Depends(get_session)):
    return await user_repo.get_user_by_id(db, id)
    
# Add new user
@router.post('/', response_model=UserDisplayPublic)
async def add_user(request: UserBase, db: Session = Depends(get_session)):
    return await user_repo.add_user(db, request)

# Update user 
@router.post('/update/{id}')
async def update_user(id: int, db: Session = Depends(get_session)):
    return await user_repo.update_user(db, id)