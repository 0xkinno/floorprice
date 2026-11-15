export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: { paper: "#F3F2EC", ink: "#15171A", lime: "#C8F25A", moss: "#3E5B2A", ember: "#D9542B", embertext: "#A63A16", hair: "#D9D6CC" },
      fontFamily: { display: ['"Fraunces Variable"', "Georgia", "serif"], ui: ['"Instrument Sans"', "system-ui", "sans-serif"], mono: ['"JetBrains Mono"', "monospace"] }
    }
  }
};
