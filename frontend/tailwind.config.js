/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        bg: "#0f172a",
        surface: "#111827",
        "surface-hover": "#161f32",
        border: "#1f2937",
        "border-hover": "#2b3648",
        critical: "#ef4444",
        "critical-bg": "rgba(239, 68, 68, 0.1)",
        warning: "#f59e0b",
        "warning-bg": "rgba(245, 158, 11, 0.1)",
        healthy: "#22c55e",
        "healthy-bg": "rgba(34, 197, 94, 0.1)",
        primary: "#3b82f6",
        "primary-bg": "rgba(59, 130, 246, 0.1)",
        muted: "#94a3b8",
        "muted-soft": "#64748b",
        text: "#e2e8f0",
      },
      fontFamily: {
        sans: [
          "Inter",
          "-apple-system",
          "BlinkMacSystemFont",
          "Segoe UI",
          "Roboto",
          "Helvetica",
          "Arial",
          "sans-serif",
        ],
        mono: ["SF Mono", "ui-monospace", "Menlo", "monospace"],
      },
      boxShadow: {
        card: "0 1px 2px rgba(0, 0, 0, 0.3)",
        "card-hover": "0 8px 24px rgba(0, 0, 0, 0.35)",
      },
      keyframes: {
        "fade-in": {
          "0%": { opacity: "0", transform: "translateY(4px)" },
          "100%": { opacity: "1", transform: "translateY(0)" },
        },
      },
      animation: {
        "fade-in": "fade-in 0.2s ease-out",
      },
    },
  },
  plugins: [],
};
