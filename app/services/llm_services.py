from app.memory.conversation import get_conversation, add_message
from google import genai
from google.genai import types
from app.core.config import settings
from sqlalchemy.ext.asyncio import AsyncSession
import asyncio

client = genai.Client(api_key=settings.GEMINI_API_KEY)

# Modèle avec quota généreux : 1500 req/jour sur free tier
GEMINI_MODEL = "gemini-1.5-flash"


async def generate_response(db: AsyncSession, user_id: int, session_id: int, user_message: str) -> str:
    try:
        await add_message(db, user_id, session_id, "user", user_message)

        conversation = await get_conversation(db, session_id)

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
            model=GEMINI_MODEL,
            history=history
        )

        # Retry sur 503 (surcharge) ET 429 (quota dépassé)
        last_error = None
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
                last_error = None
                break
            except Exception as e:
                last_error = e
                err_str = str(e)

                if "503" in err_str and attempt < 2:
                    print(f"Gemini surchargé, tentative {attempt + 1}/3...")
                    await asyncio.sleep(2 ** attempt)

                elif "429" in err_str or "RESOURCE_EXHAUSTED" in err_str:
                    # Extraire le délai suggéré par l'API si présent
                    wait = 45
                    try:
                        import re
                        match = re.search(r'retry.*?(\d+)s', err_str, re.IGNORECASE)
                        if match:
                            wait = int(match.group(1)) + 2
                    except Exception:
                        pass

                    if attempt < 2:
                        print(f"Quota Gemini dépassé, attente {wait}s (tentative {attempt + 1}/3)...")
                        await asyncio.sleep(wait)
                    else:
                        raise RuntimeError(
                            "Le service IA est temporairement indisponible (quota dépassé). "
                            "Veuillez réessayer dans quelques instants."
                        )
                else:
                    raise

        if last_error:
            raise last_error

        response_text = response.text.strip()
        await add_message(db, user_id, session_id, "assistant", response_text)
        return response_text

    except RuntimeError:
        raise
    except Exception as e:
        print(f"Erreur Gemini API: {e}")
        raise