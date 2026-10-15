/**
 * Halaman utama (/).
 *
 * Layout: panel dokumen di kiri, jendela chat di kanan.
 * Ini Client Component karena perlu state (apakah dokumen sudah diindeks).
 */

"use client";

import { useState } from "react";
import { ChatWindow } from "@/components/ChatWindow";
import { DocumentPanel } from "@/components/DocumentPanel";

export default function Home() {
  // Melacak apakah knowledge base sudah punya dokumen
  const [siapDitanya, setSiapDitanya] = useState(false);
  const [jumlahChunk, setJumlahChunk] = useState(0);

  return (
    <main className="mx-auto flex h-screen max-w-6xl flex-col p-4">
      {/* Header */}
      <header className="mb-4">
        <h1 className="text-xl font-bold text-gray-800">
          🤖 RAG Chat Assistant
        </h1>
        <p className="text-sm text-gray-500">
          Frontend Next.js terhubung ke FastAPI backend (Meeting 20)
          {jumlahChunk > 0 && (
            <span className="ml-2 rounded-full bg-green-100 px-2 py-0.5 text-xs text-green-700">
              {jumlahChunk} chunk terindeks
            </span>
          )}
        </p>
      </header>

      {/* Body: 2 kolom */}
      <div className="grid flex-1 grid-cols-1 gap-4 overflow-hidden md:grid-cols-3">
        {/* Kiri: panel dokumen (1 kolom) */}
        <div className="md:col-span-1">
          <DocumentPanel
            onIndexed={(n) => {
              setJumlahChunk(n);
              setSiapDitanya(true);
            }}
          />
        </div>

        {/* Kanan: jendela chat (2 kolom) */}
        <div className="overflow-hidden rounded-2xl border border-gray-200 bg-white md:col-span-2">
          <ChatWindow siapDitanya={siapDitanya} />
        </div>
      </div>
    </main>
  );
}
