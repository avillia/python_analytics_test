from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr

from src.api.security import requires_authorization
from src.core.handlers.auth import (
    assign_existing_role_with,
    create_new_user_with_following,
    obtain_jwt_token_for,
)

auth_router = APIRouter(
    prefix="/auth",
    tags=["service"],
)


class UserLoginRequest(BaseModel):
    login: str
    password: str


class UserSignUp(BaseModel):
    email: EmailStr
    name: str
    login: str
    password: str


class AssignRoleRequest(BaseModel):
    login: str
    role_name: str


@auth_router.post("/login")
async def login(credentials: UserLoginRequest) -> dict:
    try:
        return {
            "access_token": obtain_jwt_token_for(
                credentials.login,
                credentials.password,
            ),
            "token_type": "bearer",
        }
    except KeyError:
        raise HTTPException(
            status_code=401,
            detail=f"Invalid password for {credentials.login}!",
        )
    except LookupError:
        raise HTTPException(
            status_code=401,
            detail=f"Invalid username: no user with such login [{credentials.login}] exists!",
        )


@auth_router.post("/signup", status_code=201)
async def signup(credentials: UserSignUp) -> dict:
    try:
        create_new_user_with_following(
            credentials.login,
            credentials.email,
            credentials.name,
            credentials.password,
        )
        return {"status": "success", "login_url": auth_router.url_path_for("login")}
    except LookupError:
        raise HTTPException(
            status_code=401,
            detail="Looks like these credentials are already occupied! Try different one.",
        )


@auth_router.patch("/add_role")
async def assign_role(
    _: requires_authorization,
    new_role_request: AssignRoleRequest,
) -> dict:
    if assign_existing_role_with(new_role_request.role_name, to=new_role_request.login):
        return {
            "status": "success",
            "info": f"User '{new_role_request.login}' is now '{new_role_request.role_name}!",
        }
    return {
        "status": "OK",
        "info": f"No changes: User '{new_role_request.login}' is already '{new_role_request.role_name}",
    }
