# app/limiter.py

from slowapi import Limiter
from slowapi.util import get_remote_address
from fastapi import Request

def get_user_id_or_ip(request: Request):
    user = getattr(request.state, "user", None)
    return str(user.id) if user else get_remote_address(request)

limiter = Limiter(key_func=get_user_id_or_ip)
