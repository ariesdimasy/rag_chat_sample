/**
 * Komponen inti: jendela chat.
 *
 * Mengelola:
 *   - daftar pesan (state)
 *   - mengirim pertanyaan & menerima jawaban streaming
 *   - auto-scroll ke pesan terbaru
 */

"use client";

import { useState, useRef, useEffect } from "react";
import { ChatMessage } from "./ChatMessage";
import { ChatInput } from "./ChatInput";
import { askQuestionStream } from "@/lib/api";
import type { ChatMessage as Message } from "@/lib/types";

// Buat id unik sederhana untuk tiap pesan
function buatId() {
  return Math.random().toString(36).slice(2);
}

export function ChatWindow({ siapDitanya }: { siapDitanya: boolean }) {
  const [pesanList, setPesanList] = useState<Message[]>([]);
  const [loading, setLoading] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);

  // Auto-scroll ke bawah setiap ada pesan baru
  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: "smooth" });
  }, [pesanList]);

  async function handleSend(pertanyaan: string) {
    // 1. Tambahkan pesan user
    const pesanUser: Message = { id: buatId(), role: "user", content: pertanyaan };
    setPesanList((prev) => [...prev, pesanUser]);

    // 2. Siapkan pesan asisten kosong (akan diisi streaming)
    const idAsisten = buatId();
    const pesanAsisten: Message = {
      id: idAsisten,
      role: "assistant",
      content: "",
      isStreaming: true,
    };
    setPesanList((prev) => [...prev, pesanAsisten]);
    setLoading(true);

    try {
      // 3. Terima jawaban streaming, update pesan asisten tiap ada token baru
      await askQuestionStream(pertanyaan, (token) => {
        setPesanList((prev) =>
          prev.map((m) =>
            m.id === idAsisten ? { ...m, content: m.content + token } : m,
          ),
        );
      });
    } catch (e) {
      const msg = e instanceof Error ? e.message : "Terjadi kesalahan.";
      setPesanList((prev) =>
        prev.map((m) =>
          m.id === idAsisten ? { ...m, content: `⚠️ ${msg}` } : m,
        ),
      );
    } finally {
      // 4. Tandai streaming selesai
      setPesanList((prev) =>
        prev.map((m) => (m.id === idAsisten ? { ...m, isStreaming: false } : m)),
      );
      setLoading(false);
    }
  }

  return (
    <div className="flex flex-col h-full">
      {/* Area pesan */}
      <div ref={scrollRef} className="flex-1 overflow-y-auto p-4">
        {pesanList.length === 0 ? (
          <div className="flex h-full items-center justify-center text-center">
            <div className="text-gray-400">
              <div className="text-4xl mb-2">💬</div>
              <p className="text-sm">
                {siapDitanya
                  ? "Silakan tanya sesuatu tentang dokumen!"
                  : "Indeks dokumen dulu di panel kiri, lalu mulai bertanya."}
              </p>
            </div>
          </div>
        ) : (
          pesanList.map((m) => <ChatMessage key={m.id} message={m} />)
        )}
      </div>

      {/* Input di bawah */}
      <div className="border-t border-gray-200 p-4">
        <ChatInput onSend={handleSend} disabled={loading || !siapDitanya} />
        {!siapDitanya && (
          <p className="mt-2 text-xs text-amber-600">
            ⚠️ Indeks dokumen dulu sebelum bertanya.
          </p>
        )}
      </div>
    </div>
  );
}
