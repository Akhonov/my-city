from pydantic import BaseModel, Field


class AuthRequest(BaseModel):
    username: str = Field(min_length=3, max_length=120)
    password: str = Field(min_length=4, max_length=120)


class AuthResponse(BaseModel):
    username: str
    message: str
