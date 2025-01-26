/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{html,js}", // Adjust paths as needed
    "./index.html",
  ],
  theme: {
    extend: {},
  },
  plugins: [require("daisyui")],
};