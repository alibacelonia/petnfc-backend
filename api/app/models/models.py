from sqlmodel import SQLModel, Field, Relationship, ForeignKey
from typing import Optional, List
from datetime import datetime

from sqlalchemy import func
from sqlalchemy.dialects.postgresql import UUID
import uuid

# class UserRoles(SQLModel, table=True):
#     __tablename__ = 'user_roles'
#     user_id: int = Field(foreign_key='users.user_id', default=None, primary_key=True)
#     role_id: int = Field(foreign_key='roles.role_id', default=None, primary_key=True)
 
#     user: Optional["User"] = Relationship(back_populates='roles')
#     role: Optional["Roles"] = Relationship(back_populates='users')
    
class Roles(SQLModel, table=True):
    __tablename__ = 'roles'
    role_id: Optional[int] = Field(primary_key=True)
    role_name: str = Field(default=None, unique=True, nullable=False, index=True)
    
    users: Optional[List["User"]] = Relationship(back_populates='roles')
    
class User(SQLModel, table=True):
    __tablename__ = 'users'
    user_id: int = Field(primary_key=True)
    username: str = Field(default=None, unique=True, nullable=False)
    password: str = Field(default=None, nullable=False)
    email: str = Field(default=None, unique=True, nullable=False)
    first_name: str
    last_name: str
    address: str
    post_code: str
    phone_number: str
    secondary_contact: str
    secondary_contact_number: str
    is_verified: bool = Field(default=False, nullable=False)
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow, nullable=True)
    updated_at: Optional[datetime] = Field(default_factory=datetime.utcnow, nullable=True)
    role_id: int = Field(nullable=False, foreign_key='roles.role_id')

    pets: Optional[List["Pet"]] = Relationship(back_populates='owners')
    roles: Optional[List["Roles"]] = Relationship(back_populates='users')

class PetType(SQLModel, table=True):
    __tablename__ = 'pet_type'
    type_id: Optional[int] = Field(primary_key=True)
    type: str = Field(unique=True)
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow, nullable=True)
    updated_at: Optional[datetime] = Field(default_factory=datetime.utcnow, nullable=True)

    pets: Optional[List["Pet"]] = Relationship(back_populates='pet_type')
    
class Pet(SQLModel, table=True):
    __tablename__ = 'pets'
    pet_id: Optional[int] = Field(primary_key=True)
    unique_id: uuid.UUID = Field(default_factory=uuid.uuid4, unique=True, nullable=False)
    
    microchip_id: Optional[str] = Field(default=None, unique=True, nullable=True, index=True)
    name: Optional[str] = Field(default=None, nullable=True, index=True)
    gender: Optional[str] = Field(default=None, nullable=True, index=True)
    color: Optional[str] = Field(default=None, nullable=True, index=True)
    pet_type_id: Optional[int] = Field(default=None, foreign_key='pet_type.type_id', nullable=True)
    pet_type: Optional[PetType] = Relationship(back_populates='pets')
    breed: Optional[str] = Field(default=None, nullable=True)
    date_of_birth_month: Optional[int] = Field(default=None, nullable=True)
    date_of_birth_year: Optional[int] = Field(default=None, nullable=True)
    owner_id: Optional[int] = Field(default=None, foreign_key='users.user_id', nullable=True)
    owners: Optional[List[User]] = Relationship(back_populates='pets')
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow, nullable=True)
    updated_at: Optional[datetime] = Field(default_factory=datetime.utcnow, nullable=True)
