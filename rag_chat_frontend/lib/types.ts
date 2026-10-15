/**
 * Definisi tipe data (TypeScript).
 *
 * TypeScript membantu kita menangkap kesalahan lebih awal: kalau kita salah
 * mengetik nama field atau tipe data, editor langsung memberi peringatan.
 */

// Satu pesan dalam percakapan chat
export interface ChatMessage {
  id: string;
  role: "user" | "assistant"; // siapa yang mengirim
  content: string;
  sources?: Source[]; // potongan dokumen sumber (opsional)
  isStreaming?: boolean; // true saat jawaban sedang mengalir
}

// Potongan dokumen yang jadi dasar jawaban (dari RAG)
export interface Source {
  isi: string;
  skor: number;
}

// Bentuk jawaban dari API backend (/v1/ask)
export interface AskResponse {
  pertanyaan: string;
  jawaban: string;
  sumber: Source[];
  dari_cache: boolean;
}

// Bentuk jawaban dari API backend (/v1/index)
export interface IndexResponse {
  status: string;
  jumlah_chunk: number;
  pesan: string;
}
