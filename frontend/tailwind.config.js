/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: 'class',
  content: ['./public/**/*.html', './src/**/*.{vue,js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        oci: {
          dark: '#13335a',
          mid: '#2a688f',
          light: '#42b9eb',
          bg: '#eceded',
        },
      },
    },
  },
  plugins: [],
};
