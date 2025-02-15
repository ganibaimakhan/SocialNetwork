from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Path
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from starlette import status
from models import Users, Profile, Posts, Comments, Likes, Followers
from database import SessionLocal
from routers.auth import get_current_user
from datetime import datetime

router = APIRouter(
prefix='/follow',
    tags=['follow']
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]
payload_dependency = Annotated[dict, Depends(get_current_user)]

@router.post("/follow/{following_id}", status_code=status.HTTP_201_CREATED)
async def to_follow(payload: payload_dependency, db: db_dependency,
                      following_id: int):
    if payload is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')
    if db.query(Users).filter(Users.id == following_id).first() is None:
        raise HTTPException(status_code=404, detail='Useer not found')
    #if db.query(Followers).filter(Followers.follower_id == payload.get('id')).filter(Followers.following_id == following_id).first():
    #    raise HTTPException(status_code=409, detail='Already followed')
    follow = Followers(follower_id=payload.get('id'),
                following_id=following_id,
                created_at=datetime.now())

    db.add(follow)
    db.commit()


@router.post("/unfollow/{following_id}", status_code=status.HTTP_201_CREATED)
async def to_unfollow(payload: payload_dependency, db: db_dependency,
                    following_id: int):
    if payload is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')
    if db.query(Users).filter(Users.id == following_id).first() is None:
        raise HTTPException(status_code=404, detail='Useer not found')
    if db.query(Followers).filter(Followers.follower_id == payload.get('id')).filter(Followers.following_id == following_id).first() is None:
        raise HTTPException(status_code=404, detail='Not followed')
    db.query(Followers).filter(Followers.follower_id == payload.get('id')).filter(
        Followers.following_id == following_id).delete()
    db.commit()

@router.get("/{following_id}", status_code=status.HTTP_200_OK)
async def get_followers(payload: payload_dependency, db: db_dependency,
                    following_id: int):
    if payload is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')
    if db.query(Users).filter(Users.id == following_id).first() is None:
        raise HTTPException(status_code=404, detail='User not found')
    followers = db.query(Followers).filter(Followers.following_id == following_id).all()
    follower_ids = [follower.follower_id for follower in followers]
    return follower_ids




