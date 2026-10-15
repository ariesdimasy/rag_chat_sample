/**
 * Konfigurasi backend (server-only).
 * Baca env di dalam fungsi agar nilai .env / .env.local terbaca saat runtime
 * (bukan hanya saat build Next.js).
 */

export function getBackendEnv(): { apiBase: string; apiKey: string } {
  const apiBase = process.env.BACKEND_URL?.trim() || "http://localhost:8000";
  const apiKey = process.env.BACKEND_API_KEY?.trim() || "";

  return { apiBase, apiKey };
}

export function missingBackendKeyResponse() {
  return Response.json(
    {
      detail:
        "BACKEND_API_KEY belum di-set. Salin .env.local.example ke .env.local (atau .env) lalu isi API key yang sama dengan API_KEYS di backend.",
    },
    { status: 500 },
  );
}
