# 🎨 RAG Chat Frontend — Meeting 21: Deployment II dengan Next.js

Frontend chat modern (seperti ChatGPT) yang terhubung ke **FastAPI backend dari Meeting 20**. Dibangun dengan **Next.js 14**, **TypeScript**, dan **TailwindCSS**.

Inilah "wajah" dari sistem RAG kita — pengguna bisa mengetik pertanyaan dan melihat jawaban mengalir sedikit demi sedikit (streaming).

---

## 🎯 Apa yang Dipelajari di Sini?

| Konsep | File Terkait |
|--------|--------------|
| Next.js 14 App Router | `app/layout.tsx`, `app/page.tsx` |
| Server vs Client Components | `"use client"` di komponen interaktif |
| TypeScript (tipe data aman) | `lib/types.ts` |
| Route Handlers (API di Next.js) | `app/api/ask/route.ts`, `app/api/index/route.ts` |
| Streaming response (ReadableStream) | `app/api/ask/route.ts` + `lib/api.ts` |
| State management (useState) | `components/ChatWindow.tsx` |
| TailwindCSS styling | seluruh komponen |
| Menghubungkan frontend ke backend | route handlers → FastAPI M20 |

---

## 📁 Struktur Proyek

```
rag_chat_frontend/
├── app/
│   ├── layout.tsx            # Kerangka HTML global
│   ├── page.tsx              # Halaman utama (dokumen + chat)
│   ├── globals.css           # Style global + Tailwind
│   └── api/
│       ├── ask/route.ts      # Jembatan ke FastAPI /v1/ask (streaming)
│       └── index/route.ts    # Jembatan ke FastAPI /v1/index
├── components/
│   ├── ChatWindow.tsx        # Kelola percakapan & streaming
│   ├── ChatMessage.tsx       # Satu bubble pesan
│   ├── ChatInput.tsx         # Kotak input pertanyaan
│   └── DocumentPanel.tsx     # Panel indeks dokumen
├── lib/
│   ├── api.ts                # Fungsi panggil API
│   └── types.ts              # Definisi tipe TypeScript
├── package.json
├── tsconfig.json
├── tailwind.config.ts
└── .env.local.example
```

---

## 🔗 Cara Kerja: Frontend ↔ Backend

```
Browser  ──▶  Next.js Route Handler  ──▶  FastAPI (M20)  ──▶  RAG + DeepSeek
   ▲              (/api/ask)                (/v1/ask)
   └──────────── jawaban streaming ◀───────────┘
```

**Kenapa lewat Route Handler, bukan langsung ke FastAPI?**
1. **Keamanan** — API key backend tetap di server, tidak bocor ke browser
2. **Anti-CORS** — browser hanya bicara ke domain sendiri
3. **Fleksibel** — kita bisa mengubah/streaming respons di server

> 💡 Backend M20 mengembalikan jawaban sekaligus. Route Handler kita
> "memecahnya" jadi potongan kata dan mengalirkannya (streaming), agar
> terasa hidup seperti ChatGPT. Pola `ReadableStream`-nya persis sama
> dengan streaming LLM sungguhan.

---

## ⚙️ Cara Menjalankan

### Prasyarat
Backend **FastAPI dari Meeting 20 harus berjalan** dulu di `http://localhost:8000`.

### 1. Install dependency

```bash
npm install
```

### 2. Atur konfigurasi

```bash
cp .env.local.example .env.local
```

Isi `.env.local`:
```
BACKEND_URL=http://localhost:8000
BACKEND_API_KEY=kunci-rahasia-belajar
```

> `BACKEND_API_KEY` harus sama dengan `API_KEYS` di backend M20.

### 3. Jalankan

```bash
npm run dev
```

Buka **http://localhost:3000**.

### 4. Coba!
1. Di panel kiri, dokumen contoh sudah terisi → klik **Indeks Dokumen**
2. Di kanan, tanya: *"Berapa harga paket Premium?"*
3. Lihat jawaban mengalir + sumber dokumennya

---

## 🚀 Deploy ke Vercel

Next.js dibuat oleh Vercel, jadi deployment sangat mudah:

1. Push proyek ke GitHub
2. Buka [vercel.com](https://vercel.com), import repo
3. Set environment variable (`BACKEND_URL`, `BACKEND_API_KEY`)
4. Deploy — selesai! Dapat URL publik otomatis.

> ⚠️ Untuk production, `BACKEND_URL` harus menunjuk ke backend yang sudah
> di-deploy (bukan localhost). Ini dibahas di Meeting 22–24 (Docker, Nginx).

---

## 🧩 Server Components vs Client Components

Next.js App Router membedakan dua jenis komponen:

- **Server Component** (default) — dirender di server, tak bisa pakai `useState`/`onClick`. Cepat & hemat. Contoh: `layout.tsx`.
- **Client Component** (ditandai `"use client"`) — dirender di browser, bisa interaktif. Contoh: `ChatWindow.tsx`, `ChatInput.tsx`.

Aturan praktis: pakai Server Component sebisa mungkin, tambahkan `"use client"` hanya saat butuh interaktivitas.

---

## 🚀 Selanjutnya (Meeting 22)

Frontend + backend ini akan dibungkus dengan **Docker** agar bisa dijalankan di server mana pun secara konsisten, lalu Nginx (M23) dan CI/CD + monitoring (M24).
