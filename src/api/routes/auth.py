from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr

from src.core.handlers.auth import obtain_jwt_token_for

auth_router = APIRouter(
    prefix="/auth",
    tags=["service"],
)


class UserLogin(BaseModel):
    login: str
    password: str


class UserSignUp(BaseModel):
    email: EmailStr
    login: str
    password: str


@auth_router.get("/")
async def login(credentials: UserLogin) -> dict:
    try:
        return {
            "access_token": obtain_jwt_token_for(
                credentials.login, credentials.password
            ),
            "token_type": "bearer",
        }
    except KeyError:
        raise HTTPException(status_code=401, detail=f"Invalid password for {login=}!")
    except LookupError:
        raise HTTPException(
            status_code=401,
            detail=f"Invalid username: no user with such {login=} exists!",
        )
