from fastapi import Form, APIRouter, Depends, HTTPException
from fastapi import Request
from models import Senders
from database import db_annotated
from routers.users import get_current_user
from pydantic import BaseModel
from typing import Annotated
from starlette import status


router = APIRouter(
    prefix="/senders",
    tags=["SENDERS"],
)

class SenderModels(BaseModel):
    sender_name: str
    sender_phone: str
    sender_address: str

user_dependency = Annotated[dict, Depends(get_current_user)]

@router.get("/")
async def get_all_senders(user: get_current_user, db: db_annotated):
    senders = db.query(Senders).all()
    return {"senders": senders}


@router.post("/{sender_id}")
async def update_sender(
    current_user: user_dependency,
    db: db_annotated,
    sender_id: int,
    sender_name: str = Form(...),
    sender_phone: str = Form(...),
    sender_address: str = Form(...)
):
    if current_user["role"] != "delivery_hub":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")

    sender = db.query(Senders).filter(Senders.id == sender_id).first()
    if not sender:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sender not found")

    sender.sender_name = sender_name
    sender.sender_phone = sender_phone
    sender.sender_address = sender_address
    db.commit()
@router.post("/create")
async def create_sender(
    current_user: user_dependency,
    db: db_annotated,
    sender_name: str = Form(...),
    sender_phone: str = Form(...),
    sender_address: str = Form(...)
):
    if current_user["role"] != "delivery_hub":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")

    new_sender = Senders(
        sender_name=sender_name,
        sender_phone=sender_phone,
        sender_address=sender_address
    )
    db.add(new_sender)
    db.commit()