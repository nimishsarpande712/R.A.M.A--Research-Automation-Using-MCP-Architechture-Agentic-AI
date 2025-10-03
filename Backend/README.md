# R.A.M.A Backend (FastAPI)

Minimal FastAPI app with environment loading, SQLAlchemy session, Pydantic schemas, and CORS for the React frontend.

## Quick start

1. Optional: create `.env` in `Backend/` to override settings. By default a local `sqlite` DB (file `app.db`) is used.
2. Create/activate a virtualenv (optional if you already have `Backend/venv`):
   - Windows PowerShell
     - `python -m venv venv`
     - `./venv/Scripts/Activate.ps1`
3. Install dependencies:
   - `pip install -r requirements.txt`
4. Run the server:
   - `uvicorn app.main:app --reload --host 0.0.0.0 --port 8000`

Then open http://localhost:8000/ and http://localhost:8000/docs.

CORS is configured to allow the React dev server at `http://localhost:3000` by default. Override with `FRONTEND_ORIGIN` in `.env` if needed.

Auth endpoints:
- POST `/api/auth/register` { email, password }
- POST `/api/auth/login` { email, password } -> { access_token, token_type }
