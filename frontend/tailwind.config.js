/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
    "./src/**/*.css",
  ],
  theme: {
    extend: {
      colors: {
        navy: {
          950: '#050d18',
          900: '#0a1929',
          800: '#0d2137',
          700: '#1e3a5f',
          600: '#2d4a6f',
          500: '#3d5a80',
          400: '#5c7a9e',
        },
        accent: {
          900: '#3b0764',
          800: '#6b21a8',
          700: '#7e22ce',
          600: '#9333ea',
          500: '#a855f7',
          400: '#c084fc',
          300: '#d8b4fe',
        },
        bear: { bg: 'rgba(139,0,0,0.2)', border: '#a52a2a', text: '#e85555' },
        bull: { bg: 'rgba(21,128,61,0.2)', border: '#15803d', text: '#86efac' },
      },
    },
  },
  plugins: [],
}
