"""
Autentikasi sederhana berbasis API Key.

Setiap request harus menyertakan header:
    X-API-Key: <kunci-rahasia>

Kalau kunci tidak valid, request ditolak dengan error 401 (Unauthorized).
"""
from fastapi import Security, HTTPException, status
from fastapi.security import APIKeyHeader

from app.core.config import settings

# Beri tahu FastAPI kita pakai header bernama "X-API-Key"
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


async def verify_api_key(api_key: str = Security(api_key_header)) -> str:
    """
    Dependency yang mengecek apakah API key valid.

    Dipakai di endpoint dengan:  Depends(verify_api_key)
    """
    if api_key is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Header 'X-API-Key' tidak ditemukan. Sertakan API key Anda.",
        )
    if api_key not in settings.allowed_api_keys:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key tidak valid.",
        )
    return api_key
