from datetime import datetime
from pydantic import BaseModel
from typing import List, Optional
from uuid import UUID
from datetime import datetime

class RoleBase(BaseModel):
    role_name: str

class RoleCreate(RoleBase):
    pass

class RoleUpdate(RoleBase):
    pass

class Role(RoleBase):
    role_id: int

    class Config:
        orm_mode = True

class UserBase(BaseModel):
    username: str
    password: str
    email: str
    first_name: str
    last_name: str
    address: str
    post_code: str
    phone_number: str
    secondary_contact: str
    secondary_contact_number: str
    is_verified: Optional[bool]
    role_id: int

    class Config:
        orm_mode = True

class UserDisplayPublic(BaseModel):
    email: str
    first_name: str
    last_name: str
    address: str
    post_code: str
    phone_number: str
    secondary_contact: str
    secondary_contact_number: str
    
    class Config:
        orm_mode = True

class UserCreate(UserBase):
    created_at: Optional[datetime] = datetime.utcnow

class UserUpdateDetails(UserBase):
    pass

class UserUpdatePassword(BaseModel):
    password: str

class User(UserBase):
    user_id: int
    # roles: List[Role]

    class Config:
        orm_mode = True
        
class PetTypeBase(BaseModel):
    type: str
        
    class Config:
        orm_mode = True
        
class PetTypeUpdate(PetTypeBase):
    updated_at: datetime
        
    class Config:
        orm_mode = True
        
class PetTypeDetails(PetTypeBase):
    type_id: int
    type: str
    # created_at: datetime
    # updated_at: datetime
        
    class Config:
        orm_mode = True
        
class PetBase(BaseModel):
    pet_type_id: int = None
    name: str = None
    microchip_id: str = None
    gender: str = None
    breed: str = None
    color: str = None
    date_of_birth_month: int = None
    date_of_birth_year: int = None
    owner_id: int = None
    
    class Config:
        orm_mode = True
        
class PetCreate(PetBase):
    created_at: Optional[datetime]

class PetUpdate(BaseModel):
    pet_type_id: int = None
    name: str = None
    gender: str = None
    breed: str = None
    color: str = None
    date_of_birth_month: int = None
    date_of_birth_year: int = None
    
    class Config:
        orm_mode = True

class Pet(PetBase):
    pet_id: int

    class Config:
        orm_mode = True

class PetUnique(BaseModel):
    unique_id: UUID = None
    
    class Config:
        orm_mode = True

class PetPublicDisplay(BaseModel):
    pet: PetBase = None
    owner: UserDisplayPublic = None
    
    class Config:
        orm_mode = True

class PetDetails(PetBase):
    pet_id: int= None
    unique_id: UUID = None

    class Config:
        orm_mode = True

class PetRegisterModel(BaseModel):
    
    firstname:  str = None
    lastname:  str = None
    email:  str = None
    address:  str = None
    postalCode:  str = None
    phoneNo:  str = None
    contactPerson:  str = None
    contactPersonNo:  str = None

    guid: UUID = None
    petType: int = None
    petGender:  str = None
    petName:  str = None
    petMicrochipNo: str = None
    petBreed: str = None
    petColor:  str = None
    petBirthMonth: int = None
    petBirthYear: int = None
    
    username: str = None
    password: str = None