from passlib.context import CryptContext
from jose import jwt
import datetime
from fastapi.security.oauth2 import OAuth2PasswordBearer
from fastapi import Depends

oauth2_schema = OAuth2PasswordBearer(tokenUrl="/api/admin/auth/login")

pwd_context = CryptContext(schemes=['bcrypt'], deprecated="auto")
secret_key = "sdrtfhyuij"


def create_access_token(admin_data: dict):
    admin_data["exp"] = datetime.datetime.utcnow() + datetime.timedelta(minutes=15)
    token = jwt.encode(admin_data, secret_key, "HS256")
    return token


def verify_access_token(token: str):
    admin_data = jwt.decode(token, secret_key, algorithms=["HS256"])
    return admin_data


def get_current_admin(token=Depends(oauth2_schema)):
    data = verify_access_token(token)
    return data
