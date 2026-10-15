/**
 * Route Handler: POST /api/index
 *
 * Meneruskan permintaan "indeks dokumen" ke FastAPI backend (M20).
 * Browser → /api/index (Next.js) → FastAPI /v1/index
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

    const backendRes = await fetch(`${apiBase}/v1/index`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-API-Key": apiKey,
      },
      body: JSON.stringify({ teks: body.teks }),
    });

    const data = await backendRes.json();

    if (!backendRes.ok) {
      return Response.json(
        { detail: data.detail || "Gagal mengindeks dokumen." },
        { status: backendRes.status },
      );
    }

    return Response.json(data);
  } catch (e) {
    return Response.json(
      { detail: "Tidak bisa terhubung ke backend. Pastikan API M20 berjalan." },
      { status: 502 },
    );
  }
}
