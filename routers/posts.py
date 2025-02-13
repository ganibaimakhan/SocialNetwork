
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Path
from pydantic import BaseModel, Field, ConfigDict
from sqlalchemy.orm import Session
from starlette import status
from models import Users, Profile, Posts, Comments
from database import SessionLocal
from routers.auth import get_current_user
from datetime import datetime


router = APIRouter(
prefix='/posts',
    tags=['posts']
)


class PostDTO(BaseModel):
    title: str
    text: str

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]
payload_dependency = Annotated[dict, Depends(get_current_user)]


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_post(payload: payload_dependency, db: db_dependency,
                      new_post: PostDTO):
    if payload is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')
    user_post = Posts(**new_post.model_dump(),
                      user_id=payload.get('id'),
                      created_at=datetime.now(),
                      updated_at=datetime.now())

    db.add(user_post)
    db.commit()

@router.get('/', status_code=status.HTTP_200_OK)
async def get_post(payload: payload_dependency, db: db_dependency):
    if payload is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')
    user_posts = db.query(Posts).filter(Posts.user_id == payload.get('id')).all()
    if user_posts is None:
        raise HTTPException(status_code=404, detail='Posts not found')

    return user_posts


@router.put("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def change_post(payload: payload_dependency, db: db_dependency,
                      new_post: PostDTO, id: int):
    if payload is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')
    user_post = db.query(Posts).filter(Posts.user_id == payload.get('id')).filter(Posts.id == id).first()
    if user_post is None:
        raise HTTPException(status_code=404, detail='Post not found')
    user_post.title = new_post.title
    user_post.text = new_post.text
    user_post.updated_at = datetime.now()

    db.add(user_post)
    db.commit()


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(payload: payload_dependency, db: db_dependency, id: int):
    if payload is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')
    user_post = db.query(Posts).filter(Posts.user_id == payload.get('id')).filter(Posts.id == id).first()
    if user_post is None:
        raise HTTPException(status_code=404, detail='Post not found')
    db.query(Posts).filter(Posts.user_id == payload.get('id')).filter(Posts.id == id).delete()
    db.commit()
