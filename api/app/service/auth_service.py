from sqlmodel import Session
from app.schemas import LoginSchema
from app.repositories import user_repo
from uuid import uuid4
from fastapi import HTTPException

from passlib.context import CryptContext
from app.repositories.auth_repo import JWTRepo


# Encrypt password
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class AuthService:

    @staticmethod
    async def logins_service(login: LoginSchema, db: Session):
        _username = await user_repo.find_by_username(login.username, db)

        if _username is not None:
            if not pwd_context.verify(login.password, _username.password):
                raise HTTPException(
                    status_code=400, detail="Invalid Password !")
            return JWTRepo(data={"username": _username.username}).generate_token()
        raise HTTPException(status_code=404, detail="Username not found !")
