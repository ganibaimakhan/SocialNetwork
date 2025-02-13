
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Path
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from starlette import status
from models import Users, Profile
from database import SessionLocal
from routers.auth import get_current_user
from datetime import datetime

router = APIRouter(
prefix='/profile',
    tags=['profile']
)

class ProfileDTO(BaseModel):
    name: str
    surname: str
    date_of_birth: str
    is_verified: bool
    is_active: bool

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]
payload_dependency = Annotated[dict, Depends(get_current_user)]

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_profile(payload: payload_dependency, db: db_dependency,
                         new_profile: ProfileDTO):
    if payload is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')
    user = db.query(Users).filter(Users.id == payload.get('id')).first()
    user_profile = db.query(Profile).filter(Profile.id == user.profile_id).first()
    if user_profile is not None:
        raise HTTPException(status_code=409, detail='Profile already exists')
    user_profile = Profile(**new_profile.model_dump(),
                           user_id=payload.get('id'),
                           created_at=datetime.now(),
                           updated_at=datetime.now(),
                           last_login=datetime.now())
    #print(user_profile)
    db.add(user_profile)
    user_profile = db.query(Profile).filter(Profile.user_id == payload.get('id')).first()
    user.profile_id = user_profile.id
    db.add(user)
    db.commit()

@router.get('/', status_code=status.HTTP_200_OK)
async def get_profile(payload: payload_dependency, db: db_dependency):
    if payload is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')
    user = db.query(Users).filter(Users.id == payload.get('id')).first()
    user_profile = db.query(Profile).filter(Profile.id == user.profile_id).first()

    if user_profile is None:
        raise HTTPException(status_code=404, detail='Profile not found')
    return user_profile


@router.put("/", status_code=status.HTTP_204_NO_CONTENT)
async def change_profile(payload: payload_dependency, db: db_dependency,
                         new_profile: ProfileDTO):
    if payload is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')
    user = db.query(Users).filter(Users.id == payload.get('id')).first()
    user_profile = db.query(Profile).filter(Profile.id == user.profile_id).first()

    if user_profile is None:
        raise HTTPException(status_code=404, detail='Profile not found')
    user_profile.name = new_profile.name
    user_profile.surname = new_profile.surname
    user_profile.date_of_birth = new_profile.date_of_birth
    user_profile.is_verified = new_profile.is_verified
    user_profile.is_active = new_profile.is_active
    user_profile.updated_at = datetime.now()

    db.add(user_profile)
    db.commit()


@router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_profile(payload: payload_dependency, db: db_dependency):
    if payload is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')
    user = db.query(Users).filter(Users.id == payload.get('id')).first()
    user_profile = db.query(Profile).filter(Profile.id == user.profile_id).first()
    if user_profile is None:
        raise HTTPException(status_code=404, detail='Profile not found')
    db.query(Profile).filter(Profile.id == payload.get('profile_id')).delete()
    user.profile_id = None
    db.add(user_profile)
    db.commit()

