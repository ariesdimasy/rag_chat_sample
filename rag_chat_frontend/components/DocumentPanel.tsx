/**
 * Komponen: panel untuk memasukkan dokumen ke knowledge base.
 *
 * Pengguna menempel teks dokumen, klik "Indeks", lalu sistem RAG bisa
 * menjawab pertanyaan berdasarkan dokumen itu.
 */

"use client";

import { useState } from "react";
import { indexDocument } from "@/lib/api";

const CONTOH_DOKUMEN = `TokoBapak adalah aplikasi marketplace untuk warung dan toko kelontong. Didirikan tahun 2023 di Bandung.

Paket Premium seharga Rp149.000 per bulan menawarkan produk tak terbatas, laporan analitik lengkap, dan dukungan prioritas 24 jam.

Metode pembayaran meliputi transfer bank, GoPay, OVO, dan kartu kredit. Pencairan dana ke penjual setiap Senin dan Kamis.`;

interface DocumentPanelProps {
  onIndexed: (jumlahChunk: number) => void;
}

export function DocumentPanel({ onIndexed }: DocumentPanelProps) {
  const [teks, setTeks] = useState(CONTOH_DOKUMEN);
  const [loading, setLoading] = useState(false);
  const [pesan, setPesan] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function handleIndex() {
    setLoading(true);
    setPesan(null);
    setError(null);
    try {
      const hasil = await indexDocument(teks);
      setPesan(hasil.pesan);
      onIndexed(hasil.jumlah_chunk);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Terjadi kesalahan.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="rounded-2xl border border-gray-200 bg-white p-4">
      <h2 className="text-sm font-semibold text-gray-700 mb-2">
        📚 Knowledge Base
      </h2>
      <p className="text-xs text-gray-500 mb-3">
        Tempel dokumen di bawah, lalu klik Indeks. Sistem akan bisa menjawab
        pertanyaan berdasarkan isi dokumen ini.
      </p>

      <textarea
        value={teks}
        onChange={(e) => setTeks(e.target.value)}
        rows={8}
        className="w-full resize-none rounded-xl border border-gray-300 p-3 text-xs
                   focus:outline-none focus:ring-2 focus:ring-indigo-500"
      />

      <button
        onClick={handleIndex}
        disabled={loading || teks.trim().length < 10}
        className="mt-3 w-full rounded-xl bg-gray-800 px-4 py-2 text-sm font-medium
                   text-white hover:bg-gray-900 disabled:bg-gray-300"
      >
        {loading ? "Mengindeks..." : "Indeks Dokumen"}
      </button>

      {/* Notifikasi hasil */}
      {pesan && (
        <div className="mt-2 rounded-lg bg-green-50 border border-green-200 p-2 text-xs text-green-700">
          ✅ {pesan}
        </div>
      )}
      {error && (
        <div className="mt-2 rounded-lg bg-red-50 border border-red-200 p-2 text-xs text-red-700">
          ⚠️ {error}
        </div>
      )}
    </div>
  );
}
