/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './app/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        msingi: {
          green: '#1a5c2e',
          light: '#f0f7f3',
        },
      },
    },
  },
  plugins: [],
}