from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from auth.security import create_access_token, verify_password
from database.models import User
from database.session import get_db

router = APIRouter(prefix="/auth", tags=["auth"])


class LoginRequest(BaseModel):
    username: str
    password: str


@router.post("/token")
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> dict:
    if not payload.username or not payload.password:
        raise HTTPException(status_code=400, detail="Missing credentials")

    user = db.scalar(select(User).where(User.username == payload.username))
    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    token = create_access_token(payload.username)
    return {"access_token": token, "token_type": "bearer"}
