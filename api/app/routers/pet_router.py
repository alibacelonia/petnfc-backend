from fastapi import APIRouter, Depends, status
from pydantic import ValidationError
from sqlalchemy.orm import Session
from app.config.db import get_session
from app.schemas import PetBase, PetUpdate, PetDetails, PetPublicDisplay, PetTypeDetails, PetTypeBase
from typing import List
from app.repositories import pet_repo
from uuid import UUID
import qrcode
import os
import csv


router = APIRouter(
    prefix="/pet",
    tags=["pet"]
)

# Get a list of pet types e.g. Dog, Cat, etc...
@router.get('/pet-types', response_model=List[PetTypeDetails])
async def get_all_pet_types(db: Session = Depends(get_session)):
    return await pet_repo.get_all_pet_types(db)

# Get a list of pet types e.g. Dog, Cat, etc...
@router.get('/pet-type/{id}')
async def get_all_pet_types(id: int, db: Session = Depends(get_session)):
    return await pet_repo.get_pet_type_by_id(id, db)

# Add pet type
@router.post('/pet-type/add')
async def add_pet_type(request: PetTypeBase, db: Session = Depends(get_session)):
    return await pet_repo.add_pet_type(db, request)

# Update pet type by id
@router.post('/pet-type/update/{type_id}')
async def update_pet_type(type_id: int, request: PetTypeBase, db: Session = Depends(get_session)):
    return await pet_repo.update_pet_type(db, type_id, request)

# Get all records of pets
@router.get('/', response_model=List[PetDetails])
async def get_all_pets(db: Session = Depends(get_session)):
    return await pet_repo.get_all_pets(db)

# Get pet record using unique id from QR Code or NFC
@router.get('/{unique_id}/details')
async def get_pet_by_unique_id(unique_id: UUID, db: Session = Depends(get_session)):
    return await pet_repo.get_pet_by_unique_id(db, unique_id)
    
# Add new pet
@router.post('/', response_model=PetDetails)
async def add_pet(request: PetBase, db: Session = Depends(get_session)):
    return await pet_repo.add_pet(db, request)

# Update pet type by unique id
@router.post('/update/{id}')
async def update_pet_type(id: UUID, request: PetUpdate, db: Session = Depends(get_session)):
    return await pet_repo.update_pet(db, id, request)

# Generate QR for registered pets
@router.get('/generateqr')
def add_pet(db: Session = Depends(get_session)):
    pets = pet_repo.generate_qr(db)
    qr_code_data = []
    
    for pet_idx, pet in enumerate(pets):
        pet_id_str = str(pet_idx + 1).zfill(3)
        image_filename = f"qrcode-{pet_id_str}.png"
        image_path = os.path.join("qrs", image_filename)

        # Creating an instance of qrcode
        qr = qrcode.QRCode(
            version=1,
            box_size=32,
            border=4
        )
        
        qr.add_data(f"https://secure-petz.info/{pet.unique_id}")
        qr.make(fit=True)
        img = qr.make_image(fill='black', back_color='white')
        
        # Resizing the image to the desired size
        img = img.resize((1318, 1318))
        
        # Create the 'qrs' folder if it doesn't exist
        os.makedirs('qrs', exist_ok=True)
        img.save(image_path)

        qr_code_data.append({
            'filename': image_filename,
            'value': f"https://secure-petz.info/{pet.unique_id}"
        })

    csv_path = 'qrs/qrcodes.csv'
    with open(csv_path, mode='w', newline='') as file:
        fieldnames = ['filename', 'value']
        writer = csv.DictWriter(file, fieldnames=fieldnames)

        writer.writeheader()
        writer.writerows(qr_code_data)

    return {'message': 'QR codes generated successfully'}