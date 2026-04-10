/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        background: "#0f0f0f",
        surface: "#1a1a1a",
        border: "#2f2f2f",
        text: {
          primary: "#e5e5e5",
          secondary: "#a1a1a1",
        },
        accent: {
          DEFAULT: "#10a37f",
          hover: "#1a7f64",
        }
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
    },
  },
  plugins: [],
}
