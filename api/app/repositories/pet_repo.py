from os import abort
from fastapi import HTTPException, status
from pydantic import ValidationError
from sqlalchemy import asc
from sqlalchemy.orm import joinedload
# from sqlalchemy.orm.session import Session
from app.models.models import Pet, User, PetType
from uuid import UUID

from app.schemas import PetBase, PetPublicDisplay, PetTypeBase, PetUpdate

from sqlalchemy.exc import IntegrityError
from fastapi.responses import JSONResponse

from sqlmodel import select
from sqlmodel import Session
from datetime import datetime


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
async def get_all_pets(db: Session, response_model=list[Pet]):
    # return db.query(Pet).order_by(asc(Pet.pet_id)).all()
    result = await db.execute(select(Pet))
    songs = result.scalars().all()
    return songs

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
    except IntegrityError as e:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Duplicate Pet")
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=status.WS_1011_INTERNAL_ERROR, detail=str(e))

# Get pet by id
async def get_pet_by_id(db: Session, pet_id: int):
    pet = db.query(Pet).filter(Pet.pet_id == pet_id).first()
    if not pet:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pet not found")
    return pet

# Get pet by unique id
async def get_pet_by_unique_id(db: Session, unique_id: UUID):
    stmt = select(Pet, User).join(User, isouter=True).where(Pet.unique_id == unique_id)
    result = await db.exec(stmt)
    pet = result.fetchone()
    if pet is None:
        return {"status_code": status.HTTP_404_NOT_FOUND, "detail": "No record found"} 
    
    # Convert the SQLAlchemy result to a dictionary
    pet_data = dict(pet.Pet)
    owner_data = dict(pet.User) if pet.User else None

    # return {
    #     "status_code": status.HTTP_200_OK,
    #     "detail": "success",
    #     "data": {"pet": pet_data, "owner": owner_data}
    # }
    return ({"status_code": status.HTTP_200_OK, "detail": "success", "data": PetPublicDisplay(pet=pet_data, owner=owner_data)}) 


# Update pet
async def update_pet(db: Session, id: UUID, request: PetUpdate):
    current_datetime = datetime.utcnow()
    
    stmt = select(Pet).where(Pet.unique_id == id)
    result = await db.exec(stmt)
    pet: Pet = result.first()
    
    if pet is None:
        return ({"status_code": status.HTTP_404_NOT_FOUND, "detail": "No record found"}) 
    
    pet.pet_type_id=request.pet_type_id
    pet.name=request.name
    pet.gender=request.gender
    pet.breed=request.breed
    pet.color=request.color
    pet.date_of_birth_month=request.date_of_birth_month
    pet.date_of_birth_year=request.date_of_birth_year
    pet.updated_at=current_datetime
    
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