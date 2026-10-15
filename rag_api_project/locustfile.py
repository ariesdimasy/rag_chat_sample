"""
Load testing dengan Locust.

Locust mensimulasikan banyak pengguna mengakses API bersamaan,
untuk mengukur apakah API sanggup menangani beban tinggi.

Cara pakai:
1. Jalankan API dulu:  uvicorn app.main:app
2. Jalankan Locust:    locust -f locustfile.py --host http://localhost:8000
3. Buka http://localhost:8089, atur jumlah user, dan mulai.

Target Meeting 20: lulus 100 req/s dengan latency p99 < 2 detik.
"""
from locust import HttpUser, task, between

API_KEY = "kunci-rahasia-belajar"
HEADERS = {"X-API-Key": API_KEY}

DOKUMEN = (
    "TokoBapak adalah aplikasi marketplace. "
    "Paket Premium seharga Rp149.000 per bulan dengan produk tak terbatas."
)


class PenggunaAPI(HttpUser):
    # Jeda 1-3 detik antar request (meniru pengguna nyata)
    wait_time = between(1, 3)

    def on_start(self):
        """Dijalankan sekali saat user mulai: indeks dokumen dulu."""
        self.client.post("/v1/index", json={"teks": DOKUMEN}, headers=HEADERS)

    @task(3)  # bobot 3x lebih sering
    def health_check(self):
        self.client.get("/health")

    @task(1)
    def tanya(self):
        self.client.post(
            "/v1/ask",
            json={"pertanyaan": "berapa harga paket premium", "top_k": 2},
            headers=HEADERS,
        )
