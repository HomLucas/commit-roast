/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      fontFamily: {
        retro: ['"Press Start 2P"', 'monospace'],
        pixel: ['VT323', 'monospace'],
        sans: ['Inter', 'sans-serif'],
      },
      animation: {
        flicker: 'flicker 3s infinite',
        glow: 'glow 2s ease-in-out infinite alternate',
        scanline: 'scanline 8s linear infinite',
        float: 'float 6s ease-in-out infinite',
      },
      keyframes: {
        flicker: {
          '0%, 100%': { opacity: '1' },
          '50%': { opacity: '0.8' },
        },
        glow: {
          from: { textShadow: '0 0 5px #f0f, 0 0 10px #f0f, 0 0 15px #f0f' },
          to: { textShadow: '0 0 10px #0ff, 0 0 20px #0ff, 0 0 30px #0ff' },
        },
        scanline: {
          '0%': { transform: 'translateY(-100%)' },
          '100%': { transform: 'translateY(100vh)' },
        },
        float: {
          '0%, 100%': { transform: 'translateY(0)' },
          '50%': { transform: 'translateY(-10px)' },
        },
      },
    },
  },
  plugins: [],
}
