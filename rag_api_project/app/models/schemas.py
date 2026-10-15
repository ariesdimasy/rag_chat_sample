"""
Skema data (Pydantic models).

Pydantic memvalidasi otomatis data yang masuk & keluar API:
- Kalau request tidak sesuai bentuk → FastAPI otomatis kirim error 422 yang jelas
- Response dijamin bentuknya konsisten
- Dokumentasi Swagger otomatis dibuat dari skema ini
"""
from pydantic import BaseModel, Field


# ─────────────────────────────────────────────────────────────
# REQUEST: data yang dikirim pengguna ke API
# ─────────────────────────────────────────────────────────────
class IndexRequest(BaseModel):
    """Untuk memasukkan dokumen ke knowledge base."""
    teks: str = Field(
        ...,
        min_length=10,
        description="Isi dokumen yang akan diindeks untuk pencarian.",
        examples=["TokoBapak adalah aplikasi marketplace untuk warung..."],
    )


class AskRequest(BaseModel):
    """Untuk bertanya ke sistem RAG."""
    pertanyaan: str = Field(
        ...,
        min_length=3,
        max_length=500,
        description="Pertanyaan yang ingin dijawab berdasarkan dokumen.",
        examples=["Berapa harga paket Premium?"],
    )
    top_k: int = Field(
        default=2,
        ge=1,
        le=5,
        description="Jumlah potongan dokumen yang diambil sebagai konteks.",
    )


# ─────────────────────────────────────────────────────────────
# RESPONSE: data yang dikembalikan API ke pengguna
# ─────────────────────────────────────────────────────────────
class IndexResponse(BaseModel):
    status: str = "sukses"
    jumlah_chunk: int = Field(..., description="Banyaknya potongan dokumen yang tersimpan.")
    pesan: str


class SumberChunk(BaseModel):
    """Satu potongan dokumen yang dipakai sebagai sumber jawaban."""
    isi: str
    skor: float = Field(..., description="Skor relevansi (0-1, makin tinggi makin relevan).")


class AskResponse(BaseModel):
    pertanyaan: str
    jawaban: str
    sumber: list[SumberChunk] = Field(
        default_factory=list,
        description="Potongan dokumen yang jadi dasar jawaban (untuk verifikasi).",
    )
    dari_cache: bool = Field(
        default=False,
        description="True kalau jawaban diambil dari cache (lebih cepat).",
    )


class HealthResponse(BaseModel):
    status: str
    app_version: str
    model_siap: bool = Field(..., description="Apakah model embedding sudah dimuat.")
    dokumen_terindeks: int = Field(..., description="Jumlah dokumen di knowledge base.")


class ErrorResponse(BaseModel):
    detail: str
