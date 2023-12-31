from os import abort
import os
import shutil
from fastapi import HTTPException, UploadFile, status
from pydantic import ValidationError
from sqlalchemy import asc
from sqlalchemy.orm import joinedload
# from sqlalchemy.orm.session import Session
from app.models.models import Pet, User, PetType
from uuid import UUID, uuid4

from app.repositories import user_repo

from app.schemas import PetBase, PetPublicDisplay, PetTypeBase, PetUpdate, PetRegisterModel

from sqlalchemy.exc import IntegrityError
from fastapi.responses import JSONResponse

from sqlmodel import select, or_
from sqlmodel import Session
from datetime import datetime
import re

from pathlib import Path
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

USERDATA_DIR = os.path.join("app", "userdata")
# Get all pet types
async def get_all_pet_types(db: Session):
    # return db.query(PetType).order_by(asc(PetType.type_id)).all()
    result = await db.execute(select(PetType).order_by(asc(PetType.type_id)))
    types = result.scalars().all()
    return types

async def get_pet_type_by_id(id: int, db: Session):
    pet_type = await db.get(PetType, id)
    
    if pet_type is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pet type not found")
    return ({"status_code": status.HTTP_200_OK, "detail": "OK", "data": pet_type}) 

# Add pet type
async def add_pet_type(db: Session, request: PetTypeBase):
    current_datetime = datetime.utcnow()  # Get the current UTC datetime
    type = PetType(type=request.type, created_at=current_datetime)
    
    try:
        db.add(type)
        await db.commit()
        await db.refresh(type)
        return type
    except IntegrityError as e:
        await db.rollback()
        # return ({"status_code": status.HTTP_409_CONFLICT, "detail": {"message":"Duplicate Pet Type"}}), 409
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Duplicate Pet Type")
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=status.WS_1011_INTERNAL_ERROR, detail=str(e))

# Update pet type
async def update_pet_type(db: Session, id: int, request: PetTypeBase):
    pet_type = await db.get(PetType, id)
    
    if pet_type is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pet type not found")
    
    pet_type.type = request.type
    pet_type.updated_at = datetime.utcnow()
    db.add(pet_type)
    await db.commit()
    await db.refresh(pet_type)
    return ({"status_code": status.HTTP_200_OK, "detail": "Updated"}) 

# Get all pets
async def get_all_pets(db: Session):
    # return db.query(Pet).order_by(asc(Pet.pet_id)).all()
    result = await db.execute(select(Pet))
    pets = result.scalars().all()
    return pets

# Get all pets by owner_id
async def get_all_pets_by_owner_id(id:int, db: Session):
    # return db.query(Pet).order_by(asc(Pet.pet_id)).all()
    result = await db.execute(select(Pet).where(Pet.owner_id == id))
    pets = result.scalars().all()
    return pets

# Add new pet
async def add_pet(db: Session, request: PetBase):
    current_datetime = datetime.utcnow()  # Get the current UTC datetime
    new_pet = Pet(
        pet_type_id=request.pet_type_id,
        name=request.name,
        microchip_id=request.microchip_id,
        gender=request.gender,
        breed=request.breed,
        color=request.color,
        date_of_birth_month=request.date_of_birth_month,
        date_of_birth_year=request.date_of_birth_year,
        owner_id=request.owner_id,
        created_at=current_datetime
    )
    try:
        db.add(new_pet)
        await db.commit()
        await db.refresh(new_pet)
        return new_pet
    # except IntegrityError as e:
    #     await db.rollback()
    #     raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Duplicate Pet")
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

async def add_user(db: Session, user: User):
    new_user = user
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

# Add new pet
async def register_pet(db: Session, file: UploadFile, request: PetRegisterModel):
    current_datetime = datetime.utcnow()  # Get the current UTC datetime
    unique_filename = cleanstr(file.filename)
    try:
        stmt = select(User).where(or_(User.email == request.email, User.phone_number == request.phoneNo, User.username == request.username))
        result = await db.exec(stmt)
        user = result.first()
        
        if user is None:
            ruser = User(
                username=request.username,
                password=pwd_context.hash(request.password),
                email=request.email,
                first_name=request.firstname,
                last_name=request.lastname,
                city=request.city,
                city_id=request.city_id,
                state=request.state,
                state_code=request.state_code,
                address=request.address,
                post_code=request.postalCode,
                phone_number=request.phoneNo,
                secondary_contact=request.contactPerson,
                secondary_contact_number=request.contactPersonNo,
                created_at=current_datetime,
                role_id=2
            )
            
            new_user: User = await add_user(db, ruser)
            
            pstmt = select(Pet).where(Pet.unique_id == request.guid)
            presult = await db.exec(pstmt)
            pet : Pet = presult.first()
            
            pet.owner_id=new_user.user_id
            pet.pet_type_id=request.petType
            pet.name=request.petName
            pet.microchip_id=request.petMicrochipNo
            pet.main_picture=unique_filename
            pet.gender=request.petGender
            pet.breed=request.petBreed
            pet.color=request.petColor
            pet.date_of_birth_month=request.petBirthMonth
            pet.date_of_birth_year=request.petBirthYear
            
            db.add(pet)
            await db.commit()
            await db.refresh(pet)
            
            
            # Pet profile picture path
            pet_profile_path = os.path.join(USERDATA_DIR, str(new_user.user_id), str(request.guid), "profile") 
            
            # Create the path 
            Path(pet_profile_path).mkdir(parents=True, exist_ok=True)
            
            # Read and copy the file
            with open(os.path.join(pet_profile_path, unique_filename), 'w+b') as buffer:
                shutil.copyfileobj(file.file, buffer)
            
            # pet_type = await db.get(PetType, request.petType)
            
            return{
                "status_code": status.HTTP_200_OK, 
                "detail": "success", 
                # "data": PetPublicDisplay(pet=pet, owner=new_user, pet_type=pet_type)
            }
            
        else:
            return {"status_code": status.HTTP_409_CONFLICT, "detail": "Owner details already registered."} 
    except Exception as e:
            return {"status_code": status.HTTP_500_INTERNAL_SERVER_ERROR, "detail": "Internal Server Error."} 
    

# Get pet by id
async def get_pet_by_id(db: Session, pet_id: int):
    pet = db.query(Pet).filter(Pet.pet_id == pet_id).first()
    if not pet:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pet not found")
    return pet

# Get pet by unique id
async def get_pet_by_unique_id(db: Session, unique_id: UUID):
    stmt = select(Pet, PetType, User).join(PetType, isouter=True).join(User, isouter=True).where(Pet.unique_id == unique_id)
    result = await db.exec(stmt)
    pet = result.fetchone()
    if pet is None:
        return {"status_code": status.HTTP_404_NOT_FOUND, "detail": "No record found"} 
    
    # Convert the SQLAlchemy result to a dictionary
    pet_data = dict(pet.Pet)
    owner_data = dict(pet.User) if pet.User else None
    petType = dict(pet.PetType) if pet.PetType else None

    # return {
    #     "status_code": status.HTTP_200_OK,
    #     "detail": "success",
    #     "data": {"pet": pet_data, "owner": owner_data}
    # }
    return ({"status_code": status.HTTP_200_OK, "detail": "success", "data": PetPublicDisplay(pet=pet_data, owner=owner_data, pet_type=petType)}) 


# Update pet
async def update_pet(unique_id, owner_id, request: PetUpdate, file: UploadFile, db: Session):
    current_datetime = datetime.utcnow()
    
    stmt = select(Pet).where(Pet.unique_id == unique_id)
    result = await db.exec(stmt)
    pet: Pet = result.first()
    
    if pet is None:
        return ({"status_code": status.HTTP_404_NOT_FOUND, "detail": "No record found"}) 
    
    if file:
        unique_filename = cleanstr(file.filename)
        pet.main_picture = unique_filename
        
        # Pet profile picture path
        pet_profile_path = os.path.join(USERDATA_DIR, str(owner_id), str(unique_id), "profile") 
        
        # Create the path 
        Path(pet_profile_path).mkdir(parents=True, exist_ok=True)
        
        # Read and copy the file
        with open(os.path.join(pet_profile_path, unique_filename), 'w+b') as buffer:
            shutil.copyfileobj(file.file, buffer)
            
    pet.updated_at=current_datetime
    pet.microchip_id = request.microchip_id
    pet.weight = request.weight
    pet.behavior = request.behavior
    pet.description = request.description
    pet.pet_type_id=request.pet_type_id
    pet.name=request.name
    pet.gender=request.gender
    pet.breed=request.breed
    pet.color=request.color
    pet.date_of_birth_month=request.date_of_birth_month
    pet.date_of_birth_year=request.date_of_birth_year
    
    
    # return pet
    try:
        db.add(pet)
        await db.commit()
        await db.refresh(pet)
        return ({"status_code": status.HTTP_200_OK, "detail": "success", "data": pet}) 
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=status.WS_1011_INTERNAL_ERROR, detail=str(e)) 

async def generate_qr(db: Session):
    return await get_all_pets(db)

async def execute_sql_from_dump(db: Session, sql_dump_file_path):
    with open(sql_dump_file_path, 'r') as f:
        sql_commands = f.read()

    # Split SQL commands based on the semicolon delimiter
    sql_commands_list = re.split(r';\s*', sql_commands)

    try:
        for sql_command in sql_commands_list:
            if sql_command.strip():
                await db.execute(sql_command)
        await db.commit()
        return {"status_code": status.HTTP_200_OK, "detail": "restored"} 
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=status.WS_1011_INTERNAL_ERROR, detail=str(e))
    
    
def cleanstr(filename):
    # Remove special characters and whitespaces and convert to lowercase
    filename = ''.join(c for c in filename if c.isalnum() or c in ',._').lower()
    
    # Remove file extension and get length
    name, ext = os.path.splitext(filename)
    name_length = len(name)
    
    # Check conditions and return result
    if name_length <= 16:
        return filename
    elif name_length > 16:
        return name[:16] + ext