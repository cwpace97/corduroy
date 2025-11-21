/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'ski-blue': '#0ea5e9',
        'ski-dark': '#1e293b',
      }
    },
  },
  plugins: [],
}

