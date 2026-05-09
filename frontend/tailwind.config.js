/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        brand: {
          50: '#EEEDFE',
          100: '#CECBF6',
          500: '#7F77DD',
          600: '#534AB7',
          700: '#3C3489',
        },
      },
    },
  },
  plugins: [],
}