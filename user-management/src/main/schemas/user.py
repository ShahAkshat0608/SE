from pydantic import BaseModel, EmailStr, validator, Field
from typing import Optional

class UserBase(BaseModel):
    email: EmailStr
    name: str
    contact: Optional[str] = None
    
    @validator('email')
    def email_must_be_gmail(cls, v):
        if not v.endswith('@gmail.com'):
            raise ValueError('Email must be a Gmail address (ending with @gmail.com)')
        return v

class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(UserBase):
    id: int

    class Config:
        # orm_mode = True # Compatibility with ORM models (like our Row objects)
        # Updated to use model_config in Pydantic v2
        from_attributes = True 
        # model_config = {"from_attributes": True} 