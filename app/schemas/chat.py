from pydantic import BaseModel, Field, EmailStr
from datetime import datetime


# ── Chat ──────────────────────────────────────────────────

class ChatRequest(BaseModel):
    session_id: int
    message: str = Field(..., min_length=1, max_length=3000)


class ChatResponse(BaseModel):
    response: str


# ── Sessions ──────────────────────────────────────────────

class SessionCreate(BaseModel):
    titre: str = "Nouvelle conversation"


class SessionUpdate(BaseModel):
    titre: str


class SessionResponse(BaseModel):
    id: int
    titre: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ── Auth ──────────────────────────────────────────────────

class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    nom: str = Field(..., min_length=1, max_length=100)
    prenom: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=6)


class UserLogin(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6)


class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    nom: str
    prenom: str

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str