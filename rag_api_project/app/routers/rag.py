"""
Endpoint utama RAG: /index dan /ask.

Kedua endpoint ini:
- Dilindungi API key (Depends(verify_api_key))
- Kena rate limit (biar tidak ada yang spam)
- Punya penanganan error yang rapi
"""
from fastapi import APIRouter, Depends, HTTPException, Request, status
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.core.config import settings
from app.core.security import verify_api_key
from app.models.schemas import (
    AskRequest,
    AskResponse,
    IndexRequest,
    IndexResponse,
    SumberChunk,
)
from app.services.cache_service import cache_service
from app.services.rag_service import rag_service

# Limiter memakai alamat IP pemanggil sebagai identitas
limiter = Limiter(key_func=get_remote_address)

router = APIRouter(prefix="/v1", tags=["RAG"])


@router.post(
    "/index",
    response_model=IndexResponse,
    summary="Indeks dokumen ke knowledge base",
    dependencies=[Depends(verify_api_key)],
)
@limiter.limit(settings.rate_limit)
async def index_dokumen(request: Request, body: IndexRequest) -> IndexResponse:
    """
    Memasukkan dokumen ke knowledge base RAG.

    Dokumen akan dipecah jadi potongan (chunk), diubah jadi vektor,
    lalu disimpan agar bisa dicari saat ada pertanyaan.
    """
    if not rag_service.model_siap:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Model belum siap. Coba lagi beberapa saat.",
        )

    jumlah = rag_service.index_dokumen(body.teks)
    # Dokumen baru → cache lama tidak relevan lagi
    cache_service.bersihkan()

    return IndexResponse(
        jumlah_chunk=jumlah,
        pesan=f"Dokumen berhasil diindeks menjadi {jumlah} potongan.",
    )


@router.post(
    "/ask",
    response_model=AskResponse,
    summary="Tanya jawab berbasis dokumen (RAG)",
    dependencies=[Depends(verify_api_key)],
)
@limiter.limit(settings.rate_limit)
async def tanya_rag(request: Request, body: AskRequest) -> AskResponse:
    """
    Mengajukan pertanyaan yang dijawab berdasarkan dokumen yang sudah diindeks.

    Alur: cek cache → kalau tidak ada, jalankan RAG → simpan ke cache.
    """
    if rag_service.jumlah_dokumen == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Belum ada dokumen. Indeks dokumen dulu lewat /v1/index.",
        )

    # 1. Cek cache dulu (hemat biaya API & lebih cepat)
    cached = cache_service.get(body.pertanyaan, body.top_k)
    if cached is not None:
        return AskResponse(
            pertanyaan=body.pertanyaan,
            jawaban=cached,
            sumber=[],
            dari_cache=True,
        )

    # 2. Jalankan pipeline RAG
    try:
        jawaban, hasil = rag_service.tanya(body.pertanyaan, top_k=body.top_k)
    except Exception as e:
        # Jangan bocorkan detail internal ke pengguna
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Gagal menghasilkan jawaban: {type(e).__name__}",
        )

    # 3. Simpan ke cache untuk pertanyaan serupa berikutnya
    cache_service.set(body.pertanyaan, body.top_k, jawaban)

    sumber = [SumberChunk(isi=chunk, skor=skor) for chunk, skor in hasil]
    return AskResponse(
        pertanyaan=body.pertanyaan,
        jawaban=jawaban,
        sumber=sumber,
        dari_cache=False,
    )
