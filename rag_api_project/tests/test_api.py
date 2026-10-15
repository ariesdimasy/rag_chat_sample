"""
Test otomatis untuk API menggunakan pytest.

Jalankan dengan:
    pytest -v

Test memakai TestClient dari FastAPI — server tidak perlu dijalankan manual.
"""
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.core.config import settings

# API key valid untuk testing (dari config default)
API_KEY = list(settings.allowed_api_keys)[0]
HEADERS = {"X-API-Key": API_KEY}

DOKUMEN_CONTOH = """
TokoBapak adalah aplikasi marketplace untuk warung dan toko kelontong.
Aplikasi ini didirikan pada tahun 2023 di Bandung.

Paket Premium seharga Rp149.000 per bulan menawarkan produk tak terbatas,
laporan analitik lengkap, dan dukungan prioritas 24 jam.
"""


@pytest.fixture(scope="module")
def client():
    # 'with' memicu lifespan → model dimuat sebelum test
    with TestClient(app) as c:
        yield c


# ── Test health check ──────────────────────────────────────────
def test_health(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"
    assert data["model_siap"] is True


def test_root(client):
    resp = client.get("/")
    assert resp.status_code == 200
    assert "dokumentasi" in resp.json()


# ── Test autentikasi ───────────────────────────────────────────
def test_ask_tanpa_api_key_ditolak(client):
    resp = client.post("/v1/ask", json={"pertanyaan": "halo dunia"})
    assert resp.status_code == 401  # Unauthorized


def test_ask_api_key_salah_ditolak(client):
    resp = client.post(
        "/v1/ask",
        json={"pertanyaan": "halo dunia"},
        headers={"X-API-Key": "kunci-palsu"},
    )
    assert resp.status_code == 401


# ── Test indexing ──────────────────────────────────────────────
def test_index_dokumen(client):
    resp = client.post("/v1/index", json={"teks": DOKUMEN_CONTOH}, headers=HEADERS)
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "sukses"
    assert data["jumlah_chunk"] >= 1


# ── Test validasi input ────────────────────────────────────────
def test_ask_pertanyaan_terlalu_pendek_ditolak(client):
    # pertanyaan < 3 karakter → harus ditolak Pydantic (422)
    resp = client.post("/v1/ask", json={"pertanyaan": "hi"}, headers=HEADERS)
    assert resp.status_code == 422  # Unprocessable Entity


def test_ask_top_k_di_luar_batas_ditolak(client):
    # top_k harus 1-5; 99 harus ditolak
    resp = client.post(
        "/v1/ask",
        json={"pertanyaan": "berapa harga premium", "top_k": 99},
        headers=HEADERS,
    )
    assert resp.status_code == 422


# ── Test retrieval (tanpa perlu API key DeepSeek) ──────────────
def test_ask_mengembalikan_sumber(client):
    # Pastikan dokumen sudah diindeks dulu
    client.post("/v1/index", json={"teks": DOKUMEN_CONTOH}, headers=HEADERS)

    resp = client.post(
        "/v1/ask",
        json={"pertanyaan": "berapa harga paket premium", "top_k": 2},
        headers=HEADERS,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "jawaban" in data
    # Retrieval harus menemukan chunk yang menyebut "Premium"
    assert len(data["sumber"]) >= 1
    gabungan = " ".join(s["isi"] for s in data["sumber"]).lower()
    assert "premium" in gabungan
