from typing import Literal
from fastapi import APIRouter, Request
from pydantic import BaseModel, Field
from database import db_annotated
from models import Users
from passlib.context import CryptContext

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


@router.post("/create")
async def create_user(db: db_annotated, user: UsersModel):
    new_user = Users(
        username=user.username,
        hashed_password=bcrypt.hash(user.password),
        user_phone=user.phone,
        role=user.role
    )
    db.add(new_user)
    db.commit()

@router.get("/get")
async def get_user(db: db_annotated):
    pass
