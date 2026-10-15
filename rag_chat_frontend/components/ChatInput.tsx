/**
 * Komponen: kotak input untuk mengetik pertanyaan.
 *
 * "use client" menandai ini Client Component — bisa pakai interaktivitas
 * (useState, onClick, dll). Komponen tanpa penanda ini adalah Server
 * Component (default di Next.js App Router).
 */

"use client";

import { useState } from "react";

interface ChatInputProps {
  onSend: (pesan: string) => void;
  disabled: boolean;
}

export function ChatInput({ onSend, disabled }: ChatInputProps) {
  const [teks, setTeks] = useState("");

  function handleSubmit() {
    const bersih = teks.trim();
    if (!bersih || disabled) return;
    onSend(bersih);
    setTeks(""); // kosongkan input setelah kirim
  }

  function handleKeyDown(e: React.KeyboardEvent) {
    // Enter untuk kirim, Shift+Enter untuk baris baru
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  }

  return (
    <div className="flex gap-2 items-end">
      <textarea
        value={teks}
        onChange={(e) => setTeks(e.target.value)}
        onKeyDown={handleKeyDown}
        disabled={disabled}
        placeholder="Tanya sesuatu tentang dokumen..."
        rows={1}
        className="flex-1 resize-none rounded-xl border border-gray-300 px-4 py-3 text-sm
                   focus:outline-none focus:ring-2 focus:ring-indigo-500 disabled:bg-gray-100"
      />
      <button
        onClick={handleSubmit}
        disabled={disabled || !teks.trim()}
        className="rounded-xl bg-indigo-600 px-5 py-3 text-sm font-medium text-white
                   hover:bg-indigo-700 disabled:cursor-not-allowed disabled:bg-gray-300"
      >
        {disabled ? "..." : "Kirim"}
      </button>
    </div>
  );
}
