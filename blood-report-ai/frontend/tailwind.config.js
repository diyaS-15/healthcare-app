/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#f7fbff',
          100: '#eef5ff',
          200: '#d4e4f7',
          300: '#a8c8ec',
          400: '#6fa3df',
          500: '#4a7cc8',
          600: '#3058a8',
          700: '#123b6b',
          800: '#0a2847',
          900: '#051a2d',
        },
        secondary: {
          50: '#f5f3ff',
          100: '#ede9fe',
          200: '#ddd6fe',
          300: '#c4b5fd',
          400: '#a78bfa',
          500: '#8b5cf6',
          600: '#7c3aed',
          700: '#6d28d9',
          800: '#5b21b6',
          900: '#3f0f66',
        },
      },
      animation: {
        'spin': 'spin 1s linear infinite',
      },
      fontFamily: {
        sans: ['system-ui', 'sans-serif'],
      },
    },
  },
  plugins: [],
}
