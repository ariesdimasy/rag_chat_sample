"""
Konfigurasi aplikasi.

Semua pengaturan (API key, model, dll) dibaca dari environment variable
dan file `.env` di root proyek (via pydantic-settings).

JANGAN pakai os.getenv() sebagai default field — itu jalan sebelum .env dimuat.
"""
from pathlib import Path

from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

# rag_api_project/.env (relatif ke file ini: app/core/config.py)
_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
_ENV_FILE = _PROJECT_ROOT / ".env"

# Muat .env ke os.environ dulu (supaya os.getenv() juga konsisten setelah import ini)
if _ENV_FILE.is_file():
    load_dotenv(_ENV_FILE, encoding="utf-8")


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=_ENV_FILE,
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # --- Info Aplikasi ---
    app_name: str = "RAG API - Meeting 20"
    app_version: str = "1.0.0"

    # --- Keamanan ---
    # API key yang diperbolehkan mengakses endpoint (dipisah koma di .env)
    # Contoh di .env:  API_KEYS=kunci-rahasia-1,kunci-rahasia-2
    api_keys: str = ""

    # --- DeepSeek (untuk generation RAG) ---
    deepseek_api_key: str = ""
    deepseek_base_url: str = "https://api.deepseek.com"
    deepseek_model: str = "deepseek-v4-flash"

    # --- Model Embedding (retrieval, gratis lokal) ---
    embedding_model: str = "paraphrase-multilingual-MiniLM-L12-v2"

    # --- Rate limiting ---
    rate_limit: str = "10/minute"

    @property
    def allowed_api_keys(self) -> set[str]:
        """Ubah string 'a,b,c' jadi himpunan {a, b, c}."""
        return {k.strip() for k in self.api_keys.split(",") if k.strip()}


# Satu instance global yang dipakai di seluruh aplikasi
settings = Settings()
