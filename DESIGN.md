# DESIGN (site)

Concept: an editorial research magazine about the price of trust. Calm, exact, premium. Warm paper, not dark.
Colour tokens: Paper #F3F2EC (page), Ink #15171A (text), Lime #C8F25A (one accent per view: headline number, active slider, focus rings, never body text),
Moss #3E5B2A (links, honest series), Ember #D9542B (cheated outcomes only), Hairline #D9D6CC. Text contrast WCAG 2.2 AA.
Type: Fraunces (variable) or Newsreader Display for headlines and numerals; Instrument Sans or Geist for UI; JetBrains Mono for receipts. Self-hosted.
Ornament: hairline rules, tabular numerals, tracked small-caps labels (FLOOR PRICE, HONEST WAIT), figure numbers in the margin.
Navbar: floating squared capsule, radius 14px, backdrop blur, hairline border, links Findings, Price an attack, Techniques, Method, Paper, button "Read the paper". No wallet.
Hero: hand-built SVG of a price tag tied to a newspaper masthead showing the measured floor price from FACTS. Never overlaps text.
Motion: one swing of the tag as the number counts up; cards lift 2px; reveals 200 to 300 ms; honour prefers-reduced-motion.
Stack: Vite, React, TypeScript, Tailwind, Framer Motion, Recharts. Static build. Nothing calls a model from the browser.
Gates: Playwright screenshots at 390x844, 412x915, 768x1024, 1440x900; no horizontal scroll, no overlap, no console errors, axe AA clean.
