import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        bg: "#0E1117",
        panel: "#1e2329",
        accent: "#07b9d1",
        border: "#34495e",
        muted: "#b0b0b0",
      },
    },
  },
  plugins: [],
};

export default config;
