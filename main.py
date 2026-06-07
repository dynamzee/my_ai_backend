from fastapi import FastAPI
from pydantic import BaseModel
from pydantic_settings import BaseSettings
import httpx
from pydantic import EmailStr

class Settings(BaseSettings):
    app_name: str
    env: str
    debug: bool

    class Config:
        env_file = ".env"

settings = Settings()

app = FastAPI()

class User(BaseModel):
    name: str
    age: int
    email: str

@app.get("/")
async def root():
    return {
        "status": "I'm alive",
        "app": settings.app_name,
        "environment": settings.env,
        "debug": settings.debug
    }

@app.get("/health")
async def health():
    return {"working?": "oh yeah, I'm working."}

@app.post("/users")
async def create_user_account(user: User):
    return {"message": f"welcome, {user.name}!", "user": user}

@app.get("/users/{user_id}")
async def get_users(user_id: int):
    return {"user_id": user_id, "message": f"fetching number of users: {user_id}"}

@app.get("/users")
async def list_users(limit: int= 10):
    return {"limit": limit, "message": f"returning {limit} users."}

@app.get("/github/{username}")
async def get_github_user(username: str):
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"https://api.github.com/users/{username}")
            data = response.json()
            if response.status_code == 404:
                return {"error": f"github account '{username}' does not exist."}
            return {
                "username": data["login"],
                "name": data["name"],
                "public_repositories": data["public_repos"],
                "followers": data["followers"]
            }
    except httpx.HTTPError as error:
        return {"error": str(error)}










