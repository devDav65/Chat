import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import chat, auth

app = FastAPI(title="Chatbot API", version="1.0.0")

# CORS dynamique : "*" en local, URL Vercel en prod
_raw = os.getenv("ALLOWED_ORIGINS", "*")
origins = [o.strip() for o in _raw.split(",")] if _raw != "*" else ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(chat.router)

@app.get("/")
async def root():
    return {"message": "Welcome to the Chatbot API"}