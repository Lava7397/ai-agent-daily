import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{js,ts,jsx,tsx,mdx}", "./components/**/*.{js,ts,jsx,tsx,mdx}"],
  theme: {
    extend: {
      fontFamily: {
        display: [
          "ui-sans-serif",
          "system-ui",
          "-apple-system",
          "BlinkMacSystemFont",
          '"Helvetica Neue"',
          "Helvetica",
          "Arial",
          '"PingFang SC"',
          '"Hiragino Sans GB"',
          '"Microsoft YaHei"',
          "sans-serif",
        ],
        serif: [
          "ui-serif",
          "Georgia",
          '"Songti SC"',
          '"STSong"',
          '"Noto Serif SC"',
          "serif",
        ],
        sans: [
          "ui-sans-serif",
          "system-ui",
          '"PingFang SC"',
          '"Hiragino Sans GB"',
          '"Microsoft YaHei"',
          '"Noto Sans SC"',
          "sans-serif",
        ],
      },
      colors: {
        persimmon: {
          50: "#fff8f2",
          100: "#ffeedd",
          200: "#f5dcc4",
          300: "#e8bf98",
          400: "#c17f59",
          500: "#9a5838",
          600: "#7a3f29",
          700: "#5c2f20",
          800: "#3d2218",
          900: "#2a1710",
        },
        /** Warm neutral “ink” for type + dark bands (replaces cold #0a0a0a) */
        ink: "#1c120e",
        /** Cream page wash */
        fog: "#fff5eb",
        cream: {
          50: "#fffdfb",
          100: "#fff5eb",
          200: "#ffe8d4",
          300: "#ffd6b3",
        },
        cocoa: "#2d1810",
      },
    },
  },
  plugins: [],
};

export default config;
