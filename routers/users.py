from typing import Literal, Annotated
from fastapi import APIRouter, HTTPException, Depends, Request, Response
from pydantic import BaseModel, Field
from starlette import status
from database import db_annotated
from models import Users
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import jwt, JWTError
from datetime import timedelta, timezone, datetime
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi import Form

router = APIRouter(
    prefix="/users",
    tags=["USERS"]
)

templates = Jinja2Templates(directory="templates")

bcrypt = CryptContext(schemes=["bcrypt"], deprecated="auto")

SECRET_KEY = "haZd%o_>>d9scU57?cuAv|HZGBENME"
ALGORITHM = "HS256"


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
async def login_access_token(response: Response, form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
                             db: db_annotated):
    user = authentication(form_data.username, form_data.password, db)
    token = create_access_token(user.id, user.role, timedelta(minutes=60))
    response.set_cookie(
        key="access_token",
        value=f"Bearer {token}",
        httponly=True,
        samesite="lax",
        secure=False  # Prod ortamda HTTPS kullanıyorsanız True yapın
    )
    return {"access_token": token, "token_type": "Bearer"}


def get_token_from_cookie(request: Request) -> str:
    token_cookie = request.cookies.get("access_token")
    if not token_cookie:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    # "Bearer <token>" → "<token>"
    try:
        return token_cookie.split(" ")[1]
    except:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token format"
        )


async def get_current_user(
        token: Annotated[str, Depends(get_token_from_cookie)]
) -> dict:
    """
    - Cookie’den alınan token’ı decode eder.
    - Payload içindeki user_id ve role’ü çekip, DB’den kullanıcıyı doğrular.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("user_id")
        role: str = payload.get("role")
        if user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    # DB’den kullanıcı obje’sini alabilirsiniz, ancak biz sadece user_id ve role döndürüyoruz:
    return {"user_id": user_id, "role": role}


user_dependency = Annotated[dict, Depends(get_current_user)]


@router.get("/login")
async def login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@router.get("/logout")
async def logout(response: Response):
    """
    - Cookie’yi siliyor ve kullanıcıyı login sayfasına yönlendiriyoruz.
    """
    response.delete_cookie("access_token")
    return RedirectResponse(url="/users/login", status_code=status.HTTP_302_FOUND)


@router.get("/dashboard")
async def dashboard(request: Request, current_user: user_dependency):
    """
    - Rolüne göre hub-main.html veya guy-main.html döner.
    - Token cookie’de valid ise sayfa render edilir, aksi hâlde 401 atar.
    """
    role = current_user["role"]
    if role == "delivery_hub":
        return templates.TemplateResponse("hub-main.html", {"request": request})
    elif role == "delivery_guy":
        return templates.TemplateResponse("guy-main.html", {"request": request})
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Yetkisiz erişim"
        )


@router.get("/create")
async def create_user_form(request: Request):
    return templates.TemplateResponse("create-user.html", {"request": request})


@router.post("/create", status_code=status.HTTP_201_CREATED)
async def create_user(request: Request,
                      current_user: user_dependency,
                      db: db_annotated,
                      username: str = Form(...),
                      password: str = Form(...),
                      phone: str = Form(None),
                      address: str = Form(None),
                      role: Literal["delivery_hub", "delivery_guy"] = Form(...)
                      ):
    if current_user["role"] != "delivery_hub":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")

    new_user = Users(
        username=username,
        hashed_password=bcrypt.hash(password),
        user_phone=phone,
        address=address,
        role=role
    )
    db.add(new_user)
    db.commit()
    return templates.TemplateResponse(
        "hub-main.html",
        {
            "request": request,
            "success": "Yeni kullanıcı başarıyla oluşturuldu."
        }
    )