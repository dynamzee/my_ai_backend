from fastapi import FastAPI
from fastapi.requests import Request
from fastapi.responses import JSONResponse
from fastapi import HTTPException
from pydantic_settings import BaseSettings
from routers import notes, users
from services.github import get_github_user

class Settings(BaseSettings):
    app_name: str
    env: str
    debug: bool

    class Config:
        env_file = ".env"

app = FastAPI()
settings = Settings()

app.include_router(notes.router)
app.include_router(users.router)

@app.exception_handler(404)
async def error_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=404,
        content={
            "status": "error",
            "code": 404,
            "message": exc.detail
        }
    )

@app.get("/")
async def root():
    return {
        "status": "I'm alive!",
        "app_name": settings.app_name,
        "env": settings.env,
        "debug": settings.debug
    }

@app.get("/health")
async def health():
    return {"status": "Health is wealth. 🙂‍↔️"}

@app.get("/github/{username}")
async def fetch_github_user(username: str):
    return await get_github_user(username)







