from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from auth.security import create_access_token

router = APIRouter(prefix="/auth", tags=["auth"])


class LoginRequest(BaseModel):
    username: str
    password: str


@router.post("/token")
def login(payload: LoginRequest) -> dict:
    if not payload.username or not payload.password:
        raise HTTPException(status_code=400, detail="Missing credentials")
    token = create_access_token(payload.username)
    return {"access_token": token, "token_type": "bearer"}
