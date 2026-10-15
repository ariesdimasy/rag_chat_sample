# 🚀 RAG API — Meeting 20: Deployment I dengan FastAPI

Proyek ini membungkus sistem **RAG** (dari Meeting 19) menjadi **REST API production-ready** menggunakan **FastAPI**. Inilah langkah pertama mengubah model AI dari notebook menjadi aplikasi nyata yang bisa dipakai orang lain lewat internet.

---

## 🎯 Apa yang Dipelajari di Sini?

| Konsep | File Terkait |
|--------|--------------|
| Struktur proyek FastAPI yang rapi | seluruh folder `app/` |
| Pydantic models (validasi otomatis) | `app/models/schemas.py` |
| Autentikasi dengan API Key | `app/core/security.py` |
| Rate limiting (cegah spam) | `app/routers/rag.py` |
| Caching (hemat biaya & lebih cepat) | `app/services/cache_service.py` |
| Model loading sekali saat startup | `app/main.py` (lifespan) |
| Health check untuk monitoring | `app/routers/health.py` |
| Error handling yang aman | `app/main.py` |
| Testing otomatis | `tests/test_api.py` |
| Load testing | `locustfile.py` |

---

## 📁 Struktur Proyek

```
rag_api_project/
├── app/
│   ├── main.py               # Titik masuk: merangkai semua komponen
│   ├── core/
│   │   ├── config.py         # Konfigurasi dari environment variable
│   │   └── security.py       # Autentikasi API key
│   ├── models/
│   │   └── schemas.py        # Pydantic models (request & response)
│   ├── routers/
│   │   ├── health.py         # Endpoint /health
│   │   └── rag.py            # Endpoint /v1/index & /v1/ask
│   └── services/
│       ├── rag_service.py    # Logika RAG (retrieve + generate)
│       └── cache_service.py  # Cache jawaban
├── tests/
│   └── test_api.py           # Test otomatis (pytest)
├── locustfile.py             # Load testing
├── requirements.txt          # Daftar dependency
├── .env.example              # Template konfigurasi
└── README.md
```

---

## ⚙️ Cara Menjalankan

### 1. Siapkan environment

```bash
# Buat virtual environment
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate

# Install dependency
pip install -r requirements.txt
```

### 2. Atur konfigurasi

```bash
# Salin template lalu isi nilainya
cp .env.example .env
```

Buka `.env` dan isi `DEEPSEEK_API_KEY` (daftar gratis di [platform.deepseek.com](https://platform.deepseek.com)).

> 💡 Kalau `DEEPSEEK_API_KEY` dikosongkan, API tetap jalan dalam **mode retrieval-only** (hanya mengembalikan potongan dokumen relevan, tanpa jawaban LLM). Cocok untuk mencoba tanpa API key.

### 3. Jalankan server

```bash
uvicorn app.main:app --reload
```

Server jalan di `http://localhost:8000`.

### 4. Buka dokumentasi interaktif

Kunjungi **http://localhost:8000/docs** — Swagger UI otomatis dari FastAPI. Kamu bisa mencoba semua endpoint langsung dari browser!

---

## 📡 Contoh Penggunaan

### Cek kesehatan (tanpa API key)

```bash
curl http://localhost:8000/health
```

### Indeks dokumen (butuh API key)

```bash
curl -X POST http://localhost:8000/v1/index \
  -H "X-API-Key: kunci-rahasia-belajar" \
  -H "Content-Type: application/json" \
  -d '{"teks": "TokoBapak adalah marketplace. Paket Premium Rp149.000 per bulan."}'
```

### Bertanya (butuh API key)

```bash
curl -X POST http://localhost:8000/v1/ask \
  -H "X-API-Key: kunci-rahasia-belajar" \
  -H "Content-Type: application/json" \
  -d '{"pertanyaan": "Berapa harga paket Premium?", "top_k": 2}'
```

---

## 🧪 Menjalankan Test

```bash
pytest -v
```

Test mencakup: health check, autentikasi (key valid/invalid), indexing, validasi input, dan retrieval.

---

## 🔥 Load Testing (Opsional)

```bash
# Terminal 1: jalankan API
uvicorn app.main:app

# Terminal 2: jalankan Locust
locust -f locustfile.py --host http://localhost:8000
```

Buka `http://localhost:8089`, atur jumlah pengguna, dan lihat apakah API sanggup **100 req/s dengan latency p99 < 2 detik**.

---

## 🔒 Catatan Keamanan

- **API key & rahasia** disimpan di `.env` (tidak di-commit ke Git).
- Endpoint `/v1/*` dilindungi API key; `/health` sengaja terbuka untuk monitoring.
- Error internal tidak membocorkan detail teknis ke pengguna.
- Di production: ganti `allow_origins=["*"]` (CORS) dengan domain frontend spesifik.

---

## 🚀 Selanjutnya (Meeting 21)

API ini akan dihubungkan dengan **frontend Next.js** — membuat antarmuka chat yang memanggil endpoint `/v1/ask` ini. Lalu Docker (M22), Nginx (M23), dan CI/CD + monitoring (M24).
