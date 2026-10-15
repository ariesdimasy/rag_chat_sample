/**
 * Route Handler: POST /api/ask
 *
 * Ini adalah "jembatan" antara browser dan FastAPI backend (M20).
 * Alurnya:
 *   Browser → /api/ask (Next.js server) → FastAPI /v1/ask → jawaban
 *
 * Backend M20 mengembalikan jawaban SEKALIGUS (bukan streaming). Di sini
 * kita "memecahnya" jadi potongan-potongan kecil dan mengalirkannya ke
 * browser (streaming) supaya terasa hidup seperti ChatGPT.
 *
 * Di production nyata, streaming biasanya langsung dari LLM. Tapi pola
 * ReadableStream di sini persis sama — jadi konsepnya tetap terpelajari.
 */

import { NextRequest } from "next/server";

import { getBackendEnv, missingBackendKeyResponse } from "@/lib/backend-env";

export async function POST(req: NextRequest) {
  const { apiBase, apiKey } = getBackendEnv();
  if (!apiKey) {
    return missingBackendKeyResponse();
  }

  try {
    const body = await req.json();

    // 1. Panggil FastAPI backend
    const backendRes = await fetch(`${apiBase}/v1/ask`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-API-Key": apiKey,
      },
      body: JSON.stringify({
        pertanyaan: body.pertanyaan,
        top_k: body.top_k ?? 3,
      }),
    });

    if (!backendRes.ok) {
      const err = await backendRes.json().catch(() => ({}));
      return Response.json(
        { detail: err.detail || "Backend menolak permintaan." },
        { status: backendRes.status },
      );
    }

    const data = await backendRes.json();
    const jawaban: string = data.jawaban ?? "";

    // 2. Alirkan jawaban kata demi kata (streaming)
    const encoder = new TextEncoder();
    const stream = new ReadableStream({
      async start(controller) {
        const kata = jawaban.split(" ");
        for (let i = 0; i < kata.length; i++) {
          // Kirim satu kata (plus spasi)
          const potongan = i === 0 ? kata[i] : " " + kata[i];
          controller.enqueue(encoder.encode(potongan));
          // Jeda kecil supaya terlihat "mengetik"
          await new Promise((r) => setTimeout(r, 35));
        }
        controller.close();
      },
    });

    return new Response(stream, {
      headers: {
        "Content-Type": "text/plain; charset=utf-8",
        "Cache-Control": "no-cache",
      },
    });
  } catch (e) {
    return Response.json(
      { detail: "Tidak bisa terhubung ke backend. Pastikan API M20 berjalan." },
      { status: 502 },
    );
  }
}
