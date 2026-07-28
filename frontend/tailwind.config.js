/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,jsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#f0f7ff',
          100: '#e0effb',
          200: '#cde2fb',
          300: '#b7d3f6',
          400: '#9ec5f4',
          500: '#86b6ef',
          600: '#6da7ec',
          700: '#5598e7',
          800: '#3987e5',
          900: '#2a78d6',
        }
      }
    },
  },
  plugins: [],
}
