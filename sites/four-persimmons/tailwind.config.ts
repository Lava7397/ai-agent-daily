import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{js,ts,jsx,tsx,mdx}"],
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
        ink: "#0a0a0a",
        fog: "#f5f5f5",
      },
    },
  },
  plugins: [],
};

export default config;
