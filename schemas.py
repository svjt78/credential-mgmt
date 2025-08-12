from typing import Optional, Literal
from pydantic import BaseModel, EmailStr

# ---------- Users ----------

class UserBase(BaseModel):
    email: EmailStr
    username: str

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int
    is_active: bool
    is_verified: bool

    class Config:
        orm_mode = True

# ---------- Auth / Tokens ----------

class Token(BaseModel):
    access_token: str
    token_type: Literal["bearer"]

class LoginResponse(BaseModel):
    access_token: str
    token_type: Literal["bearer"]
    user_id: str            # credential UUID
    email: EmailStr
    username: str
    is_active: bool
    is_verified: bool

    class Config:
        orm_mode = True

class SignupResponse(BaseModel):
    id: int
    user_id: str            # credential UUID
    email: EmailStr
    username: str
    is_active: bool
    is_verified: bool
    verificationToken: str  # <-- added

    class Config:
        orm_mode = True

class TokenData(BaseModel):
    user_id: Optional[str] = None

# ---------- Requests ----------

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str

class ResetPasswordRequest(BaseModel):
    email: EmailStr

class ResetPasswordConfirm(BaseModel):
    token: str
    new_password: str

class VerifyEmailRequest(BaseModel):
    token: str
