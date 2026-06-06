from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import delete
from app.models.models import Conversation, Session


# ── Sessions ──────────────────────────────────────────────

async def create_session(db: AsyncSession, user_id: int, titre: str = "Nouvelle conversation") -> Session:
    session = Session(user_id=user_id, titre=titre)
    db.add(session)
    await db.commit()
    await db.refresh(session)
    return session


async def get_sessions(db: AsyncSession, user_id: int) -> list[Session]:
    result = await db.execute(
        select(Session)
        .filter(Session.user_id == user_id)
        .order_by(Session.updated_at.desc())
    )
    return result.scalars().all()


async def get_session(db: AsyncSession, session_id: int, user_id: int) -> Session | None:
    result = await db.execute(
        select(Session).filter(Session.id == session_id, Session.user_id == user_id)
    )
    return result.scalars().first()


async def update_session_titre(db: AsyncSession, session_id: int, user_id: int, titre: str) -> Session | None:
    session = await get_session(db, session_id, user_id)
    if not session:
        return None
    session.titre = titre
    await db.commit()
    await db.refresh(session)
    return session


async def delete_session(db: AsyncSession, session_id: int, user_id: int) -> bool:
    session = await get_session(db, session_id, user_id)
    if not session:
        return False
    await db.delete(session)
    await db.commit()
    return True


# ── Messages ──────────────────────────────────────────────

async def add_message(db: AsyncSession, user_id: int, session_id: int, role: str, content: str) -> Conversation:
    message = Conversation(
        user_id=user_id,
        session_id=session_id,
        role=role,
        content=content
    )
    db.add(message)
    await db.commit()
    await db.refresh(message)
    return message


async def get_conversation(db: AsyncSession, session_id: int, limit: int = 20) -> list[Conversation]:
    result = await db.execute(
        select(Conversation)
        .filter(Conversation.session_id == session_id)
        .order_by(Conversation.id.desc())
        .limit(limit)
    )
    messages = result.scalars().all()
    return list(reversed(messages))


async def clear_conversation(db: AsyncSession, session_id: int, user_id: int):
    await db.execute(
        delete(Conversation).where(
            Conversation.session_id == session_id,
            Conversation.user_id == user_id
        )
    )
    await db.commit()