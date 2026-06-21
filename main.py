from fastapi import FastAPI, HTTPException
from fastapi.requests import Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from pydantic_settings import BaseSettings
from pydantic import EmailStr
import httpx
from typing import Optional

class Settings(BaseSettings):
    app_name: str
    env: str
    debug: bool

    class Config:
        env_file = ".env"

app = FastAPI()

settings = Settings()

@app.exception_handler(404)
async def handle_not_found(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=404,
        content = {
            "status": "error!",
            "code": 404,
            "message": exc.detail
        }
    )

class User(BaseModel):
    name: str
    age: int
    email: str

class Note(BaseModel):
    title: str
    content: str

class NoteResponse(BaseModel):
    id: int
    title: str
    content: str

notes_counter: int = 0
notes_database: dict = {}

@app.post("/notes", response_model=NoteResponse)
async def create_new_note(note: Note):
    global notes_counter
    notes_counter += 1
    new_note = ({
        "id": notes_counter,
        "title": note.title,
        "content": note.content
    })
    notes_database[notes_counter] = new_note
    return new_note

@app.get("/notes", response_model=list[NoteResponse])
async def list_all_notes():
    return list(notes_database.values())

@app.get("/notes/{note_id}")
async def get_specific_note(note_id: int):
    if note_id not in notes_database:
        raise HTTPException(status_code=404, detail=f"ERROR! Note {note_id} not found.")
    return notes_database[note_id]

@app.put("/notes/{note_id}", response_model=NoteResponse)
async def update_note(note_id: int, note: Note):
    if note_id not in notes_database:
        raise HTTPException(status_code=404, detail=f"ERROR! Note {note_id} not found.")
    notes_database[note_id].update({
        "title": note.title,
        "content": note.content
    })
    return notes_database[note_id]

@app.delete("/notes/{note_id}", response_model=NoteResponse)
async def delete_note(note_id: int):
    if note_id not in notes_database:
        raise HTTPException(status_code=404, detail=f"ERROR! Note {note_id} not found.")
    del notes_database[note_id]
    return f"Note {note_id} has been deleted successfully."

@app.get("/")
async def root():
    return {
        "status": "I'm good to go.",
        "app_name": settings.app_name,
        "env": settings.env,
        "debug": settings.debug
    }

@app.get("/health")
async def health():
    return {"status": "app is doing it's thing."}

@app.post("/users")
async def create_user_account(user: User):
    return {
        "name": user.name,
        "age": user.age,
        "email": user.email
    }

@app.get("/users/{user_id}")
async def get_specific_user(user_id: int):
    users = {
        1: {"name": "Flo", "age": 22, "email": "flo@gmail.com"},
        2: {"name": "Rio", "age": 18, "email": "rio@gmail.com"}
    }
    if user_id not in users:
        raise HTTPException(status_code=404, detail=f"ERROR! User {user_id} does not exist!")
    return users[user_id]

@app.get("/users")
async def list_all_users(limit: int = 10):
    return {"limit": limit, "message": f"Returning {limit} users."}

@app.get("/github/{username}")
async def get_github_user(username: str):
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"https://api.github.com/users/{username}")
            data = response.json()
            if response.status_code == 404:
                raise HTTPException(status_code=404, detail=f"Github account {username} does not exist.")
            return {
                "username": data["login"],
                "name": data["name"],
                "public_repositories": data["public_repos"],
                "followers": data["followers"]
            }
    except httpx.HTTPError as error:
        return {"error": str(error)}




