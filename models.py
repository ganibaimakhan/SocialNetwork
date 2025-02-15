from sqlalchemy.orm import relationship

from database import Base
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime


class Users(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True)
    password = Column(String)
    role = Column(String)
    profile_id = Column(Integer, ForeignKey('profile.id'), default=None)
    #last_login = Column(DateTime)

class Profile(Base):
    __tablename__ = 'profile'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    name = Column(String)
    surname = Column(String)
    date_of_birth = Column(String)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    is_verified = Column(Boolean, default=False)
    last_login = Column(DateTime)
    is_active = Column(Boolean, default=True)

class Posts(Base):
    __tablename__ = 'posts'

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    text = Column(String)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    user_id = Column(Integer, ForeignKey('users.id'))
    #comments = relationship('Comments', back_populates='posts', lazy='joined')

class Comments(Base):
    __tablename__ = 'comments'

    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, ForeignKey('posts.id'))
    text = Column(String)
    user_id = Column(Integer, ForeignKey('users.id'))
    #posts = relationship('Posts', back_populates='comments')

class Likes(Base):
    __tablename__ = 'likes'
    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, ForeignKey('posts.id'))
    user_id = Column(Integer, ForeignKey('users.id'))
    created_at = Column(DateTime)

class Followers(Base):
    __tablename__ = 'followers'
    follower_id = Column(Integer, ForeignKey('users.id'), primary_key=True)
    following_id = Column(Integer, ForeignKey('users.id'), primary_key=True)
    created_at = Column(DateTime)


