from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.models import User
from app.core.security import hash_password, verify_password, create_access_token
from fastapi import HTTPException


async def register_user(db: AsyncSession, username: str, nom: str, prenom: str, email: str, password: str):
    # Vérifier si l'email existe déjà
    result = await db.execute(select(User).filter(User.email == email))
    existing = result.scalars().first()
    if existing:
        raise HTTPException(status_code=400, detail="Email déjà utilisé")

    # Vérifier si le username existe déjà
    result = await db.execute(select(User).filter(User.username == username))
    if result.scalars().first():
        raise HTTPException(status_code=400, detail="Nom d'utilisateur déjà utilisé")

    user = User(
        username=username,
        nom=nom,
        prenom=prenom,
        email=email,
        password=hash_password(password)  # garde le nom de champ de ton modèle
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def login_user(db: AsyncSession, username: str, password: str):
    result = await db.execute(select(User).filter(User.username == username))
    user = result.scalars().first()

    if not user or not verify_password(password, user.password):
        raise HTTPException(status_code=401, detail="Email ou mot de passe incorrect")

    token = create_access_token({"sub": str(user.id)})
    return {"access_token": token, "token_type": "bearer"}