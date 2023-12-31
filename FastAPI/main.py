from fastapi import FastAPI, HTTPException, Depends
from typing import Annotated, List
from sqlalchemy.orm import Session
from pydantic import BaseModel
from database import SessionLocal, engine
import models
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

origins = [
    "http://localhost:3000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins= origins,
    allow_credentials= True,
    allow_methods=["*"],
    allow_headers=["*"]
)

class UserBase(BaseModel):
    name: str
    profile: str
    category: str
    description: str
    
class UserModel(UserBase):
    id: int
    class Config:
        orm_mode = True
        
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
db_dependency = Annotated[Session, Depends(get_db)]

models.Base.metadata.create_all(bind=engine)

@app.post("/userdata/", response_model=UserModel)
async def create_user(user: UserBase, db: db_dependency):
    db_user= models.user(**user.dict())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.get("/userdata/", response_model= List[UserModel])
async def read_user(db:db_dependency, skip: int=0, limit: int = 100):
    users= db.query(models.user).offset(skip).limit(limit).all()
    return users
