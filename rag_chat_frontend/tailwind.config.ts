import type { Config } from "tailwindcss";

const config: Config = {
  // Beri tahu Tailwind di file mana saja class-nya dipakai
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        // Warna kustom untuk tema chat kita
        brand: {
          DEFAULT: "#4f46e5", // indigo
          dark: "#3730a3",
        },
      },
    },
  },
  plugins: [],
};

export default config;
