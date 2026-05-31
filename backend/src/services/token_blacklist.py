from jose import jws, jwt
from src.services.redis_client import cache

BLACKLIST_PREFIX = "blklst:"


async def blacklist_token(token: str) -> None:
    payload = jwt.get_unverified_claims(token)
    exp = payload.get("exp", 0)
    jti = payload.get("jti") or _token_fingerprint(token)
    ttl = max(exp - __import__("time").time(), 0)
    if ttl > 0:
        c = await cache()
        await c.setex(f"{BLACKLIST_PREFIX}{jti}", int(ttl), "1")


async def is_blacklisted(token: str) -> bool:
    payload = jwt.get_unverified_claims(token)
    jti = payload.get("jti") or _token_fingerprint(token)
    c = await cache()
    return await c.exists(f"{BLACKLIST_PREFIX}{jti}")


def _token_fingerprint(token: str) -> str:
    import hashlib
    return hashlib.sha256(token.encode()).hexdigest()[:32]
