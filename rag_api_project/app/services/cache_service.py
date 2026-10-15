"""
Cache sederhana untuk menyimpan jawaban.

Di production, cache biasanya pakai Redis. Untuk pembelajaran, kita pakai
dictionary di memori dengan batas waktu (TTL) — konsepnya sama persis:

  - Pertanyaan yang sama → jawaban diambil dari cache (cepat, hemat biaya API)
  - Setelah TTL habis → cache dianggap kadaluarsa

Cara upgrade ke Redis nanti: ganti isi class ini dengan panggilan redis,
tapi antarmuka (get/set) tetap sama.
"""
import time


class CacheService:
    def __init__(self, ttl_detik: int = 300) -> None:
        # ttl = time-to-live: berapa lama cache dianggap valid (detik)
        self._ttl = ttl_detik
        self._store: dict[str, tuple[str, float]] = {}

    def _kunci(self, pertanyaan: str, top_k: int) -> str:
        # Normalisasi agar "Halo" dan "halo " dianggap sama
        return f"{pertanyaan.strip().lower()}::{top_k}"

    def get(self, pertanyaan: str, top_k: int) -> str | None:
        """Ambil jawaban dari cache. None kalau tidak ada / kadaluarsa."""
        kunci = self._kunci(pertanyaan, top_k)
        item = self._store.get(kunci)
        if item is None:
            return None
        jawaban, waktu_simpan = item
        # Cek apakah sudah kadaluarsa
        if time.time() - waktu_simpan > self._ttl:
            del self._store[kunci]
            return None
        return jawaban

    def set(self, pertanyaan: str, top_k: int, jawaban: str) -> None:
        """Simpan jawaban ke cache."""
        kunci = self._kunci(pertanyaan, top_k)
        self._store[kunci] = (jawaban, time.time())

    def bersihkan(self) -> None:
        self._store.clear()

    @property
    def ukuran(self) -> int:
        return len(self._store)


# Instance global
cache_service = CacheService(ttl_detik=300)
