import os
from dotenv import load_dotenv
from urllib.parse import urlparse, urlencode, urlunparse, parse_qs
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

# Parsing propre de l'URL pour retirer TOUS les paramètres query
parsed = urlparse(DATABASE_URL)
clean_url = urlunparse((
    "postgresql+asyncpg",   # scheme
    parsed.netloc,          # host:port
    parsed.path,            # /neondb
    "",                     # params
    "",                     # query  ← on vide tout
    "",                     # fragment
))

engine = create_async_engine(
    clean_url,
    echo=True,
    connect_args={"ssl": "require"},  # SSL géré ici pour asyncpg
)

AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

Base = declarative_base()


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session