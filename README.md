# FlightScanner

Privacy-focused flight deal scanner with points conversion tracking.

## Quick Start

### Backend

```powershell
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn src.main:app --reload
```

API available at `http://localhost:8000` — Swagger docs at `/api/docs`.

### Frontend

```powershell
cd frontend
npm install
npm run dev
```

App available at `http://localhost:3000`.

## Environment Setup

Copy `.env.example` to `.env` and fill in your API keys:

```powershell
cp .env.example .env
```

Required API keys for flight search:
- **Amadeus**: `AMADEUS_CLIENT_ID` + `AMADEUS_CLIENT_SECRET` (free tier at [Amadeus Dev Portal](https://developers.amadeus.com))
- **Skyscanner**: `SKYSCANNER_API_KEY` (optional fallback)

The app runs with SQLite by default — no PostgreSQL needed for local development.

## Project Structure

```
backend/          FastAPI + SQLAlchemy async backend
frontend/         Next.js 14 frontend
scripts/          Deployment & security scripts
docker-compose.yml   Production deployment
```
