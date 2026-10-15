"""
Endpoint health check.

Endpoint /health dipakai untuk memeriksa apakah aplikasi hidup & siap.
Ini WAJIB di production — dipakai oleh load balancer, Docker, Kubernetes,
dan monitoring untuk tahu apakah server sehat.

Perhatikan: endpoint ini TIDAK butuh API key (harus bisa diakses bebas
agar sistem monitoring bisa mengeceknya).
"""
from fastapi import APIRouter

from app.core.config import settings
from app.models.schemas import HealthResponse
from app.services.rag_service import rag_service

router = APIRouter(tags=["Health"])


@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """Cek status aplikasi. Tidak butuh autentikasi."""
    return HealthResponse(
        status="ok",
        app_version=settings.app_version,
        model_siap=rag_service.model_siap,
        dokumen_terindeks=rag_service.jumlah_dokumen,
    )
