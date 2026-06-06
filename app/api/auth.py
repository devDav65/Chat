from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from pydantic import BaseModel
from app.bd.database import get_db
from app.schemas.chat import UserCreate, UserLogin, UserResponse, Token, TokenWithUser
from app.services.auth_service import register_user, login_user
from app.models.models import User
from app.core.security import create_access_token
import httpx

router = APIRouter(prefix="/api/auth")


# ── Auth classique ─────────────────────────────────────────

@router.post("/register", response_model=UserResponse)
async def register(user: UserCreate, db: AsyncSession = Depends(get_db)):
    return await register_user(
        db, user.username, user.nom, user.prenom, user.email, user.password
    )


@router.post("/login", response_model=Token)
async def login(user: UserLogin, db: AsyncSession = Depends(get_db)):
    return await login_user(db, user.username, user.password)


# ── OAuth Google ───────────────────────────────────────────

class GoogleTokenRequest(BaseModel):
    token: str


@router.post("/google", response_model=TokenWithUser)
async def google_auth(body: GoogleTokenRequest, db: AsyncSession = Depends(get_db)):
    # 1. Vérifier le token auprès de Google
    async with httpx.AsyncClient() as client:
        res = await client.get(
            "https://www.googleapis.com/oauth2/v3/userinfo",
            headers={"Authorization": f"Bearer {body.token}"},
            timeout=10,
        )

    if res.status_code != 200:
        raise HTTPException(status_code=401, detail="Token Google invalide")

    info        = res.json()
    email       = info.get("email")
    given_name  = info.get("given_name", "")
    family_name = info.get("family_name", "")

    if not email:
        raise HTTPException(status_code=400, detail="Email non fourni par Google")

    # 2. Chercher l'user par email
    result = await db.execute(select(User).filter(User.email == email))
    user   = result.scalars().first()

    # 3. Créer l'user s'il n'existe pas
    if not user:
        base_username = email.split("@")[0]
        username      = base_username
        i = 1
        while True:
            r = await db.execute(select(User).filter(User.username == username))
            if not r.scalars().first():
                break
            username = f"{base_username}{i}"
            i += 1

        user = User(
            username=username,
            nom=family_name or base_username,
            prenom=given_name or base_username,
            email=email,
            password="",
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)

    # 4. JWT + username dans la réponse
    token = create_access_token({"sub": str(user.id)})
    return {
        "access_token": token,
        "token_type":   "bearer",
        "username":     user.username,
    }