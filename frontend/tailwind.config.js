/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', 'ui-sans-serif', 'system-ui', 'sans-serif'],
        mono: ['"IBM Plex Mono"', 'ui-monospace', 'monospace'],
      },
      colors: {
        ink: '#20231f',
        paper: '#f5f4f0',
        kitchen: '#ed6a3a',
        sage: '#dce9d9',
      },
      boxShadow: {
        card: '0 12px 35px rgba(38, 40, 34, .07)',
      },
    },
  },
}
