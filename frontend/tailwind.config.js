/** @type {import('tailwindcss').Config} */
export default {
  darkMode: 'class',
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        canvas: '#FAF9F6',
        obsidian: '#141018',
        midnight: '#0D0B14',
        panel: '#151221',
        vice: {
          flamingo: '#FF2D95',
          tangerine: '#FF7A2F',
          lagoon: '#00B5AD',
          violet: '#8B3DFF',
          crimson: '#F43F5E',
        },
      },
      fontFamily: {
        sans: ['Inter', 'Plus Jakarta Sans', 'sans-serif'],
        display: ['Inter', 'Plus Jakarta Sans', 'sans-serif'],
      },
      boxShadow: {
        card: '0 8px 24px rgba(20, 16, 24, .04)',
      },
    },
  },
  plugins: [],
};
