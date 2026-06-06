# app/core/dependencies.py
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from jose import JWTError
from app.bd.database import get_db
from app.core.security import decode_token
from app.models.models import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> User:
    try:
        payload = decode_token(token)
        user_id = int(payload.get("sub"))

        result = await db.execute(select(User).filter(User.id == user_id))
        user = result.scalars().first()

        if not user:
            raise HTTPException(status_code=401, detail="Utilisateur introuvable")
        return user

    except JWTError:
        raise HTTPException(status_code=401, detail="Token invalide")