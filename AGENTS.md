# FlightScanner — Known Issues & Development Notes

## Architecture Decisions

### SQLite for dev, PostgreSQL for production
- **Why**: No Docker/PostgreSQL dependency for local development.
- **Trade-off**: SQLite doesn't support concurrent writes well. Fine for single-dev.
- **File**: `backend/src/database.py` auto-detects SQLite vs PostgreSQL and adjusts pool settings.

### API keys: SecretStr vs plain strings
- Config started with `SecretStr` (Pydantic) for all keys, but this broke local dev.
- **Fix**: Made dev defaults plain strings with `_resolve_key()` helper that handles both.
- **Files**: `backend/src/config.py`, `backend/src/services/auth.py`, `backend/src/security.py`

---

## Issues Encountered

### 1. SlowAPI `@limiter.limit()` requires `request: Request` parameter
- **Problem**: The decorator inspects the function signature and crashes if there's no parameter named `request` or `websocket` of type `starlette.requests.Request`.
- **Impact**: Routes with Pydantic body also named `request` would fail.
- **Fix**: Renamed body params (e.g., `request` → `search_query`) and added `request: Request` as the first parameter.
- **Files**: `backend/src/api/flights.py`, `backend/src/api/auth.py`

### 2. Pydantic v2 `from_orm()` — datetime field type mismatch
- **Problem**: Schema fields typed as `Optional[str]` would fail validation when SQLAlchemy returned `datetime` objects via `from_orm()` / `model_validate()`.
- **Impact**: `POST /register` returned 500.
- **Fix**: Changed schema datetime fields from `Optional[str]` to `Optional[datetime]`. Pydantic serializes them to ISO strings automatically.
- **Files**: `backend/src/schemas/auth.py`, `backend/src/schemas/alerts.py`

### 3. JWT `sub` claim must be a string (RFC 7519)
- **Problem**: python-jose validates that `sub` is a string. We passed `user.id` (int), causing `JWTClaimsError`.
- **Impact**: `GET /api/auth/me` always returned 401 after login.
- **Fix**: Convert `user.id` to `str(user.id)` when building token payload. Convert back with `int(payload["sub"])` in `get_current_user`.
- **Files**: `backend/src/api/auth.py`, `backend/src/services/auth.py`

### 4. bcrypt 5.x broke passlib 1.7.4
- **Problem**: `pip install -r requirements.txt` installs bcrypt 5.x which removed `bcrypt.__about__`. passlib 1.7.4 crashes trying to read it.
- **Impact**: Every password hash/verify operation threw `ValueError`.
- **Fix**: Removed passlib dependency entirely. Using `bcrypt` directly (`hashpw` / `checkpw`).
- **Files**: `backend/requirements.txt`, `backend/src/services/auth.py`, `backend/src/security.py`

### 5. python-jose has no `jwt.get_unverified_claims()`
- **Problem**: Token blacklist used `jwt.get_unverified_claims(token)` which doesn't exist in python-jose.
- **Impact**: `is_blacklisted()` raised AttributeError on every request.
- **Fix**: Use `jwt.decode(token, "", options={"verify_signature": False})` instead.
- **Files**: `backend/src/services/token_blacklist.py`

### 6. `TrustedHostMiddleware` blocking localhost
- **Problem**: Middleware was configured with `settings.cors_origins` (URLs like `http://localhost:3000`), but it expects bare hostnames.
- **Impact**: All requests returned 400 "Invalid host header".
- **Fix**: Changed to `["*"]` in debug mode, or explicit hostnames in production.
- **Files**: `backend/src/main.py`

### 7. SQLite + SQLAlchemy async pool args
- **Problem**: SQLAlchemy's `create_async_engine` rejects `pool_size` / `max_overflow` when using `NullPool` with SQLite.
- **Impact**: Engine creation crashed on startup.
- **Fix**: Only pass pool kwargs when not using SQLite.
- **Files**: `backend/src/database.py`

### 8. `node_modules/` and `.next/` nearly committed
- **Problem**: `.gitignore` didn't have `node_modules/` or `.next/` patterns initially.
- **Impact**: `git add -A` staged ~8700 files after `npm install` and `npm run build`.
- **Fix**: Added patterns to `.gitignore`, then `git rm --cached` to untrack.

### 9. Fernet key validation
- **Problem**: `DataEncryption` expects a 44-byte base64 key. If the key from settings doesn't match, Fernet raises `ValueError`.
- **Fix**: Added fallback that hashes the key to produce a valid 32-byte key.
- **Files**: `backend/src/security.py`

---

## Pending Improvements

- **Redis for production**: Token blacklist and rate limiter currently use in-memory fallback when Redis is unavailable. Deploy with Redis for persistence.
- **Email alerts**: SMTP config is plumbed but no actual email provider set up yet. Need real SMTP credentials in `.env`.
- **API keys**: Flight search requires Amadeus API keys (`AMADEUS_CLIENT_ID` / `AMADEUS_CLIENT_SECRET`). Without them, the search endpoint returns 503.
- **Celery worker**: `src/worker.py` exists but needs a running Redis + Celery beat process for periodic alert checking.
- **Password reset frontend**: Backend endpoints exist (`/forgot-password`, `/reset-password`) but no frontend pages are built yet.
- **Logout on frontend**: The auth store supports logout, but the UI doesn't have a logout button yet.
