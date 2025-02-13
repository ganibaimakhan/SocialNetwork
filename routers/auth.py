from datetime import timedelta, datetime
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from models import Users, Profile
from passlib.context import CryptContext
from database import SessionLocal
from typing import Annotated
from sqlalchemy.orm import Session
from starlette import status
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import jwt, JWTError
from fastapi.templating import Jinja2Templates
from dotenv import load_dotenv
import os

router = APIRouter(
    prefix='/auth',
    tags=['auth']
)
load_dotenv(dotenv_path=".env")

SECRET_KEY = os.getenv('SECRET_KEY')
ALGORITHM = "HS256"
#if not SECRET_KEY:
  #  raise ValueError("SECRET_KEY is missing! Check your .env file.")


bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
oauth2_bearer = OAuth2PasswordBearer(tokenUrl='auth/token')

class CreateUserRequest(BaseModel):
    username: str
    email: str
    password: str
    role: str

class Token(BaseModel):
    access_token: str
    token_type: str



def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_access_token(username: str, user_id: int, role: str, expires_delta: timedelta):
    encode = {'username': username, 'id': user_id, 'role': role}
    expires = datetime.utcnow() + expires_delta
    encode.update({'exp': expires})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)

db_dependency = Annotated[Session, Depends(get_db)]

templates = Jinja2Templates(directory='TodoApp/templates')

### Endpoints ###
def authenticate_user(username: str, password: str, db):
    user = db.query(Users).filter(Users.username == username).first()
    if not user:
        return None
    if not bcrypt_context.verify(password, user.password):
        return None
    return user


async def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get('username')
        user_id: int = payload.get('id')
        user_role: str = payload.get('role')
        if username is None or user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail='Could not validate user.')
        return {'username': username, 'id': user_id, 'user_role': user_role}
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Could not validate user.')

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_user(db: db_dependency,
                      create_user_request: CreateUserRequest):
    create_user_model = Users(
        email=create_user_request.email,
        username=create_user_request.username,
        role=create_user_request.role,
        password=bcrypt_context.hash(create_user_request.password)

    )

    db.add(create_user_model)
    db.commit()

@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
                                 db: db_dependency):
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Could not validate user.')
    token = create_access_token(user.username, user.id, user.role, timedelta(minutes=20))
    user_table = db.query(Users).filter(Users.id == user.id).first()
    user_profile = db.query(Profile).filter(Profile.id == user_table.profile_id).first()
    user_profile.last_login = datetime.now()
    db.add(user_profile)
    db.commit()
    return {'access_token': token, 'token_type': 'bearer'}