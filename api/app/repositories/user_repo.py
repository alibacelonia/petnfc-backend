from os import abort
from typing import List, Optional
from fastapi import Depends, HTTPException, status
from pydantic import ValidationError
from sqlalchemy import asc
from sqlalchemy.orm import joinedload
from app.config.db import get_session
# from sqlalchemy.orm.session import Session
from app.models.models import Pet, User, Roles
from uuid import UUID

from app.schemas import RoleBase, Role, RoleCreate, RoleUpdate, UserBase, UserCreate, UserUpdateDetails

from sqlalchemy.exc import IntegrityError
from fastapi.responses import JSONResponse

from sqlmodel import select
from sqlmodel import Session
from datetime import datetime

dbconn = get_session

async def find_by_username(username: str, db: Session):
    query = select(User).where(User.username == username)
    return (await db.execute(query)).scalar_one_or_none()

# Get all pet types
async def get_all_user_roles(db: Session):
    result = await db.execute(select(Roles).order_by(asc(Roles.role_id)))
    types = result.scalars().all()
    return types

async def get_user_role_by_id(id: int, db: Session):
    user_role = await db.get(Roles, id)
    
    if user_role is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User role not found")
    return ({"status_code": status.HTTP_200_OK, "detail": "OK", "data": user_role}) 

# Add pet type
async def add_user_role(db: Session, request: RoleBase):
    user_role = Roles(role_name=request.role_name)
    
    try:
        db.add(user_role)
        await db.commit()
        await db.refresh(user_role)
        return user_role
    except IntegrityError as e:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Duplicate User Role")
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=status.WS_1011_INTERNAL_ERROR, detail=str(e))

# Update pet type
async def update_user_role(db: Session, id: int, request: RoleBase):
    user_role : Roles = await db.get(Roles, id)
    
    if user_role is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User role not found")
    
    user_role.role_name = request.role_name
    db.add(user_role)
    await db.commit()
    await db.refresh(user_role)
    return ({"status_code": status.HTTP_200_OK, "detail": "Updated"}) 

# Get all pets
async def get_all_users(db: Session):
    result = await db.execute(select(User))
    users = result.scalars().all()
    return users

# Add new pet
async def add_user(db: Session, request: UserBase):
    current_datetime = datetime.utcnow()  # Get the current UTC datetime
    new_user = User(
        username=request.username,
        password=request.password,
        email=request.email,
        first_name=request.first_name,
        last_name=request.last_name,
        address=request.address,
        post_code=request.post_code,
        phone_number=request.phone_number,
        secondary_contact=request.secondary_contact,
        secondary_contact_number=request.secondary_contact_number,
        created_at=current_datetime,
        role_id=request.role_id
    )
    try:
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)
        return new_user
    except IntegrityError as e:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Duplicate User")
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=status.WS_1011_INTERNAL_ERROR, detail=str(e))

# Get pet by id
async def get_user_by_id(db: Session, id: int):
    user = await db.get(User, id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


# Update User
async def update_user(username: str, request: UserUpdateDetails, db: Session):
    stmt = select(User).where(User.username == username)
    result = await db.exec(stmt)
    user: User = result.first()
    
    if user is None:
        return ({"status_code": status.HTTP_404_NOT_FOUND, "detail": "No record found"}) 
    
    user.first_name = request.first_name
    user.last_name = request.last_name
    user.phone_number = request.phone_number
    user.state = request.state
    user.state_code = request.state_code
    user.city = request.city
    user.city_id = request.city_id
    user.address = request.street_address
    user.post_code = request.post_code
    user.secondary_contact = request.secondary_contact
    user.secondary_contact_number = request.secondary_contact_number
    
    try:
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return ({"status_code": status.HTTP_200_OK, "detail": "success", "data": user}) 
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=status.WS_1011_INTERNAL_ERROR, detail=str(e)) 