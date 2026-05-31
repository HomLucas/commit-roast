# FlightScanner

Privacy-focused flight deal scanner with points conversion tracking.

## Quick Start

### Backend

```powershell
cd backend
python -m venv venv

# PowerShell may block scripts — run this once per terminal:
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass

.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn src.main:app --reload
```

API at `http://localhost:8000` — Swagger docs at `/api/docs`.

### Frontend

```powershell
cd frontend
npm install
npm run dev
```

App at `http://localhost:3000`.

## Environment Setup

```powershell
Copy-Item .env.example .env
```

Then generate secret keys and fill in `.env`:

```powershell
# Generate JWT keys
openssl rand -hex 32
# Generate encryption key
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

No API keys required for development — app generates realistic mock flight data automatically when no real API is available.

For real data, add API keys (tried in order):
- **Skyscanner**: `SKYSCANNER_API_KEY` (primary)
- **Amadeus**: `AMADEUS_CLIENT_ID` + `AMADEUS_CLIENT_SECRET` (fallback)

For email alerts, set SMTP in `.env`:
```
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=your_app_password
```

## Local Dev Notes

- **SQLite** by default — no PostgreSQL needed.
- **Redis** not required — falls back to in-memory cache gracefully.
- **Rate limiting**: Login 5/min, Register 2/min, Refresh 3/min, Forgot/Reset 2/min.
- **Token blacklisting**: Logout revokes tokens. Works in-memory or via Redis.
- **Email**: Only sends if SMTP is configured in `.env`. Otherwise silently skips.
- **Celery worker**: For periodic alert checking, run `celery -A src.worker worker --beat` separately.

## Project Structure

```
backend/          FastAPI + SQLAlchemy async backend
frontend/         Next.js 14 frontend
scripts/          Deployment & security scripts
docker-compose.yml   Production deployment (PostgreSQL + Redis)
```
