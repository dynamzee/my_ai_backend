from fastapi import FastAPI, HTTPException, Security, Depends
from fastapi.requests import Request
from fastapi.responses import JSONResponse
from pydantic_settings import BaseSettings, SettingsConfigDict
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security.api_key import APIKeyHeader
from routers import notes, users, claude_one_off, claude_with_memory
from services.github import get_github_user
import time
from loguru import logger

class Settings(BaseSettings):
    app_name: str
    env: str
    debug: bool
    api_key: str
    anthropic_api_key: str

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )

app = FastAPI()
settings = Settings()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

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

API_KEY_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name= API_KEY_NAME)

async def verify_api_key(api_key: str = Security(api_key_header)):
    if api_key != settings.api_key:
        raise HTTPException(
            status_code=403,
            detail="Invalid/Missing api_key."
        )

app.include_router(notes.router, dependencies=[Depends(verify_api_key)])
app.include_router(users.router, dependencies=[Depends(verify_api_key)])
app.include_router(claude_one_off.router, dependencies=[Depends(verify_api_key)])
app.include_router(claude_with_memory.router, dependencies=[Depends(verify_api_key)])

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time
    logger.info(
        f"{request.method} {request.url.path}."
        f">> {response.status_code}."
        f">> ({duration:.3f})s."
    )
    return response

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


