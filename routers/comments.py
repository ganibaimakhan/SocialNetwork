
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Path
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session, joinedload
from starlette import status
from models import Users, Profile, Posts, Comments
from database import SessionLocal
from routers.auth import get_current_user
from datetime import datetime

router = APIRouter(
prefix='/comments',
    tags=['comments']
)


class CommentDTO(BaseModel):
    post_id: int
    text: str


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]
payload_dependency = Annotated[dict, Depends(get_current_user)]


@router.post("/create", status_code=status.HTTP_201_CREATED)
async def create_post(payload: payload_dependency, db: db_dependency,
                      comment: str, post_id: int):
    if payload is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')
    user_comment = Comments(post_id=post_id,
                            text=comment,
                            user_id=payload.get('id'))
    if db.query(Posts).filter(Posts.id == post_id).first() is None:
        raise HTTPException(status_code=404, detail='Post not found')
    db.add(user_comment)
    db.commit()

@router.get('/posts', status_code=status.HTTP_200_OK)
async def get_post_with_comments(payload: payload_dependency, db: db_dependency):
    if payload is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')
    posts = db.query(Posts).filter(Posts.user_id == payload.get('id')).options(joinedload(Posts.comments)).all()

    return posts
