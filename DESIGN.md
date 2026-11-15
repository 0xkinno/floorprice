# DESIGN (site)

Direction (updated on the owner's brief after the first build): an editorial research magazine about the price of trust, set on a light-blue sky,
with glass cards, a tight editorial serif and confident motion. It keeps the original Floorprice idea: a price tag tied to a newspaper masthead.

Colour tokens
- Sky 50 #F4F9FF, 100 #E6F1FD, 200 #D2E6FB, 300 #B6D6F6, 400 #8FBDEB, 500 #5E9AD8: page atmosphere (gradient, aurora, dot grid, fine grain).
- Ink #0B1B33: text and primary buttons. Muted #3A4A66: secondary text.
- Azure #0B4A99: links and the "crossed" bars. Deep teal #0F5B4F: honest series and "holds".
- Lime #C8F25A: the accent (active nav pill, tag fill, focus ring halo, headline highlights). Never used for text on light surfaces.
- Ember #D9542B for fills that mean "cheated or affordable"; text in Ember uses #A63A16 for AA contrast.
All text meets WCAG 2.2 AA, enforced by axe in `site/scripts/gates.mjs`.

Type: Newsreader (variable, optical size) for headlines and big numerals; Geist (variable) for UI; JetBrains Mono for receipts and digests. All self-hosted through Fontsource.
Surfaces: frosted glass (white gradient, 1px white edge, soft blue shadow). Chips for real or simulated. Tracked small-caps labels, numbered eyebrows.
Hero: hand-built SVG of the price tag on a string under "The Daily Ledger", with a receipt and a ledger floating behind (pointer parallax on desktop).
Motion (Framer Motion, honours prefers-reduced-motion through MotionConfig): the tag swings once and idles with a faint sway; staggered scroll reveals;
count-up numerals when they enter view; a gliding nav pill (shared layout); scroll progress bar; animated ladder bars and a spring budget needle;
page cross-fades; a slow aurora behind everything.
Floor ladder: a log-dollar bar view of the cheapest priced attack per technique, with a draggable budget that turns affordable bars orange.
Stack: Vite, React, TypeScript, Tailwind, Framer Motion. Static build. Nothing calls a model from the browser.
Gates: Playwright at 390x844, 412x915, 768x1024 and 1440x900, with the page scrolled through first: no horizontal scroll, no overlap between the hero art and its text,
no console errors, axe AA clean.
