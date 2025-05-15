from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from starlette.responses import RedirectResponse
from database import engine
from models import Base
from routers.crud import router as crud_router
from routers.users import router as users_router

app = FastAPI()
app.include_router(crud_router)
app.include_router(users_router)

app.mount("/static", StaticFiles(directory="static"), name="static")

# Veritabanı tablolarını oluştur
Base.metadata.create_all(bind=engine)


@app.get("/")
async def root(request: Request):
    """
    return RedirectResponse("static/index.html")
    """

    return RedirectResponse("docs")
