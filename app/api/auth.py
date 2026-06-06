from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.bd.database import get_db
from app.schemas.chat import UserCreate, UserLogin, UserResponse, Token
from app.services.auth_service import register_user, login_user

router = APIRouter(prefix="/api/auth")


@router.post("/register", response_model=UserResponse)
async def register(user: UserCreate, db: AsyncSession = Depends(get_db)):
    return await register_user(
        db,
        user.username,
        user.nom,
        user.prenom,
        user.email,
        user.password
    )


@router.post("/login", response_model=Token)
async def login(user: UserLogin, db: AsyncSession = Depends(get_db)):
    return await login_user(db, user.username, user.password)