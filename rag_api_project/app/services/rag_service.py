"""
Service RAG — inti logika bisnis.

Ini adalah versi "production" dari RAG yang kita bangun di Meeting 19,
tapi dikemas jadi sebuah class yang rapi dan bisa dipakai oleh API.

Alur RAG: Retrieve (cari) -> Augment (susun konteks) -> Generate (jawab).
"""
import numpy as np
from openai import OpenAI
from sentence_transformers import SentenceTransformer

from app.core.config import settings


def chunk_teks(teks: str, ukuran: int = 250, overlap: int = 50) -> list[str]:
    """Pecah teks panjang jadi potongan kecil (chunk) dengan sedikit overlap."""
    paragraf = [p.strip() for p in teks.split("\n\n") if p.strip()]
    chunks: list[str] = []
    for para in paragraf:
        if len(para) <= ukuran:
            chunks.append(para)
        else:
            start = 0
            while start < len(para):
                chunks.append(para[start:start + ukuran])
                start += ukuran - overlap
    return chunks


class RAGService:
    """
    Membungkus seluruh pipeline RAG.

    Model embedding dimuat SEKALI saat startup (singleton pattern),
    bukan tiap request — ini penting agar API cepat & hemat memori.
    """

    def __init__(self) -> None:
        self._embedder: SentenceTransformer | None = None
        self._client: OpenAI | None = None
        self._chunks: list[str] = []
        self._chunk_embeddings: np.ndarray | None = None

    # ── Startup: muat model sekali ──────────────────────────────
    def muat_model(self) -> None:
        """Dipanggil saat aplikasi start. Memuat model embedding & client LLM."""
        print("Memuat model embedding...")
        self._embedder = SentenceTransformer(settings.embedding_model)
        print("Model embedding siap.")

        if settings.deepseek_api_key:
            self._client = OpenAI(
                api_key=settings.deepseek_api_key,
                base_url=settings.deepseek_base_url,
            )
            print("Client DeepSeek siap.")
        else:
            print("DEEPSEEK_API_KEY kosong - mode retrieval-only.")

    @property
    def model_siap(self) -> bool:
        return self._embedder is not None

    @property
    def jumlah_dokumen(self) -> int:
        return len(self._chunks)

    # ── Indexing: masukkan dokumen ke knowledge base ────────────
    def index_dokumen(self, teks: str) -> int:
        """Chunk + embed dokumen, simpan di memori. Kembalikan jumlah chunk."""
        if self._embedder is None:
            raise RuntimeError("Model belum dimuat.")

        self._chunks = chunk_teks(teks)
        emb = self._embedder.encode(self._chunks)
        # Normalisasi agar bisa pakai cosine similarity via dot product
        emb = emb / np.linalg.norm(emb, axis=1, keepdims=True)
        self._chunk_embeddings = emb.astype("float32")
        return len(self._chunks)

    # ── Retrieve: cari chunk paling relevan ─────────────────────
    def retrieve(self, query: str, top_k: int = 2) -> list[tuple[str, float]]:
        """Kembalikan daftar (chunk, skor) paling relevan dengan query."""
        if self._chunk_embeddings is None or not self._chunks:
            return []

        q_emb = self._embedder.encode([query])
        q_emb = q_emb / np.linalg.norm(q_emb, axis=1, keepdims=True)

        # Cosine similarity = dot product (karena sudah dinormalisasi)
        skor = (self._chunk_embeddings @ q_emb[0])
        top_idx = np.argsort(skor)[::-1][:top_k]
        return [(self._chunks[i], float(skor[i])) for i in top_idx]

    # ── Generate: LLM menjawab berdasarkan konteks ──────────────
    def _buat_prompt(self, query: str, konteks: list[str]) -> str:
        gabung = "\n\n".join(f"[Dokumen {i+1}]\n{c}" for i, c in enumerate(konteks))
        return (
            "Jawab pertanyaan HANYA berdasarkan konteks di bawah ini. "
            'Jika informasi tidak ada, katakan "Maaf, informasi itu tidak '
            'tersedia dalam dokumen." Jangan mengarang.\n\n'
            f"=== KONTEKS ===\n{gabung}\n\n"
            f"=== PERTANYAAN ===\n{query}\n\n=== JAWABAN ==="
        )

    def generate(self, query: str, konteks: list[str]) -> str:
        """Panggil DeepSeek untuk menghasilkan jawaban dari konteks."""
        if self._client is None:
            # Fallback kalau tak ada API key: kembalikan konteks mentah
            return (
                "[Mode retrieval-only — API key DeepSeek belum diatur]\n"
                "Potongan dokumen paling relevan:\n" + "\n---\n".join(konteks)
            )

        prompt = self._buat_prompt(query, konteks)
        resp = self._client.chat.completions.create(
            model=settings.deepseek_model,
            messages=[
                {"role": "system", "content": "Kamu asisten yang menjawab akurat berdasarkan dokumen."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.2,
            max_tokens=512,
        )
        return resp.choices[0].message.content

    # ── Pipeline lengkap ────────────────────────────────────────
    def tanya(self, query: str, top_k: int = 2) -> tuple[str, list[tuple[str, float]]]:
        """Pipeline RAG penuh. Kembalikan (jawaban, daftar sumber)."""
        hasil = self.retrieve(query, top_k=top_k)
        if not hasil:
            return ("Belum ada dokumen yang diindeks. Silakan indeks dokumen dulu.", [])
        konteks = [chunk for chunk, _ in hasil]
        jawaban = self.generate(query, konteks)
        return jawaban, hasil


# Instance global (singleton) — dipakai bersama seluruh aplikasi
rag_service = RAGService()
