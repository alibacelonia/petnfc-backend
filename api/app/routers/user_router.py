from fastapi import APIRouter, Depends, Form, HTTPException, status,Security
from pydantic import ValidationError
from sqlalchemy.orm import Session
from app.service.auth_service import AuthService
from app.config.db import get_session
from app.schemas import LoginSchema, PetBase, PetUnique, PetDetails, PetPublicDisplay, PetTypeDetails, PetTypeBase, RoleBase, UserBase, UserDisplayPublic, UserUpdateDetails
from typing import List
from app.repositories import user_repo, pet_repo
from uuid import UUID
import qrcode
import os
import csv
from app.repositories.auth_repo import JWTBearer, JWTRepo
from fastapi.security import HTTPAuthorizationCredentials

from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

router = APIRouter(
    prefix="/user",
    tags=["user"],
    dependencies=[Depends(JWTBearer())]
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
async def get_user_by_id(id: int, db: Session = Depends(get_session), credentials: HTTPAuthorizationCredentials = Security(JWTBearer())):
    return await user_repo.get_user_by_id(db, id)
    
# Get user by id
@router.get('/profile/details/')
async def get_user_profile(credentials: HTTPAuthorizationCredentials = Security(JWTBearer()), db: Session = Depends(get_session)):
    try:
        token = JWTRepo.extract_token(credentials)
        return await user_repo.find_by_username(token['username'], db)
        # return token
    except HTTPException as e:
        # Customize the response here
        return {"status": "Forbidden", "message": "Authentication required."}
    
# Add new user
@router.post('/', response_model=UserDisplayPublic)
async def add_user(request: UserBase, db: Session = Depends(get_session)):
    return await user_repo.add_user(db, request)

# Update user 
@router.post('/update/profile')
async def update_user(
    first_name: str = Form(...),
    last_name: str = Form(...),
    state: str = Form(...),
    state_code: str = Form(...),
    city: str = Form(...),
    city_id: str = Form(...),
    street_address: str = Form(...),
    post_code: str = Form(...),
    phone_number: str = Form(...),
    secondary_contact: str = Form(...),
    secondary_contact_number: str = Form(...),
    credentials: HTTPAuthorizationCredentials = Security(JWTBearer()), 
    db: Session = Depends(get_session)):
    try:
        token = JWTRepo.extract_token(credentials)
        data = UserUpdateDetails(
            first_name= first_name, 
            last_name= last_name, 
            state=state,
            state_code=state_code,
            city=city,
            city_id=city_id,
            street_address=street_address,
            post_code=post_code,
            phone_number=phone_number,
            secondary_contact=secondary_contact,
            secondary_contact_number=secondary_contact_number
        )
        return await user_repo.update_user(token['username'], data, db)
        # return data
        # return token
    except HTTPException as e:
        # Customize the response here
        return {"status": "Forbidden", "message": "Authentication required."}


# Get all records of pets
@router.get('/{owner_id}/pets', response_model=List[PetDetails])
async def get_all_pets_by_owner_id(owner_id:int, db: Session = Depends(get_session)):
    return await pet_repo.get_all_pets_by_owner_id(owner_id, db)