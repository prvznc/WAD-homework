from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.auth.router import router as auth_router
from app.chats.router import router as chats_router
from app.core.config import settings

app = FastAPI(title=settings.app_name)

app.include_router(auth_router, prefix="/api")
app.include_router(chats_router, prefix="/api")

app.mount("/static", StaticFiles(directory="app/static"), name="static")


@app.get("/")
def index():
    return FileResponse("app/static/index.html")


@app.get("/health")
def health():
    return {"status": "ok"}
