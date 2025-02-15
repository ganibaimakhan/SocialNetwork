
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Path
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from starlette import status
from models import Users, Profile, Posts, Comments, Likes
from database import SessionLocal
from routers.auth import get_current_user
from datetime import datetime

router = APIRouter(
prefix='/like',
    tags=['like']
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]
payload_dependency = Annotated[dict, Depends(get_current_user)]



@router.post("/create/{post_id}", status_code=status.HTTP_201_CREATED)
async def create_like(payload: payload_dependency, db: db_dependency,
                      post_id: int):
    if payload is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')
    checking = db.query(Likes).filter(Likes.user_id == payload.get('id')).filter(Likes.post_id == post_id).first()
    if checking:
        raise HTTPException(status_code=409, detail='Already Liked')
    like = Likes(post_id=post_id,
                user_id=payload.get('id'),
                created_at=datetime.now())

    db.add(like)
    db.commit()

@router.get('/get/{post_id}', status_code=status.HTTP_200_OK)
async def get_likes(payload: payload_dependency, db: db_dependency, post_id: int):
    if payload is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')
    post = db.query(Posts).filter(Posts.id == post_id).first()
    if post is None:
        raise HTTPException(status_code=404, detail='Post not found')
    likes = db.query(Likes).filter(Likes.post_id == post_id).all()

    return len(likes)

@router.delete("/delete/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(payload: payload_dependency, db: db_dependency, post_id: int):
    if payload is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')
    post = db.query(Posts).filter(Posts.id == post_id).first()
    if post is None:
        raise HTTPException(status_code=404, detail='Post not found')
    like = db.query(Likes).filter(Likes.user_id == payload.get('id')).filter(Likes.post_id == post_id).first()
    if like is None:
        raise HTTPException(status_code=404, detail='QQQ')
    db.query(Likes).filter(Likes.user_id == payload.get('id')).filter(Likes.post_id == post_id).delete()
    db.commit()
