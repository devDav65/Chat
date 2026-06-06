from app.memory.conversation import get_conversation, add_message
from google import genai
from google.genai import types
from app.core.config import settings
from sqlalchemy.ext.asyncio import AsyncSession
import asyncio

client = genai.Client(api_key=settings.GEMINI_API_KEY)


async def generate_response(db: AsyncSession, user_id: int, session_id: int, user_message: str) -> str:
    try:
        await add_message(db, user_id, session_id, "user", user_message)

        conversation = await get_conversation(db, session_id)

        # Construire l'historique (sans le dernier message)
        history = []
        for msg in conversation[:-1]:
            role = "user" if msg.role == "user" else "model"
            history.append(
                types.Content(
                    role=role,
                    parts=[types.Part(text=msg.content)]
                )
            )

        chat = client.chats.create(
            model=settings.GEMINI_MODEL,
            history=history
        )

        # Retry automatique en cas de 503
        for attempt in range(3):
            try:
                response = chat.send_message(
                    user_message,
                    config=types.GenerateContentConfig(
                        max_output_tokens=1000,
                        temperature=0.7,
                        top_p=0.9,
                    )
                )
                break
            except Exception as e:
                if "503" in str(e) and attempt < 2:
                    print(f"Gemini surchargé, tentative {attempt + 1}/3...")
                    await asyncio.sleep(2 ** attempt)
                else:
                    raise

        response_text = response.text.strip()
        await add_message(db, user_id, session_id, "assistant", response_text)
        return response_text

    except Exception as e:
        print(f"Erreur Gemini API: {e}")
        raise