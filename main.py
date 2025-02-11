from fastapi import FastAPI, Request, status
from models import Base
from database import engine
from routers import auth, profile, posts
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
app = FastAPI()

Base.metadata.create_all(bind=engine)

#app.mount("/static", StaticFiles(directory="TodoApp/static"), name="static")


app.include_router(auth.router)
app.include_router(profile.router)

app.include_router(posts.router)
{"message": "Hello, FastAPI!"}