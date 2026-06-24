from fastapi import APIRouter, HTTPException
from schemas.users import User

router = APIRouter()

@router.post("/users")
async def create_new_user(user: User):
    new_user = {
        "name": user.name,
        "age": user.age,
        "email": user.email
    }
    return new_user

@router.get("/users/{user_id}")
async def get_specific_user(user_id: int):
    users = {
        1: {"name": "Rio", "age": 23, "email": "rio17@gmail.com"},
        2: {"name": "Flo", "age": 21, "email": "flo7@gmail.com"}
    }
    if user_id not in users:
        raise HTTPException(status_code=404, detail=f"User {user_id} not found!")
    return users[user_id]

@router.get("/users")
async def list_all_users(limit: int = 10):
    return {"limit": limit, "message": f"Returning {limit} users."}



