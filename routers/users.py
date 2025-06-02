from typing import Literal, Annotated
from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel, Field
from starlette import status
from database import db_annotated
from models import Users
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import jwt, JWTError
from datetime import timedelta, timezone, datetime
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

router = APIRouter(
    prefix="/users",
    tags=["USERS"]
)

templates = Jinja2Templates(directory="templates")

bcrypt = CryptContext(schemes=["bcrypt"], deprecated="auto")

SECRET_KEY = "haZd%o_>>d9scU57?cuAv|HZGBENME"
ALGORITHM = "HS256"

# Token alma için OAuth2 yapılandırması
oauth2_bearer = OAuth2PasswordBearer("/users/token")


class UsersModel(BaseModel):
    username: str = Field(min_length=2, max_length=100)
    password: str  # = Field(min_length=7, max_length=100)
    phone: str = Field(max_length=12)
    address: str  # = Field(min_length = 3 , max_length=100)
    role: Literal["delivery_hub", "delivery_guy"]


class TokenModel(BaseModel):
    access_token: str
    token_type: str


def authentication(username: str, password: str, db: db_annotated):
    user = db.query(Users).filter(Users.username == username).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found or incorrect password")
    if not bcrypt.verify(password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found or incorrect password")
    return user


def create_access_token(user_id: str, user_role: str, expires_delta: timedelta):
    expires = datetime.now(timezone.utc) + expires_delta
    payload = {"user_id": user_id, "role": user_role, "expires": expires.timestamp()}
    token = jwt.encode(payload, SECRET_KEY, ALGORITHM)
    return token


@router.post("/token", response_model=TokenModel)
async def login_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: db_annotated):
    user = authentication(form_data.username, form_data.password, db)
    token = create_access_token(user.id, user.role, timedelta(minutes=60))
    return {"access_token": token, "token_type": "Bearer"}


@router.get("/login")
async def login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


async def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("user_id")
        role = payload.get("role")
        if user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
        else:
            return {"user_id": user_id, "role": role}
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

user_dependency = Annotated[dict, Depends(get_current_user)]


@router.get("/dashboard")
async def dashboard(current_user: user_dependency, request: Request):
    """
    GET /users/dashboard:
    - get_current_user ile token’dan çözülen user bilgisi alınır.
    - role’a göre hub-main veya guy-main şablonunu döner.
    """
    role = current_user["role"]
    if role == "delivery_hub":
        return templates.TemplateResponse("hub-main.html", {"request": request})
    elif role == "delivery_guy":
        return templates.TemplateResponse("guy-main.html", {"request": request})
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized role")



@router.post("/create", status_code=status.HTTP_201_CREATED)
async def create_user(current_user: user_dependency,db: db_annotated, user: UsersModel ):
    role = current_user["role"]

    try:
        if role == "delivery_hub":
            new_user = Users(
                username=user.username,
                hashed_password=bcrypt.hash(user.password),
                user_phone=user.phone,
                address=user.address,
                role=user.role
            )

            db.add(new_user)
            db.commit()
            return {"message": "User created successfully"}
        else:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized User.")

    except:
        return RedirectResponse(url="/users/login")

