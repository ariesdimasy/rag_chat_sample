/**
 * Root Layout — kerangka HTML yang membungkus SEMUA halaman.
 *
 * Di Next.js App Router, file ini wajib ada. Di sinilah kita atur
 * <html>, <body>, metadata (judul tab, deskripsi), dan style global.
 */

import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "RAG Chat — Meeting 21",
  description: "Chat UI untuk sistem RAG, terhubung ke FastAPI backend.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="id">
      <body className="bg-gray-50 text-gray-900">{children}</body>
    </html>
  );
}
