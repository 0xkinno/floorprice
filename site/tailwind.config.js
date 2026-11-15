export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        sky: { 50: "#F4F9FF", 100: "#E6F1FD", 200: "#D2E6FB", 300: "#B6D6F6", 400: "#8FBDEB", 500: "#5E9AD8" },
        ink: "#0B1B33", azure: "#0B4A99", deep: "#0F5B4F", lime: "#C8F25A", ember: "#D9542B", embertext: "#A63A16",
      },
      fontFamily: {
        display: ['"Newsreader Variable"', "Georgia", "serif"],
        ui: ['"Geist Variable"', "system-ui", "sans-serif"],
        mono: ['"JetBrains Mono"', "monospace"],
      },
    },
  },
};
