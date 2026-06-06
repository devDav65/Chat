from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.chat import ChatRequest, ChatResponse, SessionCreate, SessionUpdate, SessionResponse
from app.services.llm_services import generate_response
from app.core.dependencies import get_current_user
from app.memory.conversation import (
    create_session, get_sessions, get_session,
    update_session_titre, delete_session, get_conversation
)
from app.models.models import User
from app.bd.database import get_db

router = APIRouter(prefix="/api")


# ── Sessions ──────────────────────────────────────────────

@router.post("/sessions", response_model=SessionResponse)
async def nouvelle_session(
    body: SessionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await create_session(db, current_user.id, body.titre)


@router.get("/sessions", response_model=list[SessionResponse])
async def liste_sessions(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await get_sessions(db, current_user.id)


@router.patch("/sessions/{session_id}", response_model=SessionResponse)
async def renommer_session(
    session_id: int,
    body: SessionUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    session = await update_session_titre(db, session_id, current_user.id, body.titre)
    if not session:
        raise HTTPException(status_code=404, detail="Session introuvable")
    return session


@router.delete("/sessions/{session_id}")
async def supprimer_session(
    session_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    ok = await delete_session(db, session_id, current_user.id)
    if not ok:
        raise HTTPException(status_code=404, detail="Session introuvable")
    return {"detail": "Session supprimée"}


@router.get("/sessions/{session_id}/messages")
async def historique_session(
    session_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    session = await get_session(db, session_id, current_user.id)
    if not session:
        raise HTTPException(status_code=404, detail="Session introuvable")
    messages = await get_conversation(db, session_id)
    return [{"role": m.role, "content": m.content, "created_at": m.created_at} for m in messages]


# ── Chat ──────────────────────────────────────────────────

@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(
    request: ChatRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Vérifier que la session appartient à l'utilisateur
    session = await get_session(db, request.session_id, current_user.id)
    if not session:
        raise HTTPException(status_code=404, detail="Session introuvable")

    try:
        response_text = await generate_response(
            db,
            current_user.id,
            request.session_id,
            request.message
        )
        return ChatResponse(response=response_text)
    except Exception as e:
        print(f"ERREUR DETECTEE : {e}")
        raise HTTPException(status_code=500, detail=str(e))