/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx,ts,tsx}'],
  theme: {
    extend: {
      colors: {
        // KrishiMind brand palette
        leaf: {
          50:  '#f0fdf4',
          100: '#dcfce7',
          200: '#bbf7d0',
          300: '#86efac',
          400: '#4ade80',
          500: '#22c55e',
          600: '#16a34a',
          700: '#15803d',
          800: '#166534',
          900: '#14532d',
          950: '#052e16',
        },
        earth: {
          50:  '#fdf8f0',
          100: '#faefd8',
          200: '#f4dba8',
          300: '#ecc068',
          400: '#e5a230',
          500: '#da8614',
          600: '#c0680d',
          700: '#9f4d0e',
          800: '#7f3d13',
          900: '#683313',
          950: '#3d1b07',
        },
        soil: {
          50:  '#fdf5ef',
          100: '#fae8d7',
          200: '#f3ceae',
          300: '#eaab7b',
          400: '#e08046',
          500: '#d96224',
          600: '#ca4d1a',
          700: '#a83b17',
          800: '#883119',
          900: '#6e2b17',
          950: '#3b130a',
        },
        sky: {
          50:  '#eff8ff',
          100: '#dbeffe',
          200: '#bfe3fd',
          300: '#93cffc',
          400: '#60b2f9',
          500: '#3b92f6',
          600: '#2574eb',
          700: '#1d5dd8',
          800: '#1e4caf',
          900: '#1e428a',
          950: '#172955',
        },
      },
      fontFamily: {
        display: ['"Playfair Display"', 'Georgia', 'serif'],
        body: ['"DM Sans"', '"Helvetica Neue"', 'sans-serif'],
        mono: ['"JetBrains Mono"', '"Fira Code"', 'monospace'],
      },
      backgroundImage: {
        'farm-pattern': "url(\"data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%2316a34a' fill-opacity='0.05'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E\")",
      },
      animation: {
        'grow-up': 'growUp 0.6s ease-out',
        'fade-slide': 'fadeSlide 0.5s ease-out',
        'pulse-leaf': 'pulseLeaf 2s ease-in-out infinite',
      },
      keyframes: {
        growUp: {
          '0%': { transform: 'scaleY(0)', transformOrigin: 'bottom' },
          '100%': { transform: 'scaleY(1)', transformOrigin: 'bottom' },
        },
        fadeSlide: {
          '0%': { opacity: '0', transform: 'translateY(12px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        pulseLeaf: {
          '0%, 100%': { transform: 'scale(1)' },
          '50%': { transform: 'scale(1.05)' },
        },
      },
      boxShadow: {
        'farm': '0 4px 24px rgba(22, 163, 74, 0.15)',
        'card': '0 2px 16px rgba(0, 0, 0, 0.08)',
        'deep': '0 8px 40px rgba(0, 0, 0, 0.12)',
      },
    },
  },
  plugins: [],
}
