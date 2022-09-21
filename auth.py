import jwt
from fastapi.security import HTTPBearer
from passlib.context import CryptContext

SECRET_KEY = "SECRET_KEY"
ALGORITHM = "HS256"
security = HTTPBearer()

pwd_create = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verif_pwd(plain_pwd, hashed_pwd):
    return pwd_create.verify(plain_pwd, hashed_pwd)


def get_pwd(password):
    return pwd_create.hash(password)


def encoded_token(data: dict):
    to_encode = data.copy()
    encoded_tkn = jwt.encode(to_encode, SECRET_KEY, algorithm="HS256")
    return encoded_tkn


def decoded_token(tkn):
    to_decode = tkn
    decoded_tkn = jwt.decode(to_decode, SECRET_KEY, algorithms="HS256")
    return decoded_tkn
