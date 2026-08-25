# Personal Website + AI Chatbot

Stack: HTML/CSS/JavaScript + Python/FastAPI + MySQL + OpenAI.

1. Run `database/schema.sql` in MySQL.
2. Copy `backend/.env.example` to `backend/.env`.
3. Add your MySQL password and OpenAI API key.
4. In `backend`, run:
   `python -m pip install -r requirements.txt`
5. Start the backend:
   `uvicorn main:app --reload`
6. Open `frontend/index.html`.
