from datetime import datetime, timedelta
from typing import Optional
from jose import jwt
from jose.exceptions import ExpiredSignatureError
from fastapi import Request, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.config.db import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES




class JWTRepo:

    def __init__(self, data: dict = {}, token: str = None):
        self.data = data
        self.token = token

    def generate_token(self, expires_delta: Optional[timedelta] = None):
        to_encode = self.data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(days=1)
        to_encode.update({"exp": expire})
        encode_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encode_jwt

    def decode_token(self):
        try:
            decode_token = jwt.decode(self.token, SECRET_KEY, algorithms=[ALGORITHM])
            if decode_token["exp"] >= datetime.utcnow():
                return decode_token
            else:
                return None
        except ExpiredSignatureError:
            return None
        except :
            return None

    @staticmethod
    def extract_token(token: str):
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])


class JWTBearer(HTTPBearer):

    def __init__(self, auto_error: bool = False):
        super(JWTBearer, self).__init__(auto_error=auto_error)

    async def __call__(self, request: Request):
        credentials: HTTPAuthorizationCredentials = await super(JWTBearer, self).__call__(request)
        if credentials:
            if not credentials.scheme == "Bearer":
                raise HTTPException(
                    status_code=403, detail="Invalid authentication schema.")
            if not self.verify_jwt(credentials.credentials):
                raise HTTPException(
                    status_code=403, detail="Invalid token or expired token.")
            return credentials.credentials
        else:
            raise HTTPException(
                status_code=403, detail="Invalid authorization code.")

    @staticmethod
    def verify_jwt(jwt_token: str):
        try:
            decoded = jwt.decode(jwt_token, SECRET_KEY, algorithms=[ALGORITHM]) 
        except Exception:
            raise HTTPException(
                status_code=403, detail="Invalid authorization code.")
        
        return True if decoded is not None else False
