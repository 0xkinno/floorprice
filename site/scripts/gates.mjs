// Quality gates: viewport screenshots, no horizontal scroll, no hero/text overlap, no console errors, axe AA clean.
import { createRequire } from "node:module";
import { spawn } from "node:child_process";
import fs from "node:fs";
const require = createRequire(import.meta.url);
const { chromium } = require("playwright");
const axeSrc = fs.readFileSync(new URL("../node_modules/axe-core/axe.min.js", import.meta.url), "utf8");
const VIEWPORTS = [["iphone", 390, 844], ["android", 412, 915], ["tablet", 768, 1024], ["desktop", 1440, 900]];
const PAGES = ["findings", "price", "techniques", "method", "paper"];
const server = spawn("npx", ["vite", "preview", "--port", "4173", "--strictPort"], { stdio: "ignore" });
await new Promise((r) => setTimeout(r, 2500));
fs.mkdirSync("screens", { recursive: true });
const browser = await chromium.launch();
let failures = 0;
const fail = (m) => { failures++; console.log("FAIL", m); };
for (const [name, w, h] of VIEWPORTS) {
  const ctx = await browser.newContext({ viewport: { width: w, height: h }, deviceScaleFactor: 1 });
  for (const pg of PAGES) {
    const page = await ctx.newPage();
    const errors = [];
    page.on("console", (m) => { if (m.type() === "error") errors.push(m.text()); });
    page.on("pageerror", (e) => errors.push(String(e)));
    await page.goto(`http://localhost:4173/#/${pg}`, { waitUntil: "networkidle" });
    await page.waitForTimeout(1800);
    // scroll through the page so scroll-triggered reveals run, then return to the top
    await page.evaluate(async () => { for (let y = 0; y < document.body.scrollHeight; y += 500) { window.scrollTo({ top: y, behavior: "instant" }); await new Promise((r) => setTimeout(r, 120)); } window.scrollTo({ top: 0, behavior: "instant" }); });
    await page.waitForTimeout(1600);
    const sw = await page.evaluate(() => document.documentElement.scrollWidth - window.innerWidth);
    if (sw > 0) fail(`${name}/${pg}: horizontal scroll ${sw}px`);
    if (pg === "findings") {
      const overlap = await page.evaluate(() => {
        const svg = document.querySelector("main svg[role=img]"); if (!svg) return "no hero svg";
        const a = svg.getBoundingClientRect();
        for (const el of document.querySelectorAll("main h1, main section:first-of-type p")) {
          const b = el.getBoundingClientRect();
          if (b.width && a.left < b.right - 1 && a.right > b.left + 1 && a.top < b.bottom - 1 && a.bottom > b.top + 1) return "overlap with " + el.tagName;
        }
        return null;
      });
      if (overlap) fail(`${name}/${pg}: hero ${overlap}`);
    }
    await page.addScriptTag({ content: axeSrc });
    const res = await page.evaluate(() => axe.run(document, { runOnly: { type: "tag", values: ["wcag2a", "wcag2aa", "wcag21aa", "wcag22aa"] } }));
    for (const v of res.violations) fail(`${name}/${pg}: axe ${v.id} (${v.impact}) ${v.nodes.length} nodes, e.g. ${v.nodes[0].html.slice(0, 120)}`);
    for (const e of errors) fail(`${name}/${pg}: console ${e.slice(0, 160)}`);
    if (pg === "findings" || pg === "price" || pg === "techniques") await page.screenshot({ path: `screens/${name}-${pg}.png`, fullPage: pg !== "findings" });
    await page.close();
  }
  await ctx.close();
}
await browser.close();
server.kill();
console.log(failures ? `${failures} gate failures` : "all gates passed");
process.exit(failures ? 1 : 0);
