/**
 * Komponen: satu gelembung pesan (bubble).
 *
 * Pesan dari user tampil di kanan (indigo), pesan asisten di kiri (abu-abu).
 * Kalau asisten punya "sumber" (dari RAG), tampilkan di bawah jawaban.
 */

import type { ChatMessage as Message } from "@/lib/types";

export function ChatMessage({ message }: { message: Message }) {
  const isUser = message.role === "user";

  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"} mb-4`}>
      <div className={`max-w-[75%] ${isUser ? "order-2" : "order-1"}`}>
        {/* Label siapa yang bicara */}
        <div
          className={`text-xs font-medium mb-1 ${
            isUser ? "text-right text-indigo-400" : "text-left text-gray-400"
          }`}
        >
          {isUser ? "Kamu" : "🤖 Asisten AI"}
        </div>

        {/* Isi pesan */}
        <div
          className={`rounded-2xl px-4 py-3 text-sm leading-relaxed whitespace-pre-wrap ${
            isUser
              ? "bg-indigo-600 text-white rounded-br-sm"
              : "bg-gray-100 text-gray-800 rounded-bl-sm"
          }`}
        >
          {message.content}
          {/* Kursor berkedip saat jawaban sedang mengalir */}
          {message.isStreaming && (
            <span className="inline-block w-2 h-4 ml-0.5 bg-gray-500 animate-pulse align-middle" />
          )}
        </div>

        {/* Sumber dokumen (kalau ada) */}
        {message.sources && message.sources.length > 0 && (
          <details className="mt-2 text-xs">
            <summary className="cursor-pointer text-gray-500 hover:text-gray-700">
              📄 {message.sources.length} sumber dokumen
            </summary>
            <div className="mt-1 space-y-1">
              {message.sources.map((s, i) => (
                <div
                  key={i}
                  className="bg-gray-50 border border-gray-200 rounded-lg p-2 text-gray-600"
                >
                  <span className="text-indigo-500 font-medium">
                    (skor {s.skor.toFixed(3)})
                  </span>{" "}
                  {s.isi}
                </div>
              ))}
            </div>
          </details>
        )}
      </div>
    </div>
  );
}
