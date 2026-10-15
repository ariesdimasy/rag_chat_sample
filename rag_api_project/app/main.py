"""
Titik masuk aplikasi FastAPI.

Jalankan dengan:
    uvicorn app.main:app --reload

Lalu buka dokumentasi interaktif di:
    http://localhost:8000/docs
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.core.config import settings
from app.routers import health, rag
from app.routers.rag import limiter
from app.services.rag_service import rag_service


# ── Lifespan: kode yang jalan saat startup & shutdown ──────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    # STARTUP: muat model sekali di awal (singleton pattern)
    print("Aplikasi dimulai - memuat model...")
    rag_service.muat_model()
    yield
    # SHUTDOWN: bersih-bersih kalau perlu
    print("Aplikasi berhenti.")


# ── Buat aplikasi ──────────────────────────────────────────────
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description=(
        "REST API production-ready untuk sistem RAG.\n\n"
        "Fitur: autentikasi API key, rate limiting, caching, dan dokumentasi otomatis.\n\n"
        "**Cara pakai:** indeks dokumen lewat `/v1/index`, lalu tanya lewat `/v1/ask`. "
        "Sertakan header `X-API-Key` di setiap request."
    ),
    lifespan=lifespan,
)

# ── Rate limiting ──────────────────────────────────────────────
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# ── CORS: izinkan frontend (Next.js dll) memanggil API ini ─────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],       # di production, ganti dengan domain frontend spesifik
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Error handler global untuk error tak terduga ───────────────
@app.exception_handler(Exception)
async def error_tak_terduga(request: Request, exc: Exception):
    # Jangan bocorkan detail internal — cukup pesan umum
    return JSONResponse(
        status_code=500,
        content={"detail": "Terjadi kesalahan internal. Silakan coba lagi."},
    )


# ── Daftarkan router ───────────────────────────────────────────
app.include_router(health.router)
app.include_router(rag.router)


# ── Endpoint root (info singkat) ───────────────────────────────
@app.get("/", tags=["Info"])
async def root():
    return {
        "app": settings.app_name,
        "version": settings.app_version,
        "dokumentasi": "/docs",
        "health": "/health",
    }
