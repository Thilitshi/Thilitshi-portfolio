import os
from pathlib import Path

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


KNOWLEDGE_FILE = Path(__file__).parent / "portfolio_knowledge.txt"

try:
    portfolio_knowledge = KNOWLEDGE_FILE.read_text(encoding="utf-8")
    print("Portfolio knowledge loaded successfully.")
except Exception as e:
    portfolio_knowledge = ""
    print("KNOWLEDGE FILE ERROR:", repr(e))


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
        "http://localhost:5501",
        "https://thilitshi-portfolio.vercel.app"
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
        "gemini_configured": client is not None,
        "knowledge_loaded": bool(portfolio_knowledge)
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

Your job is to help visitors learn about Thilitshi and his portfolio.

IMPORTANT RULES:

1. Use the portfolio information provided below as your main source of truth.

2. Do not invent qualifications, work experience, projects, skills,
   certifications, education or other personal information.

3. If the visitor asks something about Thilitshi that is not included
   in the portfolio information, clearly say that the information is
   not currently available.

4. Be friendly, professional and concise.

5. Give direct answers. Do not make responses unnecessarily long.

6. If the visitor asks about Thilitshi's career plans, mention that
   he is open to graduate opportunities, internships and junior roles
   when relevant.

7. If the visitor asks about his skills, projects, education,
   certifications or interests, use the information provided below.

8. Do not claim that Thilitshi has professional experience unless
   it is specifically stated in the portfolio information.

9. If the visitor asks who you are, explain that you are the AI
   assistant for Thilitshi Mudzungwane's portfolio website.

10. If the visitor asks a general question unrelated to Thilitshi,
    you may answer it normally, but do not create personal information
    about Thilitshi.

PORTFOLIO INFORMATION:
----------------------

{portfolio_knowledge}

----------------------

VISITOR MESSAGE:
{user_message}

Answer the visitor now.
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