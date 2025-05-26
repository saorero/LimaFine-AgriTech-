

/** @type {import('tailwindcss').Config} */
module.exports = {
  mode: 'jit', // Enable JIT mode for real time updates FEB
  content: [
    './templates/**/*.html',
    './static/src/**/*.js',
    './static/src/**/*.css',
    

  ],
  // Customization of tailwind is done in the theme key section
  theme: {
    extend: {
      animation: {  // predefined style for flickering
        flicker: 'flicker 1s infinite',
      },

      keyframes: {
        flicker: {
          '0%, 100%': { opacity: '1' }, // Fully visible at the start and end
          '50%': { opacity: '0.5' },   // Half visible in the middle
        },
      },

      backgroundImage: {
        'custom-bg': "url('/static/Images/background2.png')", // predefined custom background for this project
       
      },

      // Allows me to import a new fontStyle feb
      fontFamily: {
        italianno: ["Italianno", "cursive"],
      },

      
      
    },
  },

// Feb added scrollbar hiding plugin
  plugins: [require("tailwind-scrollbar-hide")],
};




