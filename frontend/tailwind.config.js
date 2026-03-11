import preset from 'frappe-ui/tailwind'

export default {
  presets: [preset],
  content: [
    './index.html',
    './src/**/*.{vue,js,ts,jsx,tsx}',
    './node_modules/frappe-ui/src/components/**/*.{vue,js,ts,jsx,tsx}',
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', 'InterVar', 'system-ui', 'sans-serif'],
      },
    },
  },
  plugins: [],
}
