const { loadEnvConfig } = require("@next/env");

// Pastikan .env / .env.local terbaca saat next.config dievaluasi
loadEnvConfig(process.cwd());

/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
};

module.exports = nextConfig;
