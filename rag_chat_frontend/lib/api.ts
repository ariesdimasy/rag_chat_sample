/**
 * Fungsi-fungsi untuk memanggil API.
 *
 * Perhatikan: kita TIDAK memanggil FastAPI backend langsung dari browser.
 * Kita memanggil "Route Handler" milik Next.js sendiri (/api/...), yang
 * kemudian meneruskan ke FastAPI. Kenapa begitu?
 *   1. API key backend tetap aman di server (tidak bocor ke browser)
 *   2. Menghindari masalah CORS
 *   3. Kita bisa mengubah/streaming respons di sisi server
 */

import type { IndexResponse } from "./types";

// ── Indeks dokumen ke knowledge base ──────────────────────────
export async function indexDocument(teks: string): Promise<IndexResponse> {
  const res = await fetch("/api/index", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ teks }),
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: "Gagal mengindeks dokumen." }));
    throw new Error(err.detail || "Gagal mengindeks dokumen.");
  }
  return res.json();
}

// ── Tanya (streaming) ─────────────────────────────────────────
/**
 * Mengirim pertanyaan dan menerima jawaban secara STREAMING
 * (mengalir sedikit demi sedikit, seperti ChatGPT).
 *
 * onToken dipanggil setiap ada potongan teks baru.
 * Mengembalikan daftar sumber di akhir.
 */
export async function askQuestionStream(
  pertanyaan: string,
  onToken: (token: string) => void,
): Promise<void> {
  const res = await fetch("/api/ask", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ pertanyaan, top_k: 3 }),
  });

  if (!res.ok || !res.body) {
    const err = await res.json().catch(() => ({ detail: "Gagal mendapat jawaban." }));
    throw new Error(err.detail || "Gagal mendapat jawaban.");
  }

  // Baca respons sebagai aliran (stream) potongan demi potongan
  const reader = res.body.getReader();
  const decoder = new TextDecoder();

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    const chunk = decoder.decode(value, { stream: true });
    onToken(chunk); // kirim potongan teks ke pemanggil
  }
}
