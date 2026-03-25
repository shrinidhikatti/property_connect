/** @type {import('tailwindcss').Config} */
export default {
  content: [
    './index.html',
    './src/**/*.{js,ts,jsx,tsx}',
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          50:  '#e6f4f6',
          100: '#b3dfe5',
          500: '#028090',
          600: '#026d7a',
          700: '#015a65',
        },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
    },
  },
  plugins: [
    // Safe area padding for iOS PWA home-indicator
    function ({ addUtilities }) {
      addUtilities({
        '.safe-area-pb': {
          paddingBottom: 'env(safe-area-inset-bottom)',
        },
      })
    },
  ],
}
