import httpx
from fastapi import HTTPException

async def get_github_user(username: str):
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"https://api.github.com/users/{username}")
            if response.status_code == 404:
                raise HTTPException(
                    status_code=404,
                    detail=f"Github user {username} not found!"
                )
            data = response.json()
            return {
                "username": data["login"],
                "name": data["name"],
                "public_repositories": data["public_repos"],
                "followers": data["followers"]
            }
    except httpx.HTTPError as error:
        raise HTTPException(status_code=503, detail=str(error))

