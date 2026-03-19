import hashlib

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User
from app.schemas.auth import AuthRequest, AuthResponse

router = APIRouter(tags=["auth"])


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


@router.post("/register", response_model=AuthResponse, summary="Register user")
def register(payload: AuthRequest, db: Session = Depends(get_db)) -> AuthResponse:
    username = payload.username.strip()
    if not username:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username is required")

    existing = db.query(User).filter(User.username == username).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User already exists")

    user = User(username=username, password_hash=hash_password(payload.password))
    db.add(user)
    db.commit()

    return AuthResponse(username=username, message="Registration successful")


@router.post("/login", response_model=AuthResponse, summary="Login user")
def login(payload: AuthRequest, db: Session = Depends(get_db)) -> AuthResponse:
    username = payload.username.strip()
    password_hash = hash_password(payload.password)

    user = db.query(User).filter(User.username == username).first()
    if not user or user.password_hash != password_hash:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username or password")

    return AuthResponse(username=user.username, message="Login successful")
