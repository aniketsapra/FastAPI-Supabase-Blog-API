import os
import requests
from jose import jwt, JWTError
from fastapi import HTTPException
from dotenv import load_dotenv
from time import time
from functools import lru_cache

load_dotenv()

SUPABASE_JWKS_URL = os.getenv("SUPABASE_JWKS_URL")
ALGORITHM = os.getenv("SUPABASE_ALGORITHM", "ES256")
AUDIENCE = os.getenv("SUPABASE_AUDIENCE")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Cache with a Time-To-Live (TTL) of 1 hour (3600 seconds)
@lru_cache(maxsize=1)
def get_jwks(ttl_hash=None):
    """
    Fetches and caches the JWKS from Supabase.
    The ttl_hash is used to invalidate the cache based on time.
    """
    del ttl_hash  # Unused, but important for cache invalidation
    try:
        headers = {"apikey": SUPABASE_KEY}
        response = requests.get(SUPABASE_JWKS_URL, headers=headers)
        response.raise_for_status()  # Raise an exception for bad status codes
        return response.json()
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch JWKS: {e}")

def get_ttl_hash(seconds=3600):
    """Return the same value within `seconds` time."""
    return round(time() / seconds)

def verify_supabase_token(token: str):
    """
    Verifies a Supabase JWT.

    Args:
        token: The JWT to verify.

    Returns:
        The decoded payload of the token.

    Raises:
        HTTPException: If the token is invalid or verification fails.
    """
    try:
        unverified_header = jwt.get_unverified_header(token)
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token header")

    kid = unverified_header.get("kid")
    if not kid:
        raise HTTPException(status_code=401, detail="Token is missing 'kid' in the header")

    jwks = get_jwks(ttl_hash=get_ttl_hash())
    
    key = next((k for k in jwks.get("keys", []) if k.get("kid") == kid), None)
    
    if not key:
        # If the key is not found, it might be because the keys have been rotated.
        # We can try to refresh the cache once.
        jwks = get_jwks.cache_clear()
        jwks = get_jwks(ttl_hash=get_ttl_hash())
        key = next((k for k in jwks.get("keys", []) if k.get("kid") == kid), None)
        if not key:
            raise HTTPException(status_code=401, detail="Signing key not found in JWKS")

    try:
        payload = jwt.decode(
            token,
            key,
            algorithms=[ALGORITHM],
            options={"verify_exp": True,"verify_aud": False},
        )
        return payload
    except JWTError as e:
        raise HTTPException(status_code=401, detail=f"Token verification failed: {e}")
    