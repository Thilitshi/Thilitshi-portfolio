import os

from dotenv import load_dotenv
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session
from google import genai

from database import Base, engine, get_db
from models import ChatMessage

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    print("WARNING: GEMINI_API_KEY is missing.")

try:
    Base.metadata.create_all(bind=engine)
    print("Database connection successful.")
except Exception as e:
    print("DATABASE ERROR:", repr(e))

app = FastAPI(title="Personal Website API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5500",
        "http://localhost:5500",
        "http://127.0.0.1:5501",
        "http://localhost:5501"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

client = None

if GEMINI_API_KEY:
    client = genai.Client(api_key=GEMINI_API_KEY)


class ChatRequest(BaseModel):
    message: str


@app.get("/")
def home():
    return {
        "message": "Personal Website API is running",
        "status": "OK"
    }


@app.get("/api/health")
def health():
    return {
        "status": "OK",
        "gemini_configured": client is not None
    }


@app.post("/api/chat")
def chat(
    request: ChatRequest,
    db: Session = Depends(get_db)
):
    user_message = request.message.strip()

    if not user_message:
        return {
            "response": "Please enter a message."
        }

    if client is None:
        raise HTTPException(
            status_code=500,
            detail="Gemini API key is not configured."
        )

    try:
        prompt = f"""
You are the AI assistant on Thilitshi Mudzungwane's personal portfolio website.

Be friendly, professional and concise.

Help visitors learn about:
- Education
- Computer Science
- Programming skills
- Projects
- Certifications
- Experience
- Career interests
- Personal website

If the visitor asks about Thilitshi, answer helpfully.
Do not invent qualifications or experience that you do not know.

Visitor message:
{user_message}
"""

        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=prompt
        )

        ai_response = response.text.strip()

        if not ai_response:
            ai_response = "Sorry, I couldn't generate a response."

        try:
            chat_record = ChatMessage(
                user_message=user_message,
                ai_response=ai_response
            )

            db.add(chat_record)
            db.commit()

        except Exception as db_error:
            db.rollback()
            print("DATABASE SAVE ERROR:", repr(db_error))

        return {
            "response": ai_response
        }

    except Exception as e:
        print("GEMINI ERROR:", repr(e))

        raise HTTPException(
            status_code=500,
            detail=f"Gemini request failed: {str(e)}"
        )