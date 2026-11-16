// Records demo clips of the live site at 1920x1080 (webm, with a visible smooth cursor path). Output: video/clips/*.webm
import { createRequire } from "node:module";
import fs from "node:fs";
const require = createRequire(import.meta.url);
const { chromium } = require("playwright");
const BASE = process.env.SITE_URL || "https://floorprice-puce.vercel.app";
const OUT = new URL("../../video/clips/", import.meta.url).pathname;
fs.mkdirSync(OUT, { recursive: true });
const browser = await chromium.launch();
async function scene(name, fn) {
  const ctx = await browser.newContext({ viewport: { width: 1920, height: 1080 }, recordVideo: { dir: OUT + "_tmp", size: { width: 1920, height: 1080 } } });
  const page = await ctx.newPage();
  await fn(page);
  const v = page.video();
  await ctx.close();
  fs.renameSync(await v.path(), OUT + name + ".webm");
  console.log("recorded", name);
}
const wait = (p, ms) => p.waitForTimeout(ms);
await scene("01_hero", async (p) => { await p.goto(`${BASE}/#/findings`, { waitUntil: "networkidle" }); await wait(p, 9000); });
await scene("02_findings_scroll", async (p) => {
  await p.goto(`${BASE}/#/findings`, { waitUntil: "networkidle" }); await wait(p, 2500);
  for (let y = 0; y <= 2600; y += 20) { await p.mouse.wheel(0, 20); await wait(p, 16); }
  await wait(p, 2500);
});
await scene("03_explorer_budget", async (p) => {
  await p.goto(`${BASE}/#/price`, { waitUntil: "networkidle" }); await wait(p, 2500);
  const box = await p.locator("#budget").boundingBox();
  const at = (f) => box.x + box.width * f;
  await p.mouse.move(at(0.3), box.y + box.height / 2); await p.mouse.down();
  for (const f of [0.3, 0.38, 0.46, 0.55, 0.64, 0.74, 0.62, 0.5, 0.42]) { await p.mouse.move(at(f), box.y + box.height / 2, { steps: 30 }); await wait(p, 700); }
  await p.mouse.up(); await wait(p, 1500);
  await p.getByText("high", { exact: true }).click(); await wait(p, 1800);
  await p.getByText("low", { exact: true }).click(); await wait(p, 2200);
});
await scene("04_techniques", async (p) => {
  await p.goto(`${BASE}/#/techniques`, { waitUntil: "networkidle" }); await wait(p, 2000);
  for (let y = 0; y <= 1800; y += 12) { await p.mouse.wheel(0, 12); await wait(p, 16); }
  await wait(p, 2000);
});
await scene("05_method", async (p) => { await p.goto(`${BASE}/#/method`, { waitUntil: "networkidle" }); await wait(p, 7000); });
await browser.close();
fs.rmSync(OUT + "_tmp", { recursive: true, force: true });
