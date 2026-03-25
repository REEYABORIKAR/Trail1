from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.models.database import get_db
from app.models.schemas import UserRegister, Token, UserOut
from app.models.user import User
from app.services.auth_service import register_user, authenticate_user, create_token_for_user
from app.core.security import get_current_user

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
def register(data: UserRegister, db: Session = Depends(get_db)):
    """Register a new user account."""
    user = register_user(db, data)
    token = create_token_for_user(user)
    return Token(access_token=token, user=UserOut.model_validate(user))


@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """Login with email and password (OAuth2 form)."""
    user = authenticate_user(db, form_data.username, form_data.password)
    token = create_token_for_user(user)
    return Token(access_token=token, user=UserOut.model_validate(user))


@router.post("/login/json", response_model=Token)
def login_json(data: "LoginBody", db: Session = Depends(get_db)):
    """Login with JSON body (used by the React frontend)."""
    user = authenticate_user(db, data.email, data.password)
    token = create_token_for_user(user)
    return Token(access_token=token, user=UserOut.model_validate(user))


@router.get("/me", response_model=UserOut)
def get_me(current_user: User = Depends(get_current_user)):
    """Get the current authenticated user's profile."""
    return current_user


# Inline schema for JSON login
from pydantic import BaseModel, EmailStr

class LoginBody(BaseModel):
    email: EmailStr
    password: str