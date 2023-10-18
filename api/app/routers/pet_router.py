from fastapi import APIRouter, Depends, Form, status, File, UploadFile
from fastapi.datastructures import FormData
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ValidationError
from sqlalchemy.orm import Session
from app.config.db import get_session
from app.schemas import PetBase, PetUpdate, PetDetails, PetPublicDisplay, PetTypeDetails, PetTypeBase, PetRegisterModel
from typing import Any, List, Optional
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

# Register Pet and Owner
@router.post('/register')
async def add_pet(
    guid: str = Form(...),
    firstname: str = Form(...),
    lastname: str = Form(...),
    email: str = Form(...),
    state: str = Form(...),
    state_code: str = Form(...),
    city: str = Form(...),
    city_id: str = Form(...),
    address: str = Form(...),
    postalCode: str = Form(...),
    phoneNo: str = Form(...),
    contactPerson: str = Form(...),
    contactPersonNo: str = Form(...),
        
    petType: str = Form(...),
    petGender: str = Form(...),
    petName: str = Form(...),
    petMicrochipNo: str = Form(...),
    petBreed: str = Form(...),
    petColor: str = Form(...),
    petBirthMonth: str = Form(...),
    petBirthYear: str = Form(...),
        
    username: str = Form(...),
    password: str = Form(...),
    file: UploadFile = File(...), 
    db: Session = Depends(get_session)):
    
    # form_data_dict = {
    #     "guid": guid,
    #     "firstname": firstname,
    #     "lastname": lastname,
    #     "email": email,    
    #     "state": state,
    #     "state_code": state_code,
    #     "city": city,
    #     "city_id": city_id,
    #     "address": address,
    #     "postalCode": postalCode,
    #     "phoneNo": phoneNo,
    #     "contactPerson": contactPerson,
    #     "contactPersonNo": contactPersonNo,
    #     "petType": petType,
    #     "petGender": petGender,
    #     "petName": petName,
    #     "petMicrochipNo": petMicrochipNo,
    #     "petBreed": petBreed,
    #     "petColor": petColor,
    #     "petBirthMonth": petBirthMonth,
    #     "petBirthYear": petBirthYear,
    #     "username": username,
    #     "password": password,
    # }   
    form_data = PetRegisterModel(
        guid=guid,
        firstname=firstname,
        lastname=lastname,
        email=email,    
        state=state,
        state_code=state_code,
        city=city,
        city_id=city_id,
        address=address,
        postalCode=postalCode,
        phoneNo=phoneNo,
        contactPerson=contactPerson,
        contactPersonNo=contactPersonNo,
        petType=petType,
        petGender=petGender,
        petName=petName,
        petMicrochipNo=petMicrochipNo,
        petWeight=0.0,
        petBreed=petBreed,
        petColor=petColor,
        petBirthMonth=petBirthMonth,
        petBirthYear=petBirthYear,
        username=username,
        password=password)
    return await pet_repo.register_pet(db, file, form_data)


# Update pet type by unique id
@router.post('/update/{id}')
async def update_pet_type(id: UUID, request: PetUpdate, db: Session = Depends(get_session)):
    # return await pet_repo.update_pet(db, id, request)
    return None

# Update pet type by unique id
@router.post('/update')
async def update_pet_type(
    guid: str = Form(...),
    ownerId: str = Form(...),
    petBehaviour: Optional[str] = Form(default=None),  # Add the new fields here
    petDescription: Optional[str] = Form(default=None),
    petWeight: str = Form(...),
    petType: str = Form(...),
    petGender: str = Form(...),
    petName: str = Form(...),
    petMicrochipNo: str = Form(...),
    petBreed: str = Form(...),
    petColor: str = Form(...),
    petBirthMonth: str = Form(...),
    petBirthYear: str = Form(...),
    file: Optional[UploadFile] = File(default=None), 
    db: Session = Depends(get_session)
):
    data = PetUpdate(
        behavior= petBehaviour,  # Include the new fields here
        description= petDescription,
        weight= petWeight,
        pet_type_id= petType,
        gender= petGender,
        name= petName,
        microchip_id= petMicrochipNo,
        breed= petBreed,
        color= petColor,
        date_of_birth_month= petBirthMonth,
        date_of_birth_year= petBirthYear,
        main_picture=file.filename if file else None
    )
    
    response = await pet_repo.update_pet(guid, ownerId, data, file, db)
    
    return response

# Generate QR for registered pets
@router.get('/generateqr')
async def add_pet(db: Session = Depends(get_session)):
    pets = await pet_repo.generate_qr(db)
    qr_code_data = []
    os.makedirs('qrs', exist_ok=True)
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
        img = qr.make_image(fill_color="#0D67B5", back_color='white')
        
        # Resizing the image to the desired size
        img = img.resize((1318, 1318))
        
        # Create the 'qrs' folder if it doesn't exist
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

@router.post('/restore-dump')
async def upload_sqldump(sql_dump: UploadFile = File(...), db: Session = Depends(get_session)):
    # Create a temporary directory to save the uploaded file
    temp_dir = "temp"
    os.makedirs(temp_dir, exist_ok=True)
    temp_file_path = os.path.join(temp_dir, sql_dump.filename)

    # Save the uploaded file
    with open(temp_file_path, "wb") as f:
        f.write(sql_dump.file.read())

    try:
        await pet_repo.execute_sql_from_dump(db, temp_file_path)
    except Exception as e:
        return {"error": f"Error executing SQL commands: {e}"}
    finally:
        # Clean up the temporary directory and file
        os.remove(temp_file_path)
        os.rmdir(temp_dir)

    return {"message": "SQL dump uploaded and processed successfully!"}