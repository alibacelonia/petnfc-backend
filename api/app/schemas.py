from datetime import datetime
from fastapi import UploadFile
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
    city:str
    state:str
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
    city:str
    state:str
    address: str
    post_code: str
    phone_number: str
    secondary_contact: str
    secondary_contact_number: str
    
    class Config:
        orm_mode = True

class UserCreate(UserBase):
    created_at: Optional[datetime] = datetime.utcnow

class UserUpdateDetails(BaseModel):
    first_name: str
    last_name: str
    phone_number: str
    city_id:str
    city:str
    state_code:str
    state:str
    street_address: str
    post_code: str
    secondary_contact: str
    secondary_contact_number: str

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
    unique_id: UUID = None
    pet_type_id: int = None
    name: str = None
    microchip_id: str = None
    description: str = None
    behavior: str = None
    main_picture: str = None
    gender: str = None
    weight: float = None
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
    microchip_id: str = None
    description: str = None
    behavior: str = None
    main_picture: str = None
    gender: str = None
    weight: float = None
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
    pet_type: PetTypeDetails = None
    
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
    state:  str = None
    state_code:  str = None
    city:  str = None
    city_id:  str = None
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
    petWeight: float = None
    petColor:  str = None
    petBirthMonth: int = None
    petBirthYear: int = None
    
    username: str = None
    password: str = None
    
class Timezone(BaseModel):
    zoneName: str
    gmtOffset: int
    gmtOffsetName: str
    abbreviation: str
    tzName: str

class Translations(BaseModel):
    kr: str
    pt_BR: str
    pt: str
    nl: str
    hr: str
    fa: str
    de: str
    es: str
    fr: str
    ja: str
    it: str
    cn: str
    tr: str

class Country(BaseModel):
    id: int
    name: str
    iso3: str
    iso2: str
    numeric_code: str
    phone_code: str
    capital: str
    currency: str
    currency_name: str
    currency_symbol: str
    tld: str
    native: str
    region: str
    subregion: str
    timezones: List[Timezone]
    translations: Translations
    latitude: str
    longitude: str
    emoji: str
    emojiU: str
    
class State(BaseModel):
    id: int
    name: str
    country_id: int
    country_code: str
    country_name: str
    state_code: str
    type: str = None
    latitude: str
    longitude: str

class City(BaseModel):
    id: int
    name: str
    state_id: int
    state_code: str
    state_name: str
    country_id: int
    country_code: str
    country_name: str
    latitude: str
    longitude: str
    wikiDataId: str
    
class LoginSchema(BaseModel):
    username: str
    password: str