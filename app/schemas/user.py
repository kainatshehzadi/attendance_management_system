from pydantic import BaseModel, EmailStr, constr, model_validator
from typing import Literal, Optional
from app.enum import RoleEnum

# Base schema shared across other user schemas
class UserBase(BaseModel):
    username: str
    email: EmailStr
    role: RoleEnum

    class Config:
        from_attributes = True

# Schema used for creating a user
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: constr(min_length=8)  # type: ignore # Plain password input
    confirm_password: str
    role: Literal['admin', 'employee']  # Default role is 'employee'
@model_validator(mode="after")
def check_passwords_match(self) -> 'UserCreate':
        if self.password != self.confirm_password:
            raise ValueError("Passwords do not match")
        return self
# Schema used for sending user data as a response
class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    role: RoleEnum

    class Config:
        from_attributes = True

# Schema used for login
class Login(BaseModel):
    email: EmailStr
    password: str

    class config:
        from_attributes = True
