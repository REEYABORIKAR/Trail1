from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional, List
from datetime import datetime
from app.models.user import UserRole


# ─── Auth Schemas ────────────────────────────────────────────────────────────

class UserRegister(BaseModel):
    full_name: str
    email: EmailStr
    password: str
    department: Optional[str] = None

    @field_validator("password")
    @classmethod
    def password_strength(cls, v):
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        return v

    @field_validator("full_name")
    @classmethod
    def name_not_empty(cls, v):
        if not v.strip():
            raise ValueError("Full name cannot be empty")
        return v.strip()


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: "UserOut"


class UserOut(BaseModel):
    id: int
    full_name: str
    email: str
    role: UserRole
    department: Optional[str]
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


# ─── RAG Schemas ─────────────────────────────────────────────────────────────

class QueryRequest(BaseModel):
    question: str
    top_k: int = 4

    @field_validator("question")
    @classmethod
    def question_not_empty(cls, v):
        if not v.strip():
            raise ValueError("Question cannot be empty")
        return v.strip()


class SourceDoc(BaseModel):
    filename: str
    page: Optional[int] = None
    chunk_index: Optional[int] = None
    excerpt: Optional[str] = None


class QueryResponse(BaseModel):
    answer: str
    sources: List[SourceDoc]
    is_fallback: bool
    contact_email: str
    question: str


class IngestResponse(BaseModel):
    message: str
    filename: str
    chunks_created: int