import hashlib
from time import time
from jose import jwt
from src.services.redis_client import cache

BLACKLIST_PREFIX = "blklst:"


def _unverified_claims(token: str) -> dict:
    return jwt.decode(token, "", options={"verify_signature": False})


async def blacklist_token(token: str) -> None:
    payload = _unverified_claims(token)
    exp = payload.get("exp", 0)
    jti = payload.get("jti") or _token_fingerprint(token)
    ttl = max(exp - time(), 0)
    if ttl > 0:
        c = await cache()
        await c.setex(f"{BLACKLIST_PREFIX}{jti}", int(ttl), "1")


async def is_blacklisted(token: str) -> bool:
    payload = _unverified_claims(token)
    jti = payload.get("jti") or _token_fingerprint(token)
    c = await cache()
    return await c.exists(f"{BLACKLIST_PREFIX}{jti}")


def _token_fingerprint(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()[:32]
