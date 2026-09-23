// frontend/tailwind.config.cjs
// Tema "racing" personalizzabile: colori accento, dark mode via classe, font display per titoli.

/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: 'class', // il toggle tema aggiunge/rimuove la classe "dark" su <html>
  content: ['./src/**/*.{html,js,svelte,ts}'],
  theme: {
    extend: {
      colors: {
        racing: {
          red: '#E10600',
          black: '#111111',
          asphalt: '#1F2229',
          silver: '#C9CDD3',
          gold: '#F5A623',
          checker: '#F5F5F5'
        }
      },
      fontFamily: {
        display: ['"Rajdhani"', '"Segoe UI"', 'sans-serif'],
        body: ['"Inter"', '"Segoe UI"', 'sans-serif']
      },
      backgroundImage: {
        'racing-gradient': 'linear-gradient(135deg, #111111 0%, #E10600 100%)'
      }
    }
  },
  plugins: []
};
