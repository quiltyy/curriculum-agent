from pydantic import BaseModel, EmailStr, Field
from enum import Enum

class UserRole(str, Enum):
    student = "student"
    advisor = "advisor"
    admin = "admin"

class RegisterIn(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    role: UserRole = UserRole.student   # default is student

class LoginIn(BaseModel):
    email: EmailStr
    password: str

class TokenOut(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class AccessTokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"

class MeOut(BaseModel):
    id: int
    email: EmailStr
    role: UserRole   # now includes role

class RefreshIn(BaseModel):
    refresh_token: str
