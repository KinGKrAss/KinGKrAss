from pydantic import BaseModel, ConfigDict, Field


class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=64)
    password: str = Field(..., min_length=8)
    role: str = Field("viewer", pattern="^(admin|editor|viewer)$")
    email: str | None = Field(None, max_length=128)


class UserUpdate(BaseModel):
    role: str | None = Field(None, pattern="^(admin|editor|viewer)$")
    email: str | None = Field(None, max_length=128)
    is_active: bool | None = None


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    role: str
    email: str | None
    is_active: bool
