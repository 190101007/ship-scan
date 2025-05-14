from typing import Literal
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from starlette import status
from database import db_annotated
from models import Users
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer

router = APIRouter(
    prefix="/users",
    tags=["USERS"]
)

bcrypt = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UsersModel(BaseModel):
    username: str = Field(min_length=2, max_length=100)
    password: str = Field(min_length=7, max_length=100)
    phone: str = Field(max_length=12)
    role: Literal["delivery_hub", "delivery_guy"]


@router.post("/create", status_code=status.HTTP_201_CREATED)
async def create_user(db: db_annotated, user: UsersModel):
    new_user = Users(
        username=user.username,
        hashed_password=bcrypt.hash(user.password),
        user_phone=user.phone,
        role=user.role
    )
    db.add(new_user)
    db.commit()


@router.post("/auth", status_code=status.HTTP_200_OK)
async def authentication(username: str, password: str, db: db_annotated):
    user = db.query(Users).filter(Users.username == username).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found or incorrect password")
    if not bcrypt.verify(password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found or incorrect password")
    return user
